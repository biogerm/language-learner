import { createContext, useContext, useState, useCallback, useEffect, useRef, type ReactNode } from 'react';
import { fetchCourseData } from '../services/r2';
import { supabase } from '../services/supabase';
import { db, type WordObject } from '../db/dexie';
import { syncExcludedDictionary, syncCustomDictionary } from '../services/sync';

interface DataContextType {
  courseData: Record<string, Record<string, any>> | null;
  dictionary: Record<string, any> | null;
  loadCourse: (courseId: string) => Promise<void>;
  syncLearningQueueRemote: () => Promise<void>;
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
  const [selectedStage, setSelectedStageState] = useState<string>(() => {
    try {
      return localStorage.getItem('selectedStage') || '';
    } catch {
      return '';
    }
  });
  const [selectedArticleId, setSelectedArticleIdState] = useState<string>(() => {
    try {
      return localStorage.getItem('selectedArticleId') || '';
    } catch {
      return '';
    }
  });
  const [appMode, setAppModeState] = useState<'study' | 'review'>(() => {
    try {
      const mode = localStorage.getItem('appMode');
      if (mode === 'study' || mode === 'review') return mode;
    } catch {}
    return 'study';
  });

  const [learningQueue, setLearningQueue] = useState<WordObject[]>([]);
  const [customDictionary, setCustomDictionary] = useState<WordObject[]>([]);
  const [excludedVocab, setExcludedVocab] = useState<string[]>([]);

  // Initialize client settings from Dexie local_settings (fallback/sync)
  useEffect(() => {
    (async () => {
      try {
        const mode = await db.local_settings.get('appMode');
        if (mode && (mode.value === 'study' || mode.value === 'review')) {
          setAppModeState(mode.value);
          try { localStorage.setItem('appMode', mode.value); } catch {}
        }
        const stage = await db.local_settings.get('selectedStage');
        if (stage && typeof stage.value === 'string') {
          setSelectedStageState(stage.value);
          try { localStorage.setItem('selectedStage', stage.value); } catch {}
        }
        const art = await db.local_settings.get('selectedArticleId');
        if (art && typeof art.value === 'string') {
          setSelectedArticleIdState(art.value);
          try { localStorage.setItem('selectedArticleId', art.value); } catch {}
        }
      } catch (e) {
        console.warn('Error loading local settings from Dexie:', e);
      }
    })();
  }, []);

  const setAppMode = useCallback((mode: 'study' | 'review') => {
    setAppModeState(mode);
    try { localStorage.setItem('appMode', mode); } catch {}
    db.local_settings.put({ key: 'appMode', value: mode, updated_at: new Date().toISOString() }).catch(() => {});
  }, []);

  const setSelectedStage = useCallback((stage: string) => {
    setSelectedStageState(stage);
    try { localStorage.setItem('selectedStage', stage); } catch {}
    db.local_settings.put({ key: 'selectedStage', value: stage, updated_at: new Date().toISOString() }).catch(() => {});
  }, []);

  const setSelectedArticleId = useCallback((article: string) => {
    setSelectedArticleIdState(article);
    try { localStorage.setItem('selectedArticleId', article); } catch {}
    db.local_settings.put({ key: 'selectedArticleId', value: article, updated_at: new Date().toISOString() }).catch(() => {});
  }, []);

  const currentCourseRef = useRef<string | null>(null);
  const courseDataRef = useRef<any>(null);

  useEffect(() => {
    currentCourseRef.current = currentCourse;
    courseDataRef.current = courseData;
  }, [currentCourse, courseData]);

  const inFlightCourseLoadsRef = useRef<Map<string, Promise<void>>>(new Map());

  const loadCourse = useCallback(async (courseId: string) => {
    if (currentCourseRef.current === courseId && courseDataRef.current) return;
    if (inFlightCourseLoadsRef.current.has(courseId)) {
      return inFlightCourseLoadsRef.current.get(courseId);
    }

    const loadPromise = (async () => {
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
              vocabData = await fetchCourseData(`courses/${courseId}/course_${courseId}_vocab.json?v=${remoteUpdated}`);
            }
          } catch (err) {
            console.warn("Failed to fetch vocab data", err);
            vocabData = [];
          }
          
          try {
            const cacheData = {
              courseId,
              dictionary: vocabData,
              articles: data,
              updated_at: courseRow.updated_at || new Date().toISOString()
            };
            await db.course_data.put(cacheData);
          } catch (cacheErr) {
            console.warn("Failed to cache course data in IndexedDB:", cacheErr);
          }
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

        if (dictMap['fortfarande'] === 'sill') {
          dictMap['fortfarande'] = 'still';
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
          if (dictMap['fortfarande'] === 'sill') {
            dictMap['fortfarande'] = 'still';
          }
          setCourseData(cached.articles);
          setDictionary(dictMap);
          setCurrentCourse(courseId);
        } else {
          throw err;
        }
      } finally {
        inFlightCourseLoadsRef.current.delete(courseId);
      }
    })();

    inFlightCourseLoadsRef.current.set(courseId, loadPromise);
    return loadPromise;
  }, []);

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
      await syncCustomDictionary();
      const local = await db.custom_dictionary.toArray();
      setCustomDictionary(local);
    } catch (err) {
      console.warn("Offline or sync failed, using local customDictionary data", err);
    }
  }, []);

  useEffect(() => {
    refreshCustomDictionary();
  }, [refreshCustomDictionary]);

  const syncLearningQueueRemote = async (retries = 3): Promise<void> => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // 1. PUSH FIRST: send any dirty/unsynced local records to cloud
      const localQueue = await db.learning_queue.toArray();
      const dirtyRecords = (localQueue || []).filter(r => !r.synced);

      if (dirtyRecords.length > 0) {
        const payloadToPush = dirtyRecords.map(record => ({
          user_id: user.id,
          course_id: record.course_id || 'sfid',
          article_id: record.article_id,
          base_form: record.base_form,
          dictation_passed: !!record.dictation_passed,
          flashcard_passed: !!record.flashcard_passed,
          status: record.status || 'active',
          updated_at: record.updated_at || new Date().toISOString()
        }));

        const { error: pushError } = await supabase
          .from('learning_queue')
          .upsert(payloadToPush, { onConflict: 'user_id, course_id, article_id, base_form' });

        if (pushError) {
          throw pushError;
        }

        // Mark pushed records as synced in local Dexie
        await db.transaction('rw', db.learning_queue, async () => {
          for (const d of dirtyRecords) {
            if (d.id) {
              await db.learning_queue.update(d.id, { synced: true });
            }
          }
        });
      }

      // 2. PULL SECOND: fetch fresh, authoritative cloud state AFTER push completes
      const { data: remoteData, error: pullError } = await supabase
        .from('learning_queue')
        .select('*')
        .eq('user_id', user.id);

      if (pullError) throw pullError;

      // 3. MERGE: reconcile cloud state with local Dexie
      if (remoteData) {
        await db.transaction('rw', db.learning_queue, async () => {
          const currentLocal = await db.learning_queue.toArray();

          // A. Purge local synced items that no longer exist remotely (deleted on another device)
          for (const localItem of currentLocal) {
            if (localItem.synced) {
              const stillExists = remoteData.some(
                r => r.article_id === localItem.article_id && r.base_form === localItem.base_form
              );
              if (!stillExists && localItem.id) {
                await db.learning_queue.delete(localItem.id);
              }
            }
          }

          // B. Upsert remote items into local
          for (const remote of remoteData) {
            const local = await db.learning_queue
              .where({ article_id: remote.article_id, base_form: remote.base_form })
              .first();

            if (local) {
              // Never overwrite unsynced local changes
              if (!local.synced) continue;

              const localUpdated = local.updated_at ? new Date(local.updated_at).getTime() : 0;
              const remoteUpdated = remote.updated_at ? new Date(remote.updated_at).getTime() : 0;
              if (localUpdated >= remoteUpdated) continue;

              await db.learning_queue.update(local.id!, {
                dictation_passed: !!remote.dictation_passed,
                flashcard_passed: !!remote.flashcard_passed,
                status: remote.status,
                updated_at: remote.updated_at,
                synced: true
              });
            } else {
              await db.learning_queue.add({
                base_form: remote.base_form,
                word_in_sentence: remote.word_in_sentence || remote.base_form,
                en_translation: remote.en_translation || '',
                contextual_en: remote.contextual_en || '',
                dict_en: remote.dict_en || '',
                article_id: remote.article_id,
                stage_id: remote.stage_id || '',
                course_id: remote.course_id || 'sfid',
                sentence_id: remote.sentence_id || '',
                sentence: remote.sentence || '',
                sentence_en: remote.sentence_en || '',
                context_sv: remote.context_sv || '',
                context_en: remote.context_en || '',
                dictation_passed: !!remote.dictation_passed,
                flashcard_passed: !!remote.flashcard_passed,
                status: remote.status || 'active',
                updated_at: remote.updated_at || new Date().toISOString(),
                synced: true
              } as any);
            }
          }
        });

        window.dispatchEvent(new CustomEvent("learning-queue-updated"));
        window.dispatchEvent(new CustomEvent("fsrs-sync", { detail: "Sync Complete" }));
      }
    } catch (err) {
      if (retries > 0) {
        console.warn(`[Sync] syncLearningQueueRemote encountered error, retrying in 1500ms (${retries} left):`, err);
        setTimeout(() => syncLearningQueueRemote(retries - 1), 1500);
      } else {
        console.error("[Sync] syncLearningQueueRemote failed after retries:", err);
      }
    }
  };

  useEffect(() => {
    const handleOnline = () => {
        syncLearningQueueRemote().catch(console.error);
        syncExcludedDictionary().catch(console.error);
        syncCustomDictionary().catch(console.error);
    };
    const handleVisibility = () => {
      if (document.visibilityState === 'visible') {
        syncLearningQueueRemote().catch(console.error);
      }
    };
    window.addEventListener('online', handleOnline);
    document.addEventListener('visibilitychange', handleVisibility);
    // Initial load sync
    syncLearningQueueRemote().catch(console.error);
    syncExcludedDictionary().catch(console.error);
    syncCustomDictionary().catch(console.error);
    return () => {
      window.removeEventListener('online', handleOnline);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
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
      syncLearningQueueRemote,
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
