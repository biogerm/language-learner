import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';
import { fetchCourseData } from '../services/r2';
import { supabase } from '../services/supabase';
import { db, type WordObject } from '../db/dexie';

interface DataContextType {
  courseData: Record<string, Record<string, any>> | null;
  dictionary: Record<string, any> | null;
  loadCourse: (courseId: string) => Promise<void>;
  selectedStage: string;
  setSelectedStage: (stage: string) => void;
  selectedArticleId: string;
  setSelectedArticleId: (article: string) => void;
  
  learningQueue: WordObject[];
  customDictionary: WordObject[];
  refreshLearningQueue: () => Promise<void>;
  removeFromLearningQueue: (id: string) => Promise<void>;
  addToCustomDictionary: (word: WordObject) => Promise<void>;
  refreshCustomDictionary: () => Promise<void>;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export function DataProvider({ children }: { children: ReactNode }) {
  const [courseData, setCourseData] = useState<Record<string, Record<string, any>> | null>(null);
  const [dictionary, setDictionary] = useState<Record<string, any> | null>(null);
  const [currentCourse, setCurrentCourse] = useState<string | null>(null);
  const [selectedStage, setSelectedStage] = useState(localStorage.getItem('selectedStage') || '');
  const [selectedArticleId, setSelectedArticleId] = useState(localStorage.getItem('selectedArticleId') || '');

  const [learningQueue, setLearningQueue] = useState<WordObject[]>([]);
  const [customDictionary, setCustomDictionary] = useState<WordObject[]>([]);

  useEffect(() => {
    localStorage.setItem('selectedStage', selectedStage);
    localStorage.setItem('selectedArticleId', selectedArticleId);
  }, [selectedStage, selectedArticleId]);

  const loadCourse = useCallback(async (courseId: string) => {
    if (currentCourse === courseId && courseData) return;
    try {
      let data = null;
      let vocabData = null;
      
      const cached = await db.course_data.get(courseId);
      if (cached && cached.articles && Object.keys(cached.articles).length > 0) {
        data = cached.articles;
        vocabData = cached.dictionary || [];
      } else {
        const { data: courseRow, error } = await supabase
          .from('courses')
          .select('r2_json_url, r2_vocab_url')
          .eq('id', courseId)
          .single();

        if (error || !courseRow?.r2_json_url) {
          throw new Error(`Course not found or missing r2_json_url for ${courseId}`);
        }

        data = await fetchCourseData(courseRow.r2_json_url);
        
        try {
          if (courseRow.r2_vocab_url) {
            vocabData = await fetchCourseData(courseRow.r2_vocab_url);
          } else {
            // Fallback assumption
            vocabData = await fetchCourseData('courses/sfid/course_sfid_vocab.json');
          }
        } catch (err) {
          console.warn("Failed to fetch vocab data", err);
          vocabData = [];
        }
        
        const cacheData = {
          courseId,
          dictionary: vocabData,
          articles: data,
        };
        await db.course_data.put(cacheData);
      }
      
      setCourseData(data);
      setDictionary(vocabData);
      setCurrentCourse(courseId);
    } catch (err) {
      console.error('Error loading course data:', err);
      const cached = await db.course_data.get(courseId);
      if (cached && cached.articles) {
        setCourseData(cached.articles);
        setDictionary(cached.dictionary || null);
        setCurrentCourse(courseId);
      } else {
        throw err;
      }
    }
  }, [currentCourse, courseData]);

  const refreshLearningQueue = useCallback(async () => {
    if (!selectedArticleId) {
      setLearningQueue([]);
      return;
    }
    const arr = await db.learning_queue.where('article_id').equals(selectedArticleId).toArray();
    setLearningQueue(arr);
  }, [selectedArticleId]);

  useEffect(() => {
    let isCancelled = false;

    const syncLearningQueue = async () => {
      if (!currentCourse || !selectedArticleId) {
        if (!isCancelled) setLearningQueue([]);
        return;
      }
      const cached = await db.course_data.get(currentCourse);
      if (!cached || !cached.dictionary || isCancelled) return;
      
      const vocabList = (cached.dictionary || []) as WordObject[];
      let articleVocab = vocabList.filter(w => w.article_id === selectedArticleId);
      
      const customVocab = await db.custom_dictionary.where('article_id').equals(selectedArticleId).toArray();
      articleVocab = [...articleVocab, ...customVocab];
      
      // Deduplicate
      const uniqueMap = new Map();
      articleVocab.forEach(w => uniqueMap.set(w.base_form, w));
      articleVocab = Array.from(uniqueMap.values());
      
      await db.transaction('rw', [db.learning_queue, db.fsrs_progress, db.custom_dictionary], async () => {
        for (const w of articleVocab) {
          if (isCancelled) return;
          const progress = await db.fsrs_progress.where('word_id').equals(w.base_form).first(); 
          
          if (progress && progress.state > 0) {
            // It has entered FSRS spaced repetition (completed dual gate at least once). Exclude from new learning queue.
            continue;
          }

          const existing = await db.learning_queue
            .where({ article_id: w.article_id, base_form: w.base_form })
            .first();
            
          if (!existing) {
            await db.learning_queue.add({
              ...w,
              course_id: currentCourse,
              status: 'active',
              dictation_passed: false,
              flashcard_passed: false,
              synced: true, // do not push defaults
              updated_at: new Date(0).toISOString()
            });
          }
        }
      });
      
      if (!isCancelled) {
        const arr = await db.learning_queue.where('article_id').equals(selectedArticleId).filter(w => w.status !== 'removed' && w.status !== 'graduated').toArray();
        if (!isCancelled) {
          setLearningQueue(arr);
        }
      }
    };

    syncLearningQueue();

    return () => {
      isCancelled = true;
    };
  }, [currentCourse, selectedArticleId, dictionary, refreshLearningQueue]);

  const refreshCustomDictionary = useCallback(async () => {
    try {
      const local = await db.custom_dictionary.toArray();
      setCustomDictionary(local);
      
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      
      const { data, error } = await supabase
        .from('custom_dictionary')
        .select('*')
        .eq('user_id', user.id);
        
      if (!error && data) {
        const unsynced = local.filter(l => !l.synced);
        for (const item of unsynced) {
          const { synced: _synced, id: _id, ...toInsert } = item;
          const existingRemote = data.find(r => r.base_form === item.base_form);
          if (existingRemote) {
             const localUpdated = item.updated_at ? new Date(item.updated_at).getTime() : 0;
             const remoteUpdated = existingRemote.updated_at ? new Date(existingRemote.updated_at).getTime() : 0;
             if (localUpdated > remoteUpdated) {
                 await supabase.from('custom_dictionary').update(toInsert).eq('id', existingRemote.id);
             }
          } else {
             await supabase.from('custom_dictionary').insert({ ...toInsert, user_id: user.id });
          }
        }
        
        const { data: finalData } = await supabase
          .from('custom_dictionary')
          .select('*')
          .eq('user_id', user.id);
          
        if (finalData) {
          await db.transaction('rw', db.custom_dictionary, async () => {
            for (const item of finalData) {
              const parsedItem = { ...item, synced: true };
              const existing = await db.custom_dictionary.where('base_form').equals(item.base_form).first();
              
              if (existing && existing.id) {
                const localUpdated = existing.updated_at ? new Date(existing.updated_at).getTime() : 0;
                const remoteUpdated = item.updated_at ? new Date(item.updated_at).getTime() : 0;
                if (!existing.synced && localUpdated > remoteUpdated) {
                    continue;
                }
                await db.custom_dictionary.update(existing.id, parsedItem);
              } else {
                await db.custom_dictionary.add(parsedItem);
              }
            }
          });
          const newLocal = await db.custom_dictionary.toArray();
          setCustomDictionary(newLocal);
        }
      }
    } catch (err) {
      console.warn("Offline or sync failed, using local customDictionary data", err);
    }
  }, []);

  useEffect(() => {
    refreshCustomDictionary();
  }, [refreshCustomDictionary]);

  const syncLearningQueueRemote = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;
    
    // Pull first
    const { data: remoteData } = await supabase.from('learning_queue').select('*').eq('user_id', user.id);
    const remoteMap = new Map();
    if (remoteData) remoteData.forEach(r => remoteMap.set(r.course_id + '_' + r.article_id + '_' + r.base_form, r));
    
    // Push
    const unsynced = await db.learning_queue.filter(r => !r.synced).toArray();
    if (unsynced.length > 0) {
       const payloadToPush = [];
       for (const record of unsynced) {
           const localUpdated = record.updated_at ? new Date(record.updated_at).getTime() : 0;
           const key = (record.course_id || 'sfid') + '_' + record.article_id + '_' + record.base_form;
           const remote = remoteMap.get(key);
           const remoteUpdated = remote?.updated_at ? new Date(remote.updated_at).getTime() : 0;
           
           if (!remote || localUpdated > remoteUpdated) {
               payloadToPush.push({
                   user_id: user.id,
                   course_id: record.course_id || 'sfid',
                   article_id: record.article_id,
                   base_form: record.base_form,
                   dictation_passed: record.dictation_passed || false,
                   flashcard_passed: record.flashcard_passed || false,
                   status: record.status || 'active',
                   updated_at: record.updated_at || new Date().toISOString()
               });
           } else {
               if (record.id) await db.learning_queue.update(record.id, { synced: true });
           }
       }
       
       if (payloadToPush.length > 0) {
           const { error } = await supabase.from('learning_queue').upsert(payloadToPush, { onConflict: 'user_id, course_id, article_id, base_form' });
           if (!error) {
               await Promise.all(payloadToPush.map(async p => {
                   const local = await db.learning_queue.where({ article_id: p.article_id, base_form: p.base_form }).first();
                   if (local && local.id) await db.learning_queue.update(local.id!, { synced: true });
               }));
           }
       }
    }
    
    // Merge
    if (remoteData) {
        await db.transaction('rw', db.learning_queue, async () => {
           for (const remote of remoteData) {
               const local = await db.learning_queue.where({ article_id: remote.article_id, base_form: remote.base_form }).first();
               const remoteUpdated = remote.updated_at ? new Date(remote.updated_at).getTime() : 0;
               
               if (local) {
                   const localUpdated = local.updated_at ? new Date(local.updated_at).getTime() : 0;
                   if (!local.synced && localUpdated > remoteUpdated) continue;
                   
                   await db.learning_queue.update(local.id!, {
                       dictation_passed: remote.dictation_passed,
                       flashcard_passed: remote.flashcard_passed,
                       status: remote.status,
                       updated_at: remote.updated_at,
                       synced: true
                   });
               } else {
                   // If we don't have it locally, wait, we might not have downloaded the course JSON.
                   // So we shouldn't insert a bare record unless we have WordObject data.
                   // Actually, if it's missing, it's fine, next time syncLearningQueue runs it will pull defaults and then we'll merge.
               }
           }
        });
        // We need to refresh the queue if something changed. But this is a background sync.
    }
  };

  useEffect(() => {
    const handleOnline = () => {
        syncLearningQueueRemote().catch(console.error);
    };
    window.addEventListener('online', handleOnline);
    // Initial load sync
    syncLearningQueueRemote().catch(console.error);
    return () => window.removeEventListener('online', handleOnline);
  }, []);

  const removeFromLearningQueue = useCallback(async (id: string) => {
    let target = await db.learning_queue.where('id').equals(id).first();
    if (!target) target = await db.learning_queue.where('base_form').equals(id).first();
    if (target && target.id) {
      await db.learning_queue.update(target.id, { status: 'removed', synced: false, updated_at: new Date().toISOString() });
      syncLearningQueueRemote().catch(console.error);
    }
    await refreshLearningQueue();
  }, [refreshLearningQueue]);

  const addToCustomDictionary = useCallback(async (word: WordObject) => {
    const tempWord = { ...word, synced: false, updated_at: new Date().toISOString() };
    const newId = await db.custom_dictionary.add(tempWord);
    const localWord = { ...tempWord, id: newId.toString() };
    
    setCustomDictionary(prev => [...prev, localWord]);

    // Background sync
    const syncWord = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return; // Unauthenticated, remains unsynced local

        const toInsert = { ...word, user_id: user.id };
        const { data, error } = await supabase
          .from('custom_dictionary')
          .insert(toInsert)
          .select()
          .single();
          
        if (!error && data) {
          await db.custom_dictionary.update(newId, { ...data, synced: true });
          setCustomDictionary(prev => prev.map(p => p.id === localWord.id ? { ...data, synced: true } : p));
        }
      } catch (err) {
        console.error("Failed to sync customDictionary item, will retry later", err);
      }
    };
    
    syncWord();
  }, []);

  return (
    <DataContext.Provider value={{ 
      courseData, 
      dictionary,
      loadCourse,
      selectedStage, setSelectedStage,
      selectedArticleId, setSelectedArticleId,
      learningQueue,
      customDictionary,
      refreshLearningQueue,
      removeFromLearningQueue,
      addToCustomDictionary,
      refreshCustomDictionary
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
