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
  // FSRS specific
  due?: Date;
  state?: number;
  stability?: number;
  difficulty?: number;
  reps?: number;
  lapses?: number;
}

export const resolveWordMetadata = async (word_id: string, fallbackData?: any): Promise<UnifiedQueueItem> => {
  const lq = await db.learning_queue.where('base_form').equalsIgnoreCase(word_id).first();
  const custom = await db.custom_dictionary.where('base_form').equalsIgnoreCase(word_id).first();
  
  const baseForm = lq?.base_form || custom?.base_form || fallbackData?.base_form || word_id;
  const wordInSentence = lq?.word_in_sentence || custom?.word_in_sentence || fallbackData?.word_in_sentence || '';
  const sentenceText = lq?.sentence || lq?.context_sv || custom?.sentence || custom?.context_sv || fallbackData?.sentence || '';
  
  // Cleanup sentence if it just repeats the word
  const finalSentence = (sentenceText && sentenceText !== baseForm && sentenceText !== wordInSentence) ? sentenceText : (lq?.context_sv || custom?.context_sv || fallbackData?.context_sv || '');

  return {
    ...fallbackData, // Inherit any existing fsrs metadata
    word_id,
    base_form: baseForm,
    word_in_sentence: wordInSentence,
    en_translation: lq?.en_translation || custom?.en_translation || fallbackData?.en_translation || '',
    contextual_en: lq?.contextual_en || custom?.contextual_en || fallbackData?.contextual_en || '',
    dict_en: lq?.dict_en || custom?.dict_en || fallbackData?.dict_en || '',
    en: lq?.en || custom?.en || fallbackData?.en || '',
    sentence: finalSentence,
    context_sv: lq?.context_sv || custom?.context_sv || fallbackData?.context_sv || '',
    context_en: lq?.context_en || custom?.context_en || fallbackData?.context_en || '',
    article_id: lq?.article_id || custom?.article_id || fallbackData?.article_id || ''
  };
};

export const buildStudyQueue = async (
  appMode: 'study' | 'review',
  courseId: string,
  selectedArticleId: string | null,
  moduleType: 'dictation' | 'flashcard',
  learningQueueProp?: any[]
): Promise<{ queue: UnifiedQueueItem[], total: number, mastered: number, remaining: number }> => {
  
  let rawWords: { word_id: string, fallbackData?: any }[] = [];
  let totalCount = 0;
  let masteredCount = 0;

  if (appMode === 'review') {
    const now = new Date();
    const exRecords = await db.excluded_dictionary.toArray();
    const excludedVocab = exRecords.map((r: any) => r.base_form.toLowerCase());
    
    const fsrsRecords = await db.fsrs_progress.filter((r: any) => {
      if (r.course_id && r.course_id !== courseId) return false;
      if (r.state === 0) return false;
      if (moduleType === 'dictation' && r.todayDictationPassed) return false;
      if (moduleType === 'flashcard' && r.todayFlashcardPassed) return false;
      if (excludedVocab.includes((r.word_id || '').toLowerCase())) return false;
      const dueDate = new Date(r.due);
      if (dueDate > now) return false;
      return true;
    }).toArray();
    
    rawWords = fsrsRecords.map((r: any) => ({ word_id: r.word_id, fallbackData: r }));
    totalCount = rawWords.length;
    masteredCount = 0; // In review, we don't track "mastered" within a session the same way initially
  } else {
    if (!selectedArticleId) {
      return { queue: [], total: 0, mastered: 0, remaining: 0 };
    }
    
    let rawLq = await db.learning_queue.where('article_id').equals(selectedArticleId).toArray();
    if (rawLq.length === 0 && learningQueueProp) {
      rawLq = learningQueueProp.filter((w: any) => w.article_id === selectedArticleId);
    }
    
    const exRecords = await db.excluded_dictionary.toArray();
    const excludedVocab = exRecords.map((r: any) => r.base_form.toLowerCase());
    
    const masteryRecords = await db.study_mastery.where({ article_id: selectedArticleId, module: moduleType }).toArray();
    const masteredWords = masteryRecords.filter((r: any) => r.mastered).map((r: any) => r.word_id.toLowerCase());
    
    const uniqueMap = new Map();
    rawLq.forEach((w: any) => {
      const base = (w.base_form || '').toLowerCase();
      const inSent = (w.word_in_sentence || '').toLowerCase();
      const isEx = (base && excludedVocab.includes(base)) || (inSent && excludedVocab.includes(inSent));
      if (w.base_form && !isEx) {
        uniqueMap.set(w.base_form.toLowerCase(), w);
      }
    });
    const uniqueList = Array.from(uniqueMap.values());
    
    totalCount = uniqueList.length;
    
    const unmasteredList = uniqueList.filter((w: any) => !masteredWords.includes(w.base_form.toLowerCase()));
    masteredCount = totalCount - unmasteredList.length;
    
    rawWords = unmasteredList.map((w: any) => ({ word_id: w.base_form, fallbackData: w }));
  }
  
  const enrichedRecords = await Promise.all(rawWords.map((w: any) => resolveWordMetadata(w.word_id, w.fallbackData)));
  const shuffled = enrichedRecords.sort(() => 0.5 - Math.random());
  
  return {
    queue: shuffled,
    total: totalCount,
    mastered: masteredCount,
    remaining: shuffled.length
  };
};
