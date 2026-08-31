import Dexie, { type Table } from 'dexie';

Dexie.debug = false;

export interface Course {
  id: string;
  title: string;
  content: string; 
}

export interface CourseData {
  courseId: string;
  dictionary: any;
  articles: Record<string, any>;
  updated_at?: string;
}

export interface FsrsProgress {
  word_id: string;
  course_id?: string;
  state: number; 
  due: Date;
  stability: number;
  difficulty: number;
  elapsed_days: number;
  scheduled_days: number;
  reps: number;
  lapses: number;
  last_review: Date;
  synced?: boolean;
  updated_at?: string;
  sync_error?: string;
  
  todayDictationPassed?: boolean;
  todayFlashcardPassed?: boolean;
  max_wrongs?: number;
  max_time?: number;
  gave_up?: boolean;
  reveal_count?: number;
  lastGatePassDate?: string;
}

export interface WordObject {
  id?: string;
  user_id?: string;
  course_id?: string;
  base_form: string;
  word_in_sentence: string;
  en_translation: string;
  contextual_en: string | null;
  dict_en?: string;
  en?: string;
  stage_id: string;
  article_id: string;
  sentence_id: string;
  sentence?: string;
  sentence_en?: string;
  context_sv?: string;
  context_en?: string;
  is_global_target?: boolean;
}

export interface CustomDictWord extends WordObject {
  synced?: boolean;
  updated_at?: string;
  is_global_target?: boolean;
}

export interface LearningQueueWord extends WordObject {
  course_id?: string;
  dictation_passed?: boolean;
  flashcard_passed?: boolean;
  status?: 'active' | 'graduated' | 'removed';
  synced?: boolean;
  updated_at?: string;
}

export interface LocalSetting {
  key: string;
  value: any;
  updated_at?: string;
}

export interface ExcludedDictWord {
  id?: number;
  user_id?: string;
  base_form: string;
  article_id?: string;
  course_id?: string;
  synced?: boolean;
  updated_at?: string;
}

export class AppDatabase extends Dexie {
  courses!: Table<Course, string>;
  course_data!: Table<CourseData, string>;
  fsrs_progress!: Table<FsrsProgress, string>;
  learning_queue!: Table<LearningQueueWord, string>; 
  custom_dictionary!: Table<CustomDictWord, string>; 
  excluded_dictionary!: Table<ExcludedDictWord, number>;
  local_settings!: Table<LocalSetting, string>;

  constructor() {
    super('AppDatabase');
    
    this.version(10).stores({
      courses: 'id, title', 
      course_data: 'courseId',
      fsrs_progress: 'word_id, state, due, synced, sync_error',
      learning_queue: '++id, article_id, base_form, [article_id+base_form], status, synced',
      custom_dictionary: '++id, base_form, article_id, synced',
      excluded_dictionary: '++id, base_form, article_id, course_id, synced',
      local_settings: 'key'
    });
  }
}

export const db = new AppDatabase();
