import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { db } from '../db/dexie';
import { submitGatePass, getFSRSStats } from '../utils/fsrs';
import { useData } from '../contexts/DataContext';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../services/supabase';
import { formatWordPrompt } from '../utils/format';
import { buildStudyQueue } from '../utils/queueBuilder';
import { playExactWordAudio, preProbeWordAudio } from '../utils/sound';

export default function Dictation() {
  const { courseId } = useParams();
  const { courseData, dictionary, selectedStage, selectedArticleId, learningQueue, appMode, syncLearningQueueRemote } = useData();
  const { isTester } = useAuth();
  const [queue, setQueue] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [input, setInput] = useState('');
  const [startTime, setStartTime] = useState(Date.now());
  const [wrongCount, setWrongCount] = useState(0);
  const [status, setStatus] = useState<'typing' | 'correct' | 'revealed'>('typing');
  const [loading, setLoading] = useState(true);
  const [feedbackMsg, setFeedbackMsg] = useState('');
  const [fsrsStats, setFsrsStats] = useState<any>(null);
  
  const [inputState, setInputState] = useState<'default' | 'correct' | 'incorrect'>('default');
  const [timerFill, setTimerFill] = useState('0%');
  const [stats, setStats] = useState<{ total: number; mastered: number; remaining: number; inFsrsCount?: number }>({ total: 0, mastered: 0, remaining: 0, inFsrsCount: 0 });

  const inputRef = useRef<HTMLInputElement | null>(null);
  const timerRef = useRef<any>(null);
  const intervalRef = useRef<any>(null);
  const isAdvancingRef = useRef(false);
  const advanceStartTimeRef = useRef<number>(0);

  useEffect(() => {
    setCurrentIndex(0);
    setWrongCount(0);
    setInput('');
    setStatus('typing');
    setInputState('default');
    setFeedbackMsg('');
    setTimerFill('0%');
    isAdvancingRef.current = false;
    advanceStartTimeRef.current = 0;
    if (timerRef.current) clearTimeout(timerRef.current);
    if (intervalRef.current) clearInterval(intervalRef.current);
  }, [courseId, selectedStage, selectedArticleId, appMode]);



  const loadFSRSStats = useCallback(async () => {
    try {
      const s = await getFSRSStats(courseId);
      setFsrsStats(s);
    } catch (e) {
      console.error('Failed to load FSRS stats:', e);
    }
  }, [courseId]);

  useEffect(() => {
    if (appMode === 'review') {
      loadFSRSStats();
    }
  }, [appMode, loadFSRSStats]);

  const updateMasteryAndVocab = async (wordId: string, isCorrect: boolean) => {
    if (!selectedArticleId) return;
    try {
      const cleanWord = wordId.toLowerCase();
      let existing = await db.learning_queue
        .where('article_id')
        .equals(selectedArticleId)
        .filter(r => (r.base_form || '').toLowerCase() === cleanWord)
        .first();

      // If the word isn't in db.learning_queue yet (words in Study mode live only in React state),
      // create it now so the gate-pass status can be persisted and synced to Supabase.
      if (!existing) {
        const queueItem = queue.find((q: any) =>
          (q.word_id || q.base_form || '').toLowerCase() === cleanWord
        );
        await db.learning_queue.add({
          base_form: queueItem?.base_form || wordId,
          word_in_sentence: queueItem?.word_in_sentence || wordId,
          en_translation: queueItem?.en_translation || '',
          contextual_en: queueItem?.contextual_en || '',
          dict_en: queueItem?.dict_en || '',
          article_id: selectedArticleId,
          stage_id: queueItem?.stage_id || selectedStage || '',
          course_id: courseId || 'sfid',
          sentence_id: queueItem?.sentence_id || '',
          sentence: queueItem?.sentence || queueItem?.context_sv || '',
          sentence_en: queueItem?.sentence_en || queueItem?.context_en || '',
          context_sv: queueItem?.context_sv || queueItem?.sentence || '',
          context_en: queueItem?.context_en || queueItem?.sentence_en || '',
          dictation_passed: false,
          flashcard_passed: false,
          status: 'active',
          synced: false,
          updated_at: new Date().toISOString()
        } as any);
        existing = await db.learning_queue
          .where('article_id')
          .equals(selectedArticleId)
          .filter(r => (r.base_form || '').toLowerCase() === cleanWord)
          .first();
      }

      if (existing && existing.id) {
        await db.learning_queue.update(existing.id, {
          dictation_passed: isCorrect,
          updated_at: new Date().toISOString(),
          synced: false
        });

        // Trigger background sync immediately to ensure cloud is up to date
        syncLearningQueueRemote().catch((e: any) => console.warn('Sync failed:', e));
      }
    } catch (e: any) {
      console.warn('Error updating learning_queue in Dexie:', e);
    }

    if (isCorrect) {
      setStats(prev => ({
        ...prev,
        mastered: Math.min(prev.total, prev.mastered + 1),
        remaining: Math.max(0, prev.remaining - 1)
      }));
    }
  };

  const lastScopeKeyRef = useRef<string>('');
  const queueRef = useRef<any[]>([]);
  const isFetchingRef = useRef<boolean>(false);

  const fetchQueue = useCallback(async () => {
    if (isFetchingRef.current) return;
    try {
      const scopeKey = appMode === 'review'
        ? `review_${courseId || ''}`
        : `study_${courseId || ''}_${selectedStage || ''}_${selectedArticleId || ''}`;
      // In review mode, never short-circuit via scopeKey cache — FSRS due dates change every session.
      // In study mode, cache is safe since the article/stage scope is stable during a session.
      if (appMode !== 'review' && lastScopeKeyRef.current === scopeKey && queueRef.current.length > 0) {
        return;
      }

      isFetchingRef.current = true;
      setLoading(true);
      const { queue: newQueue, total, mastered, remaining, inFsrsCount } = await buildStudyQueue(
        appMode as 'study' | 'review',
        courseId || '',
        selectedArticleId,
        'dictation',
        learningQueue
      );

      lastScopeKeyRef.current = scopeKey;
      queueRef.current = newQueue;
      setQueue(newQueue);
      setCurrentIndex(0);
      setStats({ total, mastered, remaining, inFsrsCount: inFsrsCount || 0 });
      
      if (appMode === 'review') {
        await loadFSRSStats();
      }
    } catch(e) {
      console.error(e);
    } finally {
      setLoading(false);
      isFetchingRef.current = false;
    }
  }, [appMode, courseId, selectedStage, selectedArticleId, loadFSRSStats, learningQueue]);

  useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

  // Listen for sync completion to immediately refresh stats without disrupting in-progress queue
  useEffect(() => {
    const handleSyncDone = async () => {
      if (queueRef.current.length > 0 || isFetchingRef.current) {
        try {
          const { total, mastered, remaining, inFsrsCount } = await buildStudyQueue(
            appMode as 'study' | 'review',
            courseId || '',
            selectedArticleId,
            'dictation',
            learningQueue
          );
          setStats({ total, mastered, remaining, inFsrsCount: inFsrsCount || 0 });
        } catch (e) {}
      } else {
        await fetchQueue();
      }
    };
    window.addEventListener('learning-queue-updated', handleSyncDone);
    return () => window.removeEventListener('learning-queue-updated', handleSyncDone);
  }, [appMode, courseId, selectedArticleId, learningQueue, fetchQueue]);

  const handleResetProgress = async () => {
    if (appMode !== 'study' || !selectedArticleId) return;
    setLoading(true);
    try {
      const records = await db.learning_queue.where('article_id').equals(selectedArticleId).toArray();
      const articleWords = (learningQueue || [])
        .filter(w => w.article_id === selectedArticleId)
        .map(w => (w.base_form || '').toLowerCase().trim())
        .filter(Boolean);
      const nowIso = new Date().toISOString();

      // 1. Reset local learning_queue
      for (const r of records) {
        if (r.id) {
          await db.learning_queue.update(r.id, {
            dictation_passed: false,
            flashcard_passed: false,
            status: 'active',
            synced: true,
            updated_at: nowIso
          });
        }
      }

      // 2. Clear any local FSRS progress for words in this article
      for (const w of articleWords) {
        await db.fsrs_progress.delete(w);
      }

      // 3. Reset in Supabase cloud (UPDATE is RLS-supported and ensures persistent reset)
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        await supabase
          .from('learning_queue')
          .update({
            dictation_passed: false,
            flashcard_passed: false,
            status: 'active',
            updated_at: nowIso
          })
          .eq('user_id', user.id)
          .eq('article_id', selectedArticleId);
      }

      window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: 'Progress Reset' }));
    } catch (e) {
      console.error('Error resetting progress:', e);
    }
    queueRef.current = [];
    lastScopeKeyRef.current = '';
    await fetchQueue();
    setLoading(false);
  };

  const handleResetFSRS = async () => {
    if (!isTester) return;
    if (window.confirm("Are you sure you want to clear all FSRS review progress?")) {
      try {
        await db.fsrs_progress.clear();
        const { data } = await supabase.auth.getUser();
        if (data?.user) {
          await supabase.from('fsrs_progress').delete().eq('user_id', data.user.id);
        }
      } catch (e) {
        console.error('Error clearing FSRS:', e);
      }
      window.location.reload();
    }
  };

  const currentRecord = queue[currentIndex];
  
  const enPrompt = currentRecord ? formatWordPrompt(currentRecord, dictionary) : 'Custom Word';

  const cleanAudioName = currentRecord?.word_id ? currentRecord.word_id.replace(/[.,!?"':;()]/g, '').trim().toLowerCase() : '';
  const currentWord = currentRecord ? { 
    id: currentRecord.word_id, 
    word: currentRecord.word_id, 
    audio: `words_audio/${cleanAudioName}.mp3` 
  } : null;

  const getExampleSentence = () => {
    let sv = '';
    let en = '';
    let foundWordInSent = '';
    let foundContextualEn = '';

    if (currentRecord?.sentence && currentRecord.sentence !== currentRecord.word_id && currentRecord.sentence !== currentRecord.word_in_sentence) {
      sv = currentRecord.sentence;
      en = currentRecord.context_en || currentRecord.sentence_en || '';
    } else if (currentRecord?.context_sv) {
      sv = currentRecord.context_sv;
      en = currentRecord.context_en || currentRecord.sentence_en || '';
    }
    
    // Look in current selected article first or search all stages
    if (courseData && (courseData as any).stages && currentWord?.word) {
      const stages = (courseData as any).stages;
      const targetArticleId = currentRecord?.article_id || selectedArticleId;
      const targetLower = currentWord.word.toLowerCase();
      const currentArt = stages.flatMap((s: any) => s.articles || []).find((a: any) => a.article_id === targetArticleId);
      
      const checkSentences = currentArt ? currentArt.sentences || [] : [];
      for (const sItem of checkSentences) {
        const matchTw = (sItem.target_words || []).find((tw: any) =>
          (tw.base_form && tw.base_form.toLowerCase() === targetLower) ||
          (tw.word_in_sentence && tw.word_in_sentence.toLowerCase() === targetLower)
        ) || (sItem.secondary_words || []).find((sw: any) =>
          (sw.base_form && sw.base_form.toLowerCase() === targetLower) ||
          (sw.word_in_sentence && sw.word_in_sentence.toLowerCase() === targetLower)
        );
        if (matchTw) {
          if (!sv) sv = sItem.sv;
          if (!en) en = sItem.en || '';
          foundWordInSent = matchTw.word_in_sentence || '';
          foundContextualEn = matchTw.contextual_en || '';
          break;
        }
        if (!sv && sItem.sv && sItem.sv.toLowerCase().includes(targetLower)) {
          sv = sItem.sv;
          en = sItem.en || '';
          break;
        }
      }

      if (!sv) {
        for (const s of stages) {
          for (const a of s.articles || []) {
            for (const sItem of a.sentences || []) {
              const matchTw = (sItem.target_words || []).find((tw: any) =>
                (tw.base_form && tw.base_form.toLowerCase() === targetLower) ||
                (tw.word_in_sentence && tw.word_in_sentence.toLowerCase() === targetLower)
              );
              if (matchTw) {
                sv = sItem.sv;
                en = sItem.en || '';
                foundWordInSent = matchTw.word_in_sentence || '';
                foundContextualEn = matchTw.contextual_en || '';
                break;
              }
              if (sItem.sv && sItem.sv.toLowerCase().includes(targetLower)) {
                sv = sItem.sv;
                en = sItem.en || '';
                break;
              }
            }
            if (sv) break;
          }
          if (sv) break;
        }
      }
    }
    return { sv, en, foundWordInSent, foundContextualEn };
  };
  const exampleSentenceObj = getExampleSentence();
  const exampleSentence = exampleSentenceObj.sv;
  const exampleSentenceEn = exampleSentenceObj.en;

  const renderHighlightedSwedish = (text: string) => {
    if (!text || !currentRecord) return text;
    const wordsToHighlight = [
      currentRecord.word_in_sentence,
      currentRecord.word_id,
      currentRecord.base_form,
      currentWord?.word,
      exampleSentenceObj.foundWordInSent
    ].filter(Boolean)
      .map(w => (w as string).trim())
      .filter(w => w.length > 0);

    const expandedWords = new Set<string>();
    wordsToHighlight.forEach(w => {
      expandedWords.add(w);
      const low = w.toLowerCase();
      expandedWords.add(low);
      // Swedish inflections & endings
      expandedWords.add(low + 't');
      expandedWords.add(low + 'a');
      expandedWords.add(low + 'are');
      expandedWords.add(low + 'ast');
      expandedWords.add(low + 'en');
      expandedWords.add(low + 'et');
      expandedWords.add(low + 'na');
      expandedWords.add(low + 's');
      expandedWords.add(low + 'ar');
      expandedWords.add(low + 'er');
      expandedWords.add(low + 'or');
      expandedWords.add(low + 'de');
      expandedWords.add(low + 'te');
      expandedWords.add(low + 'ade');
      expandedWords.add(low + 'at');
      if (low.endsWith('a')) {
        expandedWords.add(low.slice(0, -1) + 'er');
        expandedWords.add(low.slice(0, -1) + 'ade');
        expandedWords.add(low.slice(0, -1) + 'at');
        expandedWords.add(low.slice(0, -1) + 'de');
        expandedWords.add(low.slice(0, -1) + 't');
        expandedWords.add(low.slice(0, -1) + 'r');
      }
    });

    const uniqueWords = Array.from(expandedWords).sort((a, b) => b.length - a.length);
    if (!uniqueWords.length) return text;

    const escaped = uniqueWords.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
    const regex = new RegExp(`(?:^|(?<=[^\\p{L}\\p{N}]))(${escaped})(?=[^\\p{L}\\p{N}]|$)`, 'giu');

    const parts: React.ReactNode[] = [];
    let lastIdx = 0;
    let match;
    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIdx) {
        parts.push(text.slice(lastIdx, match.index));
      }
      parts.push(
        <span
          key={match.index}
          className="sentence-highlight-sv"
          style={{
            color: '#c084fc',
            backgroundColor: 'rgba(168, 85, 247, 0.22)',
            padding: '1px 6px',
            borderRadius: '4px',
            fontWeight: 700,
            borderBottom: '2px solid #a855f7'
          }}
        >
          {match[0]}
        </span>
      );
      lastIdx = match.index + match[0].length;
    }
    if (lastIdx < text.length) {
      parts.push(text.slice(lastIdx));
    }
    return parts.length ? parts : text;
  };

  const renderHighlightedEnglish = (text: string) => {
    if (!text || !currentRecord) return text;

    const rawTerms = [
      currentRecord.contextual_en,
      currentRecord.en_translation,
      currentRecord.en,
      currentRecord.dict_en,
      exampleSentenceObj.foundContextualEn,
      enPrompt
    ].filter(Boolean);

    const candidates = new Set<string>();
    for (const raw of rawTerms) {
      const cleanRaw = raw.replace(/\([^)]*\)/g, '').trim();
      const parts = cleanRaw.split(/[\/,;\n]+/);
      for (let p of parts) {
        p = p.trim().replace(/^(to|a|an|the)\s+/i, '').trim();
        if (p.length > 1) candidates.add(p);
        const words = p.split(/\s+/);
        if (words.length > 1) {
          for (const w of words) {
            const cw = w.trim().replace(/^(to|a|an|the)\s+/i, '').trim();
            if (cw.length > 2) candidates.add(cw);
          }
        }
      }
    }

    const expandedCandidates = new Set<string>();
    candidates.forEach(c => {
      expandedCandidates.add(c);
      const low = c.toLowerCase();
      expandedCandidates.add(low);
      // English inflections & suffixes
      expandedCandidates.add(low + 'ly');
      expandedCandidates.add(low + 's');
      expandedCandidates.add(low + 'es');
      expandedCandidates.add(low + 'ed');
      expandedCandidates.add(low + 'd');
      expandedCandidates.add(low + 'ing');
      expandedCandidates.add(low + 'er');
      expandedCandidates.add(low + 'est');
      if (low.endsWith('y')) {
        expandedCandidates.add(low.slice(0, -1) + 'ily');
        expandedCandidates.add(low.slice(0, -1) + 'ies');
        expandedCandidates.add(low.slice(0, -1) + 'ied');
      }
      if (low.endsWith('e')) {
        expandedCandidates.add(low.slice(0, -1) + 'ing');
        expandedCandidates.add(low.slice(0, -1) + 'ed');
      }
    });

    const sortedCandidates = Array.from(expandedCandidates).sort((a, b) => b.length - a.length);
    if (!sortedCandidates.length) return text;

    const escaped = sortedCandidates.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
    const regex = new RegExp(`(?:^|(?<=[^\\p{L}\\p{N}]))(${escaped})(?=[^\\p{L}\\p{N}]|$)`, 'giu');

    const parts: React.ReactNode[] = [];
    let lastIdx = 0;
    let match;
    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIdx) {
        parts.push(text.slice(lastIdx, match.index));
      }
      parts.push(
        <span
          key={match.index}
          className="sentence-highlight-en"
          style={{
            color: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.2)',
            padding: '1px 6px',
            borderRadius: '4px',
            fontWeight: 600,
            borderBottom: '2px solid #38bdf8'
          }}
        >
          {match[0]}
        </span>
      );
      lastIdx = match.index + match[0].length;
    }
    if (lastIdx < text.length) {
      parts.push(text.slice(lastIdx));
    }
    return parts.length ? parts : text;
  };

  const getMaskedSentence = () => {
    if (!exampleSentence || !currentRecord) return '';
    let masked = exampleSentence;
    const wordsToMask = [currentRecord.word_id, currentRecord.base_form, currentRecord.word_in_sentence]
      .filter(Boolean)
      .sort((a, b) => b.length - a.length);
    wordsToMask.forEach(w => {
      const safeWord = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      masked = masked.replace(new RegExp(`(^|\\W)(${safeWord})(?=\\W|$)`, 'gi'), '$1_____');
    });
    wordsToMask.forEach(w => {
      const safeWord = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      masked = masked.replace(new RegExp(`(${safeWord})`, 'gi'), '_____');
    });
    return masked;
  };

  const getEnglishTranslation = () => {
    if (currentRecord?.context_en) return currentRecord.context_en;
    if (currentRecord?.contextual_en) return currentRecord.contextual_en;
    if (currentRecord?.en_translation) return currentRecord.en_translation;
    if (currentRecord?.en) return currentRecord.en;
    if (dictionary && currentWord?.word && dictionary[currentWord.word.toLowerCase()]) {
      return dictionary[currentWord.word.toLowerCase()];
    }
    return '';
  };
  const enDefinition = getEnglishTranslation();

  const playAudio = useCallback(() => {
    const targetWord = currentWord?.word || currentRecord?.word_id || currentRecord?.base_form;
    if (targetWord) {
      playExactWordAudio(targetWord);
    }
  }, [currentWord, currentRecord]);

  const proceedToNext = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (intervalRef.current) clearInterval(intervalRef.current);
    isAdvancingRef.current = false;
    advanceStartTimeRef.current = 0;
    setStatus('typing');
    setWrongCount(0);
    setInput('');
    setInputState('default');
    setFeedbackMsg('');
    setTimerFill('0%');
    setCurrentIndex(prev => prev + 1);
    setStartTime(Date.now());
    setTimeout(() => {
      inputRef.current?.focus();
    }, 50);
  }, []);

  // Proactively pre-probe audio for current and upcoming words
  useEffect(() => {
    if (currentWord?.word) {
      preProbeWordAudio(currentWord.word);
    }
    const next1 = queue[currentIndex + 1]?.word_id || queue[currentIndex + 1]?.base_form;
    const next2 = queue[currentIndex + 2]?.word_id || queue[currentIndex + 2]?.base_form;
    if (next1) preProbeWordAudio(next1);
    if (next2) preProbeWordAudio(next2);
  }, [currentIndex, currentWord, queue]);

  const triggerAutoAdvance = useCallback(() => {
    const svLen = currentWord?.word?.length || 0;
    const enLen = enDefinition.length;
    const svSentLen = exampleSentence ? exampleSentence.length : 0;
    const enSentLen = exampleSentenceEn ? exampleSentenceEn.length : 0;

    // Generous reading speed for language learning:
    // - Base comprehension buffer: 2500ms
    // - Swedish sentence: 150ms per char
    // - English sentence translation: 100ms per char
    // - Word and definition: 100ms per char
    const calculatedDelay = 2500 + svLen * 100 + enLen * 100 + svSentLen * 150 + enSentLen * 100;
    const minDelay = (svSentLen > 0) ? 6000 : 2500;
    const delay = Math.min(18000, Math.max(minDelay, calculatedDelay));
    
    isAdvancingRef.current = true;
    advanceStartTimeRef.current = Date.now();
    let start = Date.now();
    
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = window.setInterval(() => {
      const elapsed = Date.now() - start;
      const percent = Math.min(100, (elapsed / delay) * 100);
      setTimerFill(`${percent}%`);
    }, 16);
    
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = window.setTimeout(() => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      proceedToNext();
    }, delay);
  }, [currentWord, enDefinition, exampleSentence, exampleSentenceEn, proceedToNext]);

  const handleCorrect = async () => {
    if (!currentWord || !courseId || status !== 'typing') return;
    const timeSpent = (Date.now() - startTime) / 1000;
    const timeSec = Math.round(timeSpent);
    
    setStatus('correct');
    setInputState('correct');
    setFeedbackMsg(`Correct! (Errors: ${wrongCount}, Time: ${timeSec}s)`);
    playAudio();
    
    if (appMode === 'study') {
      updateMasteryAndVocab(currentWord.id, true);
    }

    const res = await submitGatePass(courseId, currentWord.id, 'dictation', wrongCount, timeSpent, false, 0);
    if (res.completed) {
      window.dispatchEvent(new CustomEvent('fsrs-toast', { detail: res.toastMsg || `${res.ratingName} | ${res.dayStr}` }));
    }
    if (appMode === 'review') {
      loadFSRSStats();
      setStats(prev => ({
        total: prev.total,
        mastered: Math.min(prev.total, prev.mastered + 1),
        remaining: Math.max(0, prev.remaining - 1)
      }));
    }

    triggerAutoAdvance();
  };

  const handleReveal = async () => {
    if (!currentWord || !courseId || status !== 'typing') return;
    const timeSpent = (Date.now() - startTime) / 1000;
    
    setStatus('revealed');
    setInputState('incorrect');
    setFeedbackMsg('');
    playAudio();
    
    if (appMode === 'study') {
      updateMasteryAndVocab(currentWord.id, false);
      await submitGatePass(courseId, currentWord.id, 'dictation', wrongCount, timeSpent, true, 1);
    } else {
      // Review mode: mark gave_up — fsrs.ts will trigger FSRS scheduling once BOTH gates are done
      const res = await submitGatePass(courseId, currentWord.id, 'dictation', wrongCount, timeSpent, true, 1);
      if (res.completed) {
        window.dispatchEvent(new CustomEvent('fsrs-toast', { detail: res.toastMsg || `${res.ratingName} | ${res.dayStr}` }));
      }
      loadFSRSStats();
    }

    // Since the word was revealed / failed, re-append to queue so user must practice again this session.
    if (currentRecord) {
      queueRef.current = [...queueRef.current, currentRecord];
      setQueue(prev => [...prev, currentRecord]);
    }

    triggerAutoAdvance();
  };

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        e.stopPropagation();
        playAudio();
        return;
      }
      
      if (e.code === 'Space' && (e.target === document.body || status !== 'typing' || isAdvancingRef.current)) {
        e.preventDefault();
        playAudio();
        return;
      }
      
      if (e.key === 'Escape' || (e.key === '/' && e.metaKey)) {
        e.preventDefault();
        if (isAdvancingRef.current || status === 'revealed') {
          proceedToNext();
        } else if (status === 'typing' && wrongCount >= 1) {
          handleReveal();
        }
        return;
      }

      if ((isAdvancingRef.current || status === 'revealed' || status === 'correct') && e.key === 'Enter') {
        if (advanceStartTimeRef.current > 0 && Date.now() - advanceStartTimeRef.current > 400) {
          e.preventDefault();
          proceedToNext();
        }
        return;
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, [status, wrongCount, appMode, proceedToNext, handleReveal, playAudio]);

  const cleanText = (text: string) => {
    return text.replace(/[.,!?"':;()\-\u2019\u2018\u2026\u201C\u201D\u00AB\u00BB]/g, '').trim().toLowerCase();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      e.stopPropagation();
      playAudio();
      return;
    }

    if (e.key === 'Escape' || (e.key === '/' && e.metaKey)) {
      return;
    }

    if (e.key === 'Enter') {
      e.preventDefault();
      e.stopPropagation();

      if (status === 'revealed') {
        if (appMode !== 'review') {
          if (advanceStartTimeRef.current > 0 && Date.now() - advanceStartTimeRef.current > 400) {
            proceedToNext();
          }
        }
        return;
      }

      if (status === 'correct' || isAdvancingRef.current) {
        if (advanceStartTimeRef.current > 0 && Date.now() - advanceStartTimeRef.current > 400) {
          proceedToNext();
        }
        return;
      }

      if (status !== 'typing' || !currentWord || !courseId) return;
      
      const cleanUserText = cleanText(input);
      if (!cleanUserText) {
        // Ignore pressing Enter on empty input without penalizing as wrong
        return;
      }
      const cleanCorrectText = cleanText(currentWord.word);
      const isCorrect = cleanUserText === cleanCorrectText;
      
      if (!isCorrect) {
        const newWrongCount = wrongCount + 1;
        setWrongCount(newWrongCount);
        setInputState('incorrect');
        
        let fb = '';
        if (cleanUserText.length > cleanCorrectText.length) {
          fb = 'Too long';
        } else if (cleanUserText.length < cleanCorrectText.length) {
          fb = 'Too short';
        } else {
          let errCount = 0;
          for (let i = 0; i < cleanCorrectText.length; i++) {
            if (cleanUserText[i] !== cleanCorrectText[i]) errCount++;
          }
          fb = `${errCount} ${errCount === 1 ? 'letter' : 'letters'} wrong`;
        }
        setFeedbackMsg(fb);
        return;
      }

      handleCorrect();
    }
  };

  const showAnswer = status === 'correct' || status === 'revealed';
  const isAllDone = !loading && stats.total > 0 && (
    appMode === 'study'
      ? (stats.mastered >= stats.total && (currentIndex >= queue.length || (!isAdvancingRef.current && status !== 'correct' && status !== 'revealed')))
      : (queue.length > 0 && currentIndex >= queue.length)
  );

  // Safety net: In study mode, if current queue runs out but some words remain unmastered, auto-recycle remaining
  useEffect(() => {
    if (!loading && appMode === 'study' && queue.length > 0 && currentIndex >= queue.length && stats.mastered < stats.total) {
      fetchQueue();
    }
  }, [currentIndex, queue.length, stats.mastered, stats.total, appMode, loading, fetchQueue]);

  useEffect(() => {
    if (status === 'typing' && !isAllDone && !loading) {
      const timer = setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [currentIndex, status, isAllDone, loading]);

  if (loading) return (
    <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
      <main className="flashcard-container glass-panel">
        <div style={{ padding: '48px', fontSize: '20px', color: 'var(--text)' }}>Loading dictation...</div>
      </main>
    </div>
  );

  return (
    <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
      <main className="flashcard-container glass-panel">
        <div id="progress-stats">
          <span className="stat-total">
            {appMode === 'review' ? `Review Due: ${stats.total}` : `Total: ${stats.total}`}
          </span>
          <span className="stat-correct">Mastered: {stats.mastered}</span>
          <span className="stat-remaining">Remaining: {stats.remaining}</span>
          {appMode === 'study' && (
            <button id="reset-progress-btn" tabIndex={-1} onClick={handleResetProgress}>Reset Progress</button>
          )}
          {appMode === 'review' && isTester && (
            <button id="reset-fsrs-btn" tabIndex={-1} onClick={handleResetFSRS} title="Reset all FSRS review data">Reset FSRS</button>
          )}
        </div>
        
        <div id="feedback-msg" className={`feedback ${!isAllDone && (inputState === 'correct' ? 'correct' : (inputState === 'incorrect' ? 'incorrect' : ''))}`}>
          {!isAllDone && feedbackMsg}
        </div>

        {!isAllDone && (
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', justifyContent: 'center', marginBottom: '2rem' }}>
            <button id="play-btn" tabIndex={-1} className="play-btn" onClick={playAudio} title="Play Audio (Tab)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z" />
              </svg>
            </button>
          </div>
        )}

        {isAllDone && (
          <div style={{ textAlign: 'center', margin: '2rem 0' }}>
            <h2 style={{ fontSize: '1.8rem', color: '#10b981', marginBottom: '1rem' }}>🎉 Congratulations!</h2>
            <p style={{ color: 'var(--text-secondary)' }}>
              {appMode === 'review' ? 'You have completed all scheduled FSRS reviews!' : 'You have mastered all target words in this session!'}
            </p>
          </div>
        )}
        
        <div className="input-group">
          {isAllDone && (
            <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
              <div id="english-prompt" style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
                {appMode === 'review'
                  ? '🎉 All caught up!'
                  : stats.total === 0
                  ? (stats.inFsrsCount && stats.inFsrsCount > 0
                    ? '🎉 All words in this lesson are already in your FSRS review schedule, no initial study needed!'
                    : '📝 No Words Selected')
                  : '🎉 Session complete!'}
              </div>
              <div id="hint-display" style={{ color: '#94a3b8', fontSize: '1rem' }}>
                {appMode === 'review'
                  ? 'No reviews due right now.'
                  : stats.total === 0
                  ? (stats.inFsrsCount && stats.inFsrsCount > 0
                    ? 'You can review them in Review Mode when they become due.'
                    : 'All words for this article are excluded. Use Edit Mode (📖) in Narration to select words.')
                  : 'All words mastered for this article.'}
              </div>
            </div>
          )}

          {!isAllDone && !showAnswer && wrongCount >= 3 && exampleSentence && (
            <div id="sentence-hint-display" style={{ color: '#9ca3af', fontStyle: 'italic', marginBottom: '0.75rem', textAlign: 'center' }}>
              {getMaskedSentence()}
            </div>
          )}

          {!isAllDone && wrongCount >= 2 && status === 'typing' && enPrompt && (
            <div id="hint-display" style={{ color: '#9ca3af', fontStyle: 'italic', marginBottom: '0.5rem', textAlign: 'center' }}>
              Hint: {enPrompt}
            </div>
          )}
          {!isAllDone && (
            <input 
              ref={inputRef}
              autoFocus
              type="text" 
              id="spell-input" 
              className={`spell-input ${inputState === 'correct' ? 'correct' : (inputState === 'incorrect' ? 'incorrect' : '')}`}
              value={input} 
              onChange={e => { setInput(e.target.value); setInputState('default'); }} 
              onKeyDown={handleKeyDown}
              placeholder="Type here and hit Enter"
              disabled={showAnswer || isAdvancingRef.current}
              autoComplete="off"
              spellCheck="false"
            />
          )}
          
          {!isAllDone && !showAnswer && (
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
              <button 
                id="reveal-btn" 
                tabIndex={-1}
                className={`reveal-btn ${wrongCount >= 1 ? 'show' : ''}`}
                onClick={handleReveal}
              >
                Reveal Answer
              </button>
            </div>
          )}
          
          {!isAllDone && showAnswer && (
            <div id="answer-display" className="answer-display show">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                <strong className="correct-sv" id="correct-sv" onClick={playAudio} style={{ cursor: 'pointer' }} title="Play Audio (Tab)">
                  {currentWord?.word}
                </strong>
              </div>
              <span className="correct-en" id="correct-en">{enPrompt}</span>
              {exampleSentence && (
                <div 
                  id="sentence-display" 
                  style={{ 
                    marginTop: '1rem', 
                    padding: '12px 18px', 
                    background: 'rgba(255, 255, 255, 0.04)', 
                    borderRadius: '10px', 
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    textAlign: 'center' 
                  }}
                >
                  <div style={{ fontSize: '1.1rem', color: '#f1f5f9', lineHeight: 1.6, fontWeight: 500 }}>
                    {renderHighlightedSwedish(exampleSentence)}
                  </div>
                  {exampleSentenceEn && (
                    <div id="sentence-en-display" style={{ marginTop: '6px', fontSize: '0.95rem', color: '#94a3b8', lineHeight: 1.5, fontStyle: 'italic' }}>
                      {renderHighlightedEnglish(exampleSentenceEn)}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {!isAllDone && showAnswer && (
            <button tabIndex={-1} className="reveal-btn show" style={{ marginTop: '1.25rem' }} onClick={proceedToNext}>
              Next (Enter)
            </button>
          )}
        </div>
        
        <div id="timer-bar" className={`timer-bar ${!isAllDone && isAdvancingRef.current ? 'show' : ''}`}>
          <div id="timer-fill" className="timer-fill" style={{ width: timerFill }}></div>
        </div>
      </main>

      {appMode === 'review' && fsrsStats && (
        <div id="fsrs-review-stats" className="glass-panel">
          <div className="fsrs-stat-item"><span className="stat-val">{fsrsStats.totalStudied}</span><span className="stat-lbl">📚 Studied</span></div>
          <div className="fsrs-stat-item"><span className="stat-val" style={{ color: '#fbbf24' }}>{fsrsStats.learning}</span><span className="stat-lbl">🌱 Learning</span></div>
          <div className="fsrs-stat-item"><span className="stat-val" style={{ color: '#a3e635' }}>{fsrsStats.young}</span><span className="stat-lbl">🌿 Familiar</span></div>
          <div className="fsrs-stat-item"><span className="stat-val" style={{ color: '#4ade80' }}>{fsrsStats.mature}</span><span className="stat-lbl">🌳 Mastered</span></div>
          <div className="fsrs-stat-item"><span className="stat-val" style={{ color: '#60a5fa' }}>{fsrsStats.hitRate}%</span><span className="stat-lbl">🎯 Retention</span></div>
          <div className="fsrs-stat-item"><span className="stat-val" style={{ color: '#c084fc' }}>{fsrsStats.dueTomorrow}</span><span className="stat-lbl">📅 Tomorrow</span></div>
        </div>
      )}
    </div>
  );
}
