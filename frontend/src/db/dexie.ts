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
  sync_error?: string;
  
  todayDictationPassed?: boolean;
  todayFlashcardPassed?: boolean;
  max_wrongs?: number;
  max_time?: number;
  gave_up?: boolean;
  reveal_count?: number;
  lastGatePassDate?: string;
}

export class AppDatabase extends Dexie {
  courses!: Table<Course, string>;
  course_data!: Table<CourseData, string>;
  fsrs_progress!: Table<FsrsProgress, string>;

  constructor() {
    super('AppDatabase');
    
    this.version(3).stores({
      courses: 'id, title', 
      course_data: 'courseId',
      fsrs_progress: 'word_id, state, due, synced, sync_error'
    });
  }
}

export const db = new AppDatabase();
