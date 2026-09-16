import { db, type WordObject, type CustomDictWord, type FsrsProgress } from '../db/dexie';
import { global_dict } from '../data/global_dict';
import { syncOfflineProgress } from '../utils/fsrs';

export interface ManualAddResult {
  word_id: string;
  found_in: 'course' | 'global' | 'custom';
  en_translation: string;
  has_example: boolean;
  fsrs_initialized: boolean;
}

export async function manualAddWord(word: string, courseId?: string, customEn?: string): Promise<ManualAddResult> {
  const w = word.trim().toLowerCase();
  // 1. 带例句词典（课程/文章/全局带例句）优先
  const courseData = await db.course_data.toArray();
  let wordObj: WordObject | null = null;
  for (const cd of courseData) {
    // 简化查找：搜索 dictionary 中匹配 base_form
    if ((cd.dictionary as any)?.[w]) wordObj = { base_form: w, en_translation: (cd.dictionary as any)[w], word_in_sentence: w, course_id: cd.courseId, stage_id: '', article_id: '', sentence_id: '', contextual_en: null };
  }

  // 2. 全局不带例句字典
  let en = (global_dict as any)[w];
  let source: 'course' | 'global' | 'custom' = 'global';
  let hasExample = false;
  if (wordObj) { en = wordObj.en_translation; source = 'course'; hasExample = true; }

  // 3. 未命中 → 写入 custom_dictionary
  if (!en && customEn) {
    await db.custom_dictionary.put({ base_form: w, en_translation: customEn, word_in_sentence: w, article_id: '', stage_id: '', course_id: courseId || '', sentence: '', sentence_en: '', synced: false } as CustomDictWord);
    en = customEn; source = 'custom';
  }

  // FSRS 初始化
  const now = new Date();
  const progress: FsrsProgress = {
    word_id: w,
    course_id: courseId || 'sfid',
    state: 0, due: now, stability: 0, difficulty: 0,
    elapsed_days: 0, scheduled_days: 0, reps: 0, lapses: 0,
    last_review: now, synced: false
  };
  await db.fsrs_progress.put(progress);
  await syncOfflineProgress();
  return { word_id: w, found_in: source, en_translation: en || customEn || '', has_example: hasExample, fsrs_initialized: true };
}
