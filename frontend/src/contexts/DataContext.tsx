import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';
import { fetchCourseData } from '../services/r2';
import { supabase } from '../services/supabase';
import { db, type WordObject } from '../db/dexie';
import { syncExcludedDictionary } from '../services/sync';

interface DataContextType {
  courseData: Record<string, Record<string, any>> | null;
  dictionary: Record<string, any> | null;
  loadCourse: (courseId: string) => Promise<void>;
  selectedStage: string;
  setSelectedStage: (stage: string) => void;
  selectedArticleId: string;
  setSelectedArticleId: (article: string) => void;
  appMode: 'study' | 'review';
  setAppMode: (mode: 'study' | 'review') => void;
  
  learningQueue: WordObject[];
  customDictionary: WordObject[];
  excludedVocab: string[];
  refreshLearningQueue: () => Promise<void>;
  removeFromLearningQueue: (id: string) => Promise<void>;
  addToCustomDictionary: (word: WordObject) => Promise<void>;
  refreshCustomDictionary: () => Promise<void>;
  refreshExcludedDictionary: () => Promise<void>;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export function DataProvider({ children }: { children: ReactNode }) {
  const [courseData, setCourseData] = useState<Record<string, Record<string, any>> | null>(null);
  const [dictionary, setDictionary] = useState<Record<string, any> | null>(null);
  const [currentCourse, setCurrentCourse] = useState<string | null>(null);
  const [selectedStage, setSelectedStageState] = useState('');
  const [selectedArticleId, setSelectedArticleIdState] = useState('');
  const [appMode, setAppModeState] = useState<'study' | 'review'>('study');

  const [learningQueue, setLearningQueue] = useState<WordObject[]>([]);
  const [customDictionary, setCustomDictionary] = useState<WordObject[]>([]);
  const [excludedVocab, setExcludedVocab] = useState<string[]>([]);

  // Initialize client settings from Dexie local_settings (default appMode to 'study')
  useEffect(() => {
    (async () => {
      try {
        const stage = await db.local_settings.get('selectedStage');
        if (stage && typeof stage.value === 'string') {
          setSelectedStageState(stage.value);
        }
        const art = await db.local_settings.get('selectedArticleId');
        if (art && typeof art.value === 'string') {
          setSelectedArticleIdState(art.value);
        }
      } catch (e) {
        console.warn('Error loading local settings from Dexie:', e);
      }
    })();
  }, []);

  const setAppMode = useCallback((mode: 'study' | 'review') => {
    setAppModeState(mode);
    db.local_settings.put({ key: 'appMode', value: mode, updated_at: new Date().toISOString() }).catch(() => {});
  }, []);

  const setSelectedStage = useCallback((stage: string) => {
    setSelectedStageState(stage);
    db.local_settings.put({ key: 'selectedStage', value: stage, updated_at: new Date().toISOString() }).catch(() => {});
  }, []);

  const setSelectedArticleId = useCallback((article: string) => {
    setSelectedArticleIdState(article);
    db.local_settings.put({ key: 'selectedArticleId', value: article, updated_at: new Date().toISOString() }).catch(() => {});
  }, []);

  const loadCourse = useCallback(async (courseId: string) => {
    if (currentCourse === courseId && courseData) return;
    try {
      let data = null;
      let vocabData = null;
      
      const { data: courseRow, error } = await supabase
        .from('courses')
        .select('r2_json_url, r2_vocab_url, updated_at')
        .eq('id', courseId)
        .single();

      if (error || !courseRow?.r2_json_url) {
        throw new Error(`Course not found or missing r2_json_url for ${courseId}`);
      }

      const cached = await db.course_data.get(courseId);
      const remoteUpdated = courseRow.updated_at ? new Date(courseRow.updated_at).getTime() : 0;
      const localUpdated = cached?.updated_at ? new Date(cached.updated_at).getTime() : 0;

      const hasValidDict = cached && (
        (Array.isArray(cached.dictionary) && cached.dictionary.length > 0) ||
        (cached.dictionary && typeof cached.dictionary === 'object' && Object.keys(cached.dictionary).length > 0)
      );

      if (cached && cached.articles && Object.keys(cached.articles).length > 0 && hasValidDict && localUpdated >= remoteUpdated) {
        data = cached.articles;
        vocabData = cached.dictionary || [];
      } else {
        console.log(`Cache invalid or missing. Fetching course ${courseId} from remote...`);
        data = await fetchCourseData(`${courseRow.r2_json_url}?v=${remoteUpdated}`);
        
        try {
          if (courseRow.r2_vocab_url) {
            vocabData = await fetchCourseData(`${courseRow.r2_vocab_url}?v=${remoteUpdated}`);
          } else {
            // Fallback assumption based on current courseId
            vocabData = await fetchCourseData(`courses/${courseId}/course_${courseId}_vocab.json?v=${remoteUpdated}`);
          }
        } catch (err) {
          console.warn("Failed to fetch vocab data", err);
          vocabData = [];
        }
        
        const cacheData = {
          courseId,
          dictionary: vocabData,
          articles: data,
          updated_at: courseRow.updated_at || new Date().toISOString()
        };
        await db.course_data.put(cacheData);
      }
      
      const dictMap: Record<string, string> = {};
      if (Array.isArray(vocabData)) {
        for (const v of vocabData) {
          if (v.base_form) {
            const translation = v.en_translation || v.contextual_en || v.en;
            if (translation && !dictMap[v.base_form.toLowerCase()]) {
              dictMap[v.base_form.toLowerCase()] = translation;
            }
          }
        }
      } else if (vocabData && typeof vocabData === 'object') {
        Object.assign(dictMap, vocabData);
      }

      setCourseData(data);
      setDictionary(dictMap);
      setCurrentCourse(courseId);
    } catch (err) {
      console.error('Error loading course data:', err);
      const cached = await db.course_data.get(courseId);
      if (cached && cached.articles) {
        const dictMap: Record<string, string> = {};
        if (Array.isArray(cached.dictionary)) {
          for (const v of cached.dictionary) {
            if (v.base_form) {
              const translation = v.en_translation || v.contextual_en || v.en;
              if (translation && !dictMap[v.base_form.toLowerCase()]) {
                dictMap[v.base_form.toLowerCase()] = translation;
              }
            }
          }
        } else if (cached.dictionary && typeof cached.dictionary === 'object') {
          Object.assign(dictMap, cached.dictionary);
        }
        setCourseData(cached.articles);
        setDictionary(dictMap);
        setCurrentCourse(courseId);
      } else {
        throw err;
      }
    }
  }, [currentCourse, courseData]);

  const syncLearningQueue = useCallback(async () => {
    if (!currentCourse || !selectedArticleId) {
      setLearningQueue([]);
      return;
    }
    const cached = await db.course_data.get(currentCourse);
    if (!cached || !cached.dictionary) return;
    
    const vocabList = (cached.dictionary || []) as WordObject[];
    
    let targetWordsSet = new Set<string>();
    const sentenceMap = new Map<string, { sv: string, en: string }>();
    const wordToSentenceMap = new Map<string, { sv: string, en: string }>();

    if (cached.articles && cached.articles.stages) {
        for (const s of cached.articles.stages) {
            for (const a of s.articles) {
                if (a.article_id === selectedArticleId && a.sentences) {
                    for (const sent of a.sentences) {
                        if (sent.sentence_id) {
                            sentenceMap.set(sent.sentence_id, { sv: sent.sv, en: sent.en });
                        }
                        if (sent.target_words) {
                            for (const tw of sent.target_words) {
                                targetWordsSet.add(tw.base_form);
                                if (!wordToSentenceMap.has(tw.base_form.toLowerCase())) {
                                    wordToSentenceMap.set(tw.base_form.toLowerCase(), { sv: sent.sv, en: sent.en });
                                }
                            }
                        }
                        if (sent.secondary_words) {
                            for (const sw of sent.secondary_words) {
                                if (!wordToSentenceMap.has(sw.base_form.toLowerCase())) {
                                    wordToSentenceMap.set(sw.base_form.toLowerCase(), { sv: sent.sv, en: sent.en });
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    const exRecords = await db.excluded_dictionary.toArray();
    const excludedVocab = exRecords.map(r => r.base_form.toLowerCase());
    setExcludedVocab(excludedVocab);

    let articleVocab: WordObject[] = [];
    if (Array.isArray(vocabList) && vocabList.length > 0) {
      articleVocab = vocabList
        .filter(w => {
          if (w.article_id !== selectedArticleId || !targetWordsSet.has(w.base_form)) return false;
          const base = (w.base_form || '').toLowerCase();
          const inSent = (w.word_in_sentence || '').toLowerCase();
          const isEx = (base && excludedVocab.includes(base)) || (inSent && excludedVocab.includes(inSent));
          return !isEx;
        })
        .map(w => {
          const sentInfo = (w.sentence_id && sentenceMap.get(w.sentence_id)) || wordToSentenceMap.get(w.base_form.toLowerCase());
          return {
            ...w,
            sentence: sentInfo?.sv || w.sentence || '',
            sentence_en: sentInfo?.en || w.sentence_en || '',
            context_sv: sentInfo?.sv || w.sentence || '',
            context_en: sentInfo?.en || w.sentence_en || ''
          };
        });
    }

    // Robust Fallback: If vocabList didn't match or was empty, construct directly from target_words in the article sentences!
    if (articleVocab.length === 0 && cached.articles && cached.articles.stages) {
      for (const s of cached.articles.stages) {
        for (const a of s.articles || []) {
          if (a.article_id === selectedArticleId && a.sentences) {
            for (const sent of a.sentences) {
              if (sent.target_words) {
                for (const tw of sent.target_words) {
                  const base = (tw.base_form || '').toLowerCase();
                  const inSent = (tw.word_in_sentence || '').toLowerCase();
                  const isEx = (base && excludedVocab.includes(base)) || (inSent && excludedVocab.includes(inSent));
                  if (!isEx) {
                    articleVocab.push({
                      base_form: tw.base_form,
                      word_in_sentence: tw.word_in_sentence || tw.base_form,
                      en_translation: tw.en_translation || tw.contextual_en || '',
                      contextual_en: tw.contextual_en || '',
                      dict_en: tw.dict_en || tw.contextual_en || '',
                      article_id: a.article_id,
                      stage_id: s.stage_id,
                      course_id: currentCourse,
                      sentence: sent.sv || '',
                      sentence_en: sent.en || '',
                      context_sv: sent.sv || '',
                      context_en: sent.en || '',
                      sentence_id: sent.sentence_id || '',
                      synced: true,
                      updated_at: new Date(0).toISOString()
                    } as unknown as WordObject);
                  }
                }
              }
            }
          }
        }
      }
    }
    
    const customVocab = await db.custom_dictionary.where('article_id').equals(selectedArticleId).toArray();
    articleVocab = [...articleVocab, ...customVocab];
    
    // Deduplicate
    const uniqueMap = new Map<string, WordObject>();
    articleVocab.forEach(w => uniqueMap.set(w.base_form.toLowerCase(), w));
    articleVocab = Array.from(uniqueMap.values());
    
    // Clean up any stale in-progress learning_queue items that are now in FSRS, excluded, or orphan
    try {
      const existingQueue = await db.learning_queue.where('article_id').equals(selectedArticleId).toArray();
      const fsrsRecords = await db.fsrs_progress.where('course_id').equals(currentCourse).toArray();
      const fsrsSet = new Set(fsrsRecords.filter(r => r.state !== 0).map(r => (r.word_id || '').toLowerCase()));

      for (const item of existingQueue) {
        const base = (item.base_form || '').toLowerCase();
        const isEx = base && excludedVocab.includes(base);
        const isGraduated = base && fsrsSet.has(base);
        if ((isEx || isGraduated) && item.id) {
          await db.learning_queue.delete(item.id);
        }
      }

      // Purge orphan records without article_id
      const orphans = await db.learning_queue.filter(r => !r.article_id).toArray();
      for (const o of orphans) {
        if (o.id) await db.learning_queue.delete(o.id);
      }
    } catch (e) {}

    // In-memory representation for current article study session
    setLearningQueue(articleVocab);
  }, [currentCourse, selectedArticleId, selectedStage]);

  const refreshLearningQueue = useCallback(async () => {
    await syncLearningQueue();
  }, [syncLearningQueue]);

  useEffect(() => {
    syncLearningQueue();
  }, [syncLearningQueue]);

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
                 const { error: upErr } = await supabase.from('custom_dictionary').update(toInsert).eq('id', existingRemote.id);
                 if (!upErr && item.id) {
                   await db.custom_dictionary.update(item.id, { synced: true });
                 }
             } else {
                 if (item.id) await db.custom_dictionary.update(item.id, { synced: true });
             }
          } else {
             const { error: insErr } = await supabase.from('custom_dictionary').insert({ ...toInsert, user_id: user.id });
             if (!insErr && item.id) {
               await db.custom_dictionary.update(item.id, { synced: true });
             }
          }
        }
        
        const { data: finalData } = await supabase
          .from('custom_dictionary')
          .select('*')
          .eq('user_id', user.id);
          
        if (finalData) {
          await db.transaction('rw', [db.custom_dictionary, db.learning_queue], async () => {
            const remoteBaseForms = new Set(finalData.map(r => (r.base_form || '').toLowerCase()));
            const currentLocals = await db.custom_dictionary.toArray();
            for (const loc of currentLocals) {
              // ONLY delete if it was previously confirmed synced and is now deleted on remote
              if (loc.id && loc.synced && !remoteBaseForms.has((loc.base_form || '').toLowerCase())) {
                await db.custom_dictionary.delete(loc.id);
                // Also clean up from learning_queue if it was a custom word
                const lqMatches = await db.learning_queue.where('base_form').equalsIgnoreCase(loc.base_form).toArray();
                for (const lq of lqMatches) {
                  if (lq.id) await db.learning_queue.delete(lq.id);
                }
              }
            }

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

  const refreshExcludedDictionary = useCallback(async () => {
    try {
      await syncExcludedDictionary();
      const exRecords = await db.excluded_dictionary.toArray();
      setExcludedVocab(exRecords.map(r => r.base_form.toLowerCase()));
    } catch (e) {
      console.warn('Error refreshing excluded dictionary:', e);
    }
  }, []);

  useEffect(() => {
    refreshExcludedDictionary();
  }, [refreshExcludedDictionary]);

  return (
    <DataContext.Provider value={{ 
      courseData, 
      dictionary,
      loadCourse,
      selectedStage, setSelectedStage,
      selectedArticleId, setSelectedArticleId,
      appMode, setAppMode,
      learningQueue,
      customDictionary,
      excludedVocab,
      refreshLearningQueue,
      removeFromLearningQueue,
      addToCustomDictionary,
      refreshCustomDictionary,
      refreshExcludedDictionary
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
