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
      .from('user_excluded_vocab')
      .select('*')
      .eq('user_id', userId);

    if (error) {
      // If table does not exist or network error, silently fall back to local Dexie
      return;
    }

    const localRecords = await db.excluded_dictionary.toArray();
    const localMap = new Map(localRecords.map(r => [r.base_form.toLowerCase(), r]));

    // 2. Reconcile
    await db.transaction('rw', db.excluded_dictionary, async () => {
      // Add missing remote records locally
      for (const remote of remoteData || []) {
        if (!localMap.has(remote.base_form.toLowerCase())) {
          await db.excluded_dictionary.add({
            base_form: remote.base_form.toLowerCase(),
            article_id: remote.article_id,
            course_id: remote.course_id,
            user_id: userId,
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
        article_id: r.article_id || '',
        course_id: r.course_id || 'sfid',
        updated_at: r.updated_at || new Date().toISOString()
      }));

      const { error: pushError } = await supabase
        .from('user_excluded_vocab')
        .upsert(payload, { onConflict: 'user_id, base_form' });

      if (!pushError) {
        for (const r of unsynced) {
          if (r.id) await db.excluded_dictionary.update(r.id, { synced: true });
        }
      }
    }
  } catch (e) {
    console.warn('Sync excluded dictionary error:', e);
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
