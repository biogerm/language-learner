import Dexie, { type Table } from 'dexie';

export interface Course {
  id: string;
  title: string;
  content: string; 
}

export interface CourseData {
  courseId: string;
  dictionary: any;
  articles: Record<string, any>;
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
  base_form: string;
  word_in_sentence: string;
  en_translation: string;
  contextual_en: string | null;
  stage_id: string;
  article_id: string;
  sentence_id: string;
}

export interface CustomDictWord extends WordObject {
  synced?: boolean;
  updated_at?: string;
}

export interface LearningQueueWord extends WordObject {
  course_id?: string;
  dictation_passed?: boolean;
  flashcard_passed?: boolean;
  status?: 'active' | 'graduated' | 'removed';
  synced?: boolean;
  updated_at?: string;
}

export class AppDatabase extends Dexie {
  courses!: Table<Course, string>;
  course_data!: Table<CourseData, string>;
  fsrs_progress!: Table<FsrsProgress, string>;
  learning_queue!: Table<LearningQueueWord, string>; 
  custom_dictionary!: Table<CustomDictWord, string>; 

  constructor() {
    super('AppDatabase');
    
    this.version(7).stores({
      courses: 'id, title', 
      course_data: 'courseId',
      fsrs_progress: 'word_id, state, due, synced, sync_error',
      learning_queue: '++id, article_id, base_form, [article_id+base_form], status, synced',
      custom_dictionary: '++id, base_form, synced'
    });
  }
}

export const db = new AppDatabase();
