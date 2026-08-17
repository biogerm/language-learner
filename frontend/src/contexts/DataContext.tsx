import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';
import { fetchCourseData } from '../services/r2';
import { supabase } from '../services/supabase';
import { db } from '../db/dexie';
import { global_dict } from '../data/global_dict';

interface DataContextType {
  dictionary: Record<string, string>;
  courseData: Record<string, Record<string, any>> | null;
  loadCourse: (courseId: string) => Promise<void>;
  selectedStage: string;
  setSelectedStage: (stage: string) => void;
  selectedArticleId: string;
  setSelectedArticleId: (article: string) => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export function DataProvider({ children }: { children: ReactNode }) {
  const [courseData, setCourseData] = useState<Record<string, Record<string, any>> | null>(null);
  const [currentCourse, setCurrentCourse] = useState<string | null>(null);
  const [selectedStage, setSelectedStage] = useState(localStorage.getItem('selectedStage') || '');
  const [selectedArticleId, setSelectedArticleId] = useState(localStorage.getItem('selectedArticleId') || '');

  useEffect(() => {
    localStorage.setItem('selectedStage', selectedStage);
    localStorage.setItem('selectedArticleId', selectedArticleId);
  }, [selectedStage, selectedArticleId]);

  const loadCourse = useCallback(async (courseId: string) => {
    if (currentCourse === courseId && courseData) return;
    try {
      let data = null;
      // Check cache first
      const cached = await db.course_data.get(courseId);
      // Since legacy data is a nested object, we check if it has keys
      if (cached && cached.articles && Object.keys(cached.articles).length > 0) {
        data = cached.articles;
      } else {
        // Fetch r2_json_url from Supabase
        const { data: courseRow, error } = await supabase
          .from('courses')
          .select('r2_json_url')
          .eq('id', courseId)
          .single();

        if (error || !courseRow?.r2_json_url) {
          throw new Error(`Course not found or missing r2_json_url for ${courseId}`);
        }

        // Fetch the JSON from R2
        data = await fetchCourseData(courseRow.r2_json_url);
        
        // Save to Dexie cache (we store the whole tree in 'articles' since the schema has dictionary/articles)
        const cacheData = {
          courseId,
          dictionary: {},
          articles: data,
        };
        await db.course_data.put(cacheData);
      }
      
      setCourseData(data);
      setCurrentCourse(courseId);
    } catch (err) {
      console.error('Error loading course data:', err);
      // Try fallback to cache even if it failed
      const cached = await db.course_data.get(courseId);
      if (cached && cached.articles) {
        setCourseData(cached.articles);
        setCurrentCourse(courseId);
      } else {
        throw err;
      }
    }
  }, [currentCourse, courseData]);

  return (
    <DataContext.Provider value={{ 
      dictionary: global_dict as Record<string, string>, 
      courseData, 
      loadCourse,
      selectedStage, setSelectedStage,
      selectedArticleId, setSelectedArticleId
    }}>
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const context = useContext(DataContext);
  if (!context) throw new Error('useData must be used within a DataProvider');
  return context;
}


