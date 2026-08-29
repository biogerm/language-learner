import { db } from '../db/dexie';

export interface UnifiedQueueItem {
  word_id: string;
  base_form: string;
  word_in_sentence: string;
  en_translation: string;
  contextual_en: string;
  dict_en: string;
  en: string;
  sentence: string;
  context_sv: string;
  context_en: string;
  article_id: string;
  course_id?: string;
  // FSRS specific
  due?: Date;
  state?: number;
  stability?: number;
  difficulty?: number;
  reps?: number;
  lapses?: number;
}

export interface StudyQueueStats {
  queue: UnifiedQueueItem[];
  total: number;
  mastered: number;
  remaining: number;
  inFsrsCount?: number;
}

// Memory cache for sentence mappings: courseId -> Map<sentence_id, { sv: string, en: string }>
const courseSentenceCache = new Map<string, Map<string, { sv: string; en: string }>>();
const courseWordToSentenceCache = new Map<string, Map<string, { sv: string; en: string }>>();

export const getSentenceMapForCourse = async (courseId: string) => {
  if (courseSentenceCache.has(courseId)) {
    return {
      sentenceMap: courseSentenceCache.get(courseId)!,
      wordToSentenceMap: courseWordToSentenceCache.get(courseId)!
    };
  }

  const sentenceMap = new Map<string, { sv: string; en: string }>();
  const wordToSentenceMap = new Map<string, { sv: string; en: string }>();

  try {
    const cached = await db.course_data.get(courseId);
    if (cached && cached.articles && cached.articles.stages) {
      for (const s of cached.articles.stages) {
        for (const a of s.articles || []) {
          for (const sent of a.sentences || []) {
            if (sent.sentence_id) {
              sentenceMap.set(sent.sentence_id, { sv: sent.sv, en: sent.en || '' });
            }
            if (sent.target_words) {
              for (const tw of sent.target_words) {
                const base = (tw.base_form || '').toLowerCase();
                if (base && !wordToSentenceMap.has(base)) {
                  wordToSentenceMap.set(base, { sv: sent.sv, en: sent.en || '' });
                }
              }
            }
            if (sent.secondary_words) {
              for (const sw of sent.secondary_words) {
                const base = (sw.base_form || '').toLowerCase();
                if (base && !wordToSentenceMap.has(base)) {
                  wordToSentenceMap.set(base, { sv: sent.sv, en: sent.en || '' });
                }
              }
            }
          }
        }
      }
    }
  } catch (e) {
    console.warn('Error building sentence cache for course:', courseId, e);
  }

  courseSentenceCache.set(courseId, sentenceMap);
  courseWordToSentenceCache.set(courseId, wordToSentenceMap);

  return { sentenceMap, wordToSentenceMap };
};

export const resolveWordMetadata = async (
  word_id: string,
  fallbackData?: any,
  activeCourseId?: string
): Promise<UnifiedQueueItem> => {
  const cleanWordId = (word_id || '').trim().toLowerCase();

  // 1. Look up in custom_dictionary (prioritize matching article if provided)
  let custom = null;
  if (fallbackData?.article_id) {
    custom = await db.custom_dictionary
      .where({ article_id: fallbackData.article_id, base_form: cleanWordId })
      .first();
  }
  if (!custom) {
    custom = await db.custom_dictionary
      .where('base_form')
      .equalsIgnoreCase(cleanWordId)
      .first();
  }

  // 2. Look up in learning_queue (prioritize matching article if provided)
  let lq = null;
  if (fallbackData?.article_id) {
    lq = await db.learning_queue
      .where({ article_id: fallbackData.article_id, base_form: cleanWordId })
      .first();
  }
  if (!lq) {
    lq = await db.learning_queue
      .where('base_form')
      .equalsIgnoreCase(cleanWordId)
      .first();
  }

  // 3. Resolve base properties
  const baseForm = fallbackData?.base_form || custom?.base_form || lq?.base_form || word_id;
  const wordInSentence = fallbackData?.word_in_sentence || custom?.word_in_sentence || lq?.word_in_sentence || '';

  // Resolve course_id and sentence_id coordinates (prioritize fallbackData coordinates from current article queue)
  const targetCourseId = fallbackData?.course_id || custom?.course_id || lq?.course_id || activeCourseId || 'sfid';
  let targetSentenceId = fallbackData?.sentence_id || custom?.sentence_id || lq?.sentence_id || '';

  // If sentence_id is missing, search main dictionary
  if (!targetSentenceId) {
    try {
      const cached = await db.course_data.get(targetCourseId);
      if (cached && cached.dictionary && Array.isArray(cached.dictionary)) {
        const dictEntry = cached.dictionary.find(
          (d: any) => (d.base_form || '').toLowerCase() === cleanWordId
        );
        if (dictEntry && dictEntry.sentence_id) {
          targetSentenceId = dictEntry.sentence_id;
        }
      }
    } catch (e) {}
  }

  // 4. Resolve sentence text dynamically via sentenceMap
  let resolvedSentenceSv = '';
  let resolvedSentenceEn = '';

  const { sentenceMap, wordToSentenceMap } = await getSentenceMapForCourse(targetCourseId);

  if (targetSentenceId && sentenceMap.has(targetSentenceId)) {
    const match = sentenceMap.get(targetSentenceId)!;
    resolvedSentenceSv = match.sv;
    resolvedSentenceEn = match.en;
  } else if (fallbackData?.sentence && fallbackData.sentence !== baseForm && fallbackData.sentence !== wordInSentence) {
    resolvedSentenceSv = fallbackData.sentence;
    resolvedSentenceEn = fallbackData.sentence_en || fallbackData.context_en || '';
  } else if (custom?.sentence && custom.sentence !== baseForm && custom.sentence !== wordInSentence) {
    resolvedSentenceSv = custom.sentence;
    resolvedSentenceEn = custom.sentence_en || custom.context_en || '';
  } else if (wordToSentenceMap.has(cleanWordId)) {
    const match = wordToSentenceMap.get(cleanWordId)!;
    resolvedSentenceSv = match.sv;
    resolvedSentenceEn = match.en;
  }

  // Fallback to cached string if dynamic resolution yielded nothing
  const rawFallbackSv = fallbackData?.sentence || lq?.sentence || lq?.context_sv || custom?.sentence || custom?.context_sv || '';
  const finalSentence =
    resolvedSentenceSv ||
    (rawFallbackSv && rawFallbackSv !== baseForm && rawFallbackSv !== wordInSentence ? rawFallbackSv : '');
  const finalContextEn = resolvedSentenceEn || fallbackData?.context_en || fallbackData?.sentence_en || lq?.context_en || custom?.context_en || '';

  return {
    ...fallbackData,
    word_id,
    base_form: baseForm,
    word_in_sentence: wordInSentence,
    en_translation: custom?.en_translation || fallbackData?.en_translation || lq?.en_translation || '',
    contextual_en: custom?.contextual_en || fallbackData?.contextual_en || lq?.contextual_en || '',
    dict_en: custom?.dict_en || fallbackData?.dict_en || lq?.dict_en || '',
    en: custom?.en || fallbackData?.en || lq?.en || '',
    sentence: finalSentence,
    context_sv: finalSentence,
    context_en: finalContextEn,
    article_id: fallbackData?.article_id || custom?.article_id || lq?.article_id || '',
    course_id: targetCourseId
  };
};

export const buildStudyQueue = async (
  appMode: 'study' | 'review',
  courseId: string,
  selectedArticleId: string | null,
  moduleType: 'dictation' | 'flashcard',
  learningQueueProp?: any[]
): Promise<StudyQueueStats> => {
  let rawWords: { word_id: string; fallbackData?: any }[] = [];
  let totalCount = 0;
  let masteredCount = 0;
  let inFsrsCount = 0;

  if (appMode === 'review') {
    const now = new Date();
    const exRecords = await db.excluded_dictionary.toArray();
    const excludedVocab = exRecords.map((r: any) => (r.base_form || '').toLowerCase());

    const fsrsRecords = await db.fsrs_progress
      .filter((r: any) => {
        if (r.course_id && r.course_id !== courseId) return false;
        if (r.state === 0) return false;
        if (moduleType === 'dictation' && r.todayDictationPassed) return false;
        if (moduleType === 'flashcard' && r.todayFlashcardPassed) return false;
        if (excludedVocab.includes((r.word_id || '').toLowerCase())) return false;
        const dueDate = new Date(r.due);
        if (dueDate > now) return false;
        return true;
      })
      .toArray();

    rawWords = fsrsRecords.map((r: any) => ({ word_id: r.word_id, fallbackData: r }));
    totalCount = rawWords.length;
    masteredCount = 0;
  } else {
    if (!selectedArticleId) {
      return { queue: [], total: 0, mastered: 0, remaining: 0, inFsrsCount: 0 };
    }

    let rawLq = await db.learning_queue.where('article_id').equals(selectedArticleId).toArray();
    if (rawLq.length === 0 && learningQueueProp) {
      rawLq = learningQueueProp.filter((w: any) => w.article_id === selectedArticleId);
    }

    const exRecords = await db.excluded_dictionary.toArray();
    const excludedVocab = exRecords.map((r: any) => (r.base_form || '').toLowerCase());

    // Fetch active FSRS records for this course to filter out already learning/reviewing words
    const fsrsRecords = await db.fsrs_progress
      .filter((r: any) => {
        if (r.course_id && r.course_id !== courseId) return false;
        return r.state !== 0;
      })
      .toArray();
    const fsrsWordSet = new Set(fsrsRecords.map((r: any) => (r.word_id || '').toLowerCase()));

    const uniqueMap = new Map();
    rawLq.forEach((w: any) => {
      const base = (w.base_form || '').toLowerCase();
      const inSent = (w.word_in_sentence || '').toLowerCase();
      const isEx = (base && excludedVocab.includes(base)) || (inSent && excludedVocab.includes(inSent));
      if (w.base_form && !isEx) {
        if (fsrsWordSet.has(base) || (inSent && fsrsWordSet.has(inSent))) {
          inFsrsCount++;
        } else {
          uniqueMap.set(base, w);
        }
      }
    });
    const uniqueList = Array.from(uniqueMap.values());

    totalCount = uniqueList.length;

    const unmasteredList = uniqueList.filter((w: any) => {
      if (moduleType === 'dictation') return !w.dictation_passed;
      if (moduleType === 'flashcard') return !w.flashcard_passed;
      return true;
    });
    masteredCount = totalCount - unmasteredList.length;

    rawWords = unmasteredList.map((w: any) => ({ word_id: w.base_form, fallbackData: w }));
  }

  const enrichedRecords = await Promise.all(
    rawWords.map((w: any) => resolveWordMetadata(w.word_id, w.fallbackData, courseId))
  );
  const shuffled = enrichedRecords.sort(() => 0.5 - Math.random());

  return {
    queue: shuffled,
    total: totalCount,
    mastered: masteredCount,
    remaining: shuffled.length,
    inFsrsCount
  };
};

