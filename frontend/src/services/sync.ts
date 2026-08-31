import { db } from '../db/dexie';
import { supabase } from './supabase';

/**
 * Synchronize excluded words with Supabase cloud database
 */
export async function syncExcludedDictionary() {
  if (!navigator.onLine) return;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) return;
    const userId = session.user.id;

    // 1. Pull from Supabase
    const { data: remoteData, error } = await supabase
      .from('excluded_dictionary')
      .select('*')
      .eq('user_id', userId);

    if (error) {
      console.warn('Error fetching excluded_dictionary from Supabase:', error);
      return;
    }

    const localRecords = await db.excluded_dictionary.toArray();
    const localMap = new Map(localRecords.map(r => [`${(r.course_id || 'sfid').toLowerCase()}_${r.base_form.toLowerCase()}`, r]));

    // 2. Reconcile: add missing remote records locally
    await db.transaction('rw', db.excluded_dictionary, async () => {
      for (const remote of remoteData || []) {
        const key = `${(remote.course_id || 'sfid').toLowerCase()}_${remote.base_form.toLowerCase()}`;
        if (!localMap.has(key)) {
          await db.excluded_dictionary.add({
            base_form: remote.base_form.toLowerCase(),
            course_id: remote.course_id || 'sfid',
            article_id: remote.article_id || '',
            synced: true,
            updated_at: remote.updated_at || new Date().toISOString()
          });
        }
      }
    });

    // 3. Push unsynced local records
    const unsynced = await db.excluded_dictionary.filter(r => !r.synced).toArray();
    if (unsynced.length > 0) {
      const payload = unsynced.map(r => ({
        user_id: userId,
        base_form: r.base_form.toLowerCase(),
        course_id: r.course_id || 'sfid',
        updated_at: r.updated_at || new Date().toISOString()
      }));

      const { error: pushError } = await supabase
        .from('excluded_dictionary')
        .upsert(payload, { onConflict: 'user_id, course_id, base_form' });

      if (!pushError) {
        for (const r of unsynced) {
          if (r.id) await db.excluded_dictionary.update(r.id, { synced: true });
        }
      } else {
        console.warn('Error pushing excluded_dictionary to Supabase:', pushError);
      }
    }
  } catch (e) {
    console.warn('Sync excluded dictionary error:', e);
  }
}

/**
 * Delete excluded words from Supabase cloud database
 */
export async function deleteExcludedDictionaryWords(baseForms: string[], courseId = 'sfid') {
  if (!navigator.onLine || !baseForms || baseForms.length === 0) return;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) return;
    const userId = session.user.id;

    const cleanForms = Array.from(new Set(baseForms.map(w => w.toLowerCase()).filter(Boolean)));
    if (cleanForms.length === 0) return;

    const { error } = await supabase
      .from('excluded_dictionary')
      .delete()
      .eq('user_id', userId)
      .eq('course_id', courseId.toLowerCase())
      .in('base_form', cleanForms);

    if (error) {
      console.warn('Error deleting excluded_dictionary from Supabase:', error);
    }
  } catch (e) {
    console.warn('Delete excluded dictionary error:', e);
  }
}

/**
 * Delete custom dictionary words from Supabase cloud database
 */
export async function deleteCustomDictionaryWords(baseForms: string[]) {
  if (!navigator.onLine || !baseForms || baseForms.length === 0) return;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) return;
    const userId = session.user.id;

    const cleanForms = Array.from(new Set(baseForms.map(w => w.toLowerCase()).filter(Boolean)));
    if (cleanForms.length === 0) return;

    const { error } = await supabase
      .from('custom_dictionary')
      .delete()
      .eq('user_id', userId)
      .in('base_form', cleanForms);

    if (error) {
      console.warn('Error deleting custom_dictionary from Supabase:', error);
    }
  } catch (e) {
    console.warn('Delete custom dictionary error:', e);
  }
}

/**
 * Synchronize custom dictionary (annotated / extracted vocabulary) with Supabase cloud database
 */
export async function syncCustomDictionary() {
  if (!navigator.onLine) return;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) return;
    const userId = session.user.id;

    // 1. Pull from Supabase
    const { data: remoteData, error } = await supabase
      .from('custom_dictionary')
      .select('*')
      .eq('user_id', userId);

    if (error) {
      console.warn('Error fetching custom_dictionary from Supabase:', error);
      return;
    }

    const localRecords = await db.custom_dictionary.toArray();
    const localMap = new Map(localRecords.map(r => [(r.base_form || r.word_in_sentence || '').toLowerCase(), r]));

    // 2. Reconcile remote items into local Dexie
    await db.transaction('rw', [db.custom_dictionary, db.learning_queue], async () => {
      for (const remote of remoteData || []) {
        const key = (remote.base_form || remote.word_in_sentence || '').toLowerCase();
        const local = localMap.get(key);
        if (!local) {
          await db.custom_dictionary.add({
            ...remote,
            synced: true
          });
        } else if (local.id && local.synced) {
          await db.custom_dictionary.update(local.id, {
            ...remote,
            synced: true
          });
        }
      }
    });

    // 3. Push unsynced local records to Supabase
    const unsynced = await db.custom_dictionary.filter(r => !r.synced).toArray();
    if (unsynced.length > 0) {
      const payload = unsynced.map(r => ({
        user_id: userId,
        base_form: r.base_form || r.word_in_sentence,
        word_in_sentence: r.word_in_sentence || r.base_form,
        en_translation: r.en_translation || r.en || '',
        dict_en: r.dict_en || null,
        stage_id: r.stage_id || '',
        article_id: r.article_id || '',
        sentence_id: r.sentence_id || '',
        sentence: r.sentence || r.context_sv || '',
        sentence_en: r.sentence_en || r.context_en || '',
        context_sv: r.context_sv || r.sentence || '',
        context_en: r.context_en || r.sentence_en || '',
        course_id: r.course_id || 'sfid',
        is_global_target: !!r.is_global_target,
        updated_at: r.updated_at || new Date().toISOString()
      }));

      const { error: pushError } = await supabase
        .from('custom_dictionary')
        .upsert(payload, { onConflict: 'user_id, base_form' });

      if (!pushError) {
        for (const r of unsynced) {
          if (r.id) await db.custom_dictionary.update(r.id, { synced: true });
        }
      } else {
        console.warn('Error pushing custom_dictionary to Supabase:', pushError);
      }
    }
  } catch (e) {
    console.warn('Sync custom dictionary error:', e);
  }
}

/**
 * Clean up all legacy localStorage keys
 */
export function purgeLegacyLocalStorage() {
  const legacyKeys = [
    'excludedVocab',
    'customVocab',
    'appMode',
    'selectedStage',
    'selectedArticleId',
    'dictationMasteredWords',
    'flashcardMasteredWords',
    'vocabBook',
    'studyDictationPassed',
    'studyFlashcardPassed',
    'fsrsData'
  ];
  legacyKeys.forEach(k => {
    try {
      localStorage.removeItem(k);
    } catch {}
  });
}
