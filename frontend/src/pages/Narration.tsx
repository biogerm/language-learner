import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useData } from '../contexts/DataContext';
import { getMp3PublicUrl } from '../services/r2';
import { db, type WordObject } from '../db/dexie';
import { global_dict } from '../data/global_dict';
import { playExactWordAudio } from '../utils/sound';

interface MissingVocabItem {
  sv: string;
  stage: string;
  article: string;
  course_id: string;
  sentence_id?: string;
  context_sv: string;
  context_en: string;
  user_en?: string;
  baseForm?: string;
  dictEn?: string;
}

interface CustomVocabEntry {
  sv: string;
  en: string;
  stage?: string;
  article?: string;
  course_id?: string;
  timestamp?: number;
  baseForm?: string;
  base_form?: string;
  word_in_sentence?: string;
  dictEn?: string;
  sentence_id?: string;
  sentence?: string;
  sentence_en?: string;
  context_sv?: string;
  context_en?: string;
  isGlobalTarget?: boolean;
  is_global_target?: boolean;
}

interface TokenState {
  token: string;
  cleanWord: string;
  cleanWordLower: string;
  isWord: boolean;
  type: 'target' | 'secondary' | 'custom' | 'plain';
  isSelected: boolean;
  isUnknown: boolean;
  initiallySelected: boolean;
  baseForm?: string;
  dictEn?: string;
  isGlobalTarget?: boolean;
  isInFsrs?: boolean;
}

export default function Narration() {
  const { courseId } = useParams();
  const { courseData, loadCourse, selectedStage, selectedArticleId, refreshLearningQueue, refreshCustomDictionary, refreshExcludedDictionary } = useData();
  const [loading, setLoading] = useState(false);
  const [hoverSyncId, setHoverSyncId] = useState<string | null>(null);

  const [activeIndex, setActiveIndex] = useState(0);
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  
  // Edit mode state
  const [editModeIndex, setEditModeIndex] = useState<number | null>(null);
  const [editingTokens, setEditingTokens] = useState<TokenState[]>([]);
  const [hasChanged, setHasChanged] = useState(false);

  // Excluded & Custom vocab state
  const [excludedVocab, setExcludedVocab] = useState<string[]>([]);
  const [customVocab, setCustomVocab] = useState<CustomVocabEntry[]>([]);
  const [fsrsVocab, setFsrsVocab] = useState<string[]>([]);

  // Missing Translation Modal State
  const [missingQueue, setMissingQueue] = useState<MissingVocabItem[]>([]);
  const [missingIndex, setMissingIndex] = useState<number | null>(null);
  const [missingInput, setMissingInput] = useState('');
  const [missingError, setMissingError] = useState('');

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const wordAudioRef = useRef<HTMLAudioElement | null>(null);
  const sentenceRefs = useRef<(HTMLElement | null)[]>([]);

  // Load excludedVocab, customVocab, and fsrsVocab from Dexie
  const loadVocabStorage = useCallback(async () => {
    try {
      const storedEx = await db.excluded_dictionary.toArray();
      setExcludedVocab(storedEx.map(r => r.base_form.toLowerCase()));
    } catch (e) {
      setExcludedVocab([]);
    }

    try {
      const activeCid = (courseId || 'sfid').toLowerCase();
      const allFsrs = await db.fsrs_progress.toArray();
      const activeFsrs = allFsrs.filter(r => (!r.course_id || r.course_id.toLowerCase() === activeCid) && r.state !== 0);
      setFsrsVocab(activeFsrs.map(r => (r.word_id || '').toLowerCase()));
    } catch (e) {
      setFsrsVocab([]);
    }

    try {
      const storedCustom = await db.custom_dictionary.toArray();
      setCustomVocab(storedCustom.map(r => ({
        sv: r.word_in_sentence || r.base_form,
        baseForm: r.base_form,
        base_form: r.base_form,
        word_in_sentence: r.word_in_sentence,
        dictEn: r.dict_en,
        en: r.en_translation,
        stage: r.stage_id,
        article: r.article_id,
        course_id: r.course_id,
        context_sv: r.sentence || r.context_sv,
        context_en: r.sentence_en || r.context_en,
        isGlobalTarget: !!r.is_global_target,
        timestamp: Date.now()
      })));
    } catch (e) {
      setCustomVocab([]);
    }
  }, [courseId]);

  useEffect(() => {
    loadVocabStorage();
  }, [loadVocabStorage]);

  useEffect(() => {
    if (courseId) {
      setLoading(true);
      loadCourse(courseId).finally(() => setLoading(false));
    }
  }, [courseId, loadCourse]);

  useEffect(() => {
    setActiveIndex(0);
    setEditModeIndex(null);
    setEditingTokens([]);
    setHasChanged(false);
  }, [selectedArticleId]);

  useEffect(() => {
    if (sentenceRefs.current[activeIndex]) {
      sentenceRefs.current[activeIndex]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [activeIndex]);

  const sentencesArray = useMemo(() => {
    if (!courseData || !selectedStage || !selectedArticleId) return [];

    if (courseData.stages && Array.isArray(courseData.stages)) {
      const stage = courseData.stages.find((s: any) => s.stage_id === selectedStage);
      if (!stage) return [];
      const article = stage.articles?.find((a: any) => a.article_id === selectedArticleId);
      return article?.sentences || [];
    }

    const stageData = courseData[selectedStage];
    if (!stageData) return [];
    let sentences = stageData[selectedArticleId] || [];
    if (!Array.isArray(sentences) && typeof sentences === 'object') {
      sentences = Object.keys(sentences)
        .sort((a, b) => Number(a) - Number(b))
        .map(k => sentences[k]);
    }
    return sentences;
  }, [courseData, selectedStage, selectedArticleId]);

  // Dictionary lookup helper strictly matching L
  const getKnownTranslation = useCallback((word: string): string => {
    if (!word) return '';
    const cleanW = word.toLowerCase();
    const globalEn = (global_dict as Record<string, string>)[cleanW];
    if (globalEn) return globalEn;

    // Check courseData lemma map -> global_dict
    if (courseData) {
      const stages: any[] = Array.isArray(courseData.stages) ? courseData.stages : [];
      for (const stage of stages) {
        for (const article of stage.articles || []) {
          for (const s of article.sentences || []) {
            const allMeta = [...(s.target_words || []), ...(s.secondary_words || [])];
            for (const tw of allMeta) {
              const inSent = (tw.word_in_sentence || '').toLowerCase();
              const base = (tw.base_form || '').toLowerCase();
              if (inSent === cleanW || base === cleanW) {
                if (base && (global_dict as Record<string, string>)[base]) {
                  return (global_dict as Record<string, string>)[base];
                }
              }
            }
          }
        }
      }
    }
    return '';
  }, [courseData]);

  const getKnownTranslationInfo = useCallback((word: string): { baseForm: string, dictEn: string, isGlobalTarget?: boolean } | null => {
    if (!word) return null;
    const cleanW = word.toLowerCase();

    if (courseData) {
      const stages: any[] = Array.isArray(courseData.stages) ? courseData.stages : [];
      for (const stage of stages) {
        for (const article of stage.articles || []) {
          for (const s of article.sentences || []) {
            const targets = s.target_words || [];
            for (const tw of targets) {
              const inSent = (tw.word_in_sentence || '').toLowerCase();
              const base = (tw.base_form || '').toLowerCase();
              if (inSent === cleanW || base === cleanW) {
                const en = tw.en_translation || tw.contextual_en || (base ? (global_dict as Record<string, string>)[base] : '');
                if (en) {
                  return { baseForm: base || cleanW, dictEn: en, isGlobalTarget: true };
                }
              }
            }
            const secondaries = s.secondary_words || [];
            for (const sw of secondaries) {
              const inSent = (sw.word_in_sentence || '').toLowerCase();
              const base = (sw.base_form || '').toLowerCase();
              if (inSent === cleanW || base === cleanW) {
                const en = sw.en_translation || sw.contextual_en || (base ? (global_dict as Record<string, string>)[base] : '');
                if (en) {
                  return { baseForm: base || cleanW, dictEn: en, isGlobalTarget: false };
                }
              }
            }
          }
        }
      }
    }

    const globalEn = (global_dict as Record<string, string>)[cleanW];
    if (globalEn) return { baseForm: cleanW, dictEn: globalEn, isGlobalTarget: false };

    return null;
  }, [courseData]);

  const stopPlayback = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    if (wordAudioRef.current) {
      wordAudioRef.current.pause();
      wordAudioRef.current.currentTime = 0;
    }
    setPlayingIndex(null);
  }, []);

  const playAudio = useCallback((audioPath: string, index?: number) => {
    stopPlayback();
    const idx = index !== undefined ? index : activeIndex;
    setPlayingIndex(idx);
    const url = getMp3PublicUrl(audioPath);
    const audio = new Audio(url);
    audioRef.current = audio;
    audio.onended = () => setPlayingIndex(null);
    audio.play().catch(console.error);
  }, [activeIndex, stopPlayback]);

  const playWordAudio = useCallback((word: string) => {
    playExactWordAudio(word);
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (editModeIndex !== null || missingIndex !== null) return;

      if (e.code === 'Space') {
        e.preventDefault();
        const nextIdx = e.shiftKey
          ? Math.max(activeIndex - 1, 0)
          : Math.min(activeIndex + 1, (sentencesArray?.length || 1) - 1);
        setActiveIndex(nextIdx);
        if (sentencesArray?.[nextIdx]) {
          const sId = sentencesArray[nextIdx].sentence_id || sentencesArray[nextIdx].id;
          playAudio(`sentences_audio/${sId}.mp3`, nextIdx);
        }
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (sentencesArray?.[activeIndex]) {
          const sId = sentencesArray[activeIndex].sentence_id || sentencesArray[activeIndex].id;
          playAudio(`sentences_audio/${sId}.mp3`, activeIndex);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [sentencesArray, activeIndex, playAudio, editModeIndex, missingIndex]);

  // Enter Edit Mode on a specific sentence
  // Enter Edit Mode on a specific sentence
  const enterEditMode = useCallback(async (sentenceIndex: number) => {
    stopPlayback();
    const sent = sentencesArray[sentenceIndex];
    if (!sent) return;

    let storedEx: string[] = [];
    try {
      const ex = await db.excluded_dictionary.toArray();
      storedEx = ex.map(r => r.base_form.toLowerCase());
    } catch (e) {}

    let storedFsrs: string[] = [];
    try {
      const activeCid = (courseId || 'sfid').toLowerCase();
      const allFsrs = await db.fsrs_progress.toArray();
      storedFsrs = allFsrs
        .filter(r => (!r.course_id || r.course_id.toLowerCase() === activeCid) && r.state !== 0)
        .map(r => (r.word_id || '').toLowerCase());
    } catch (e) {}

    let storedCustom: any[] = [];
    try {
      const cu = await db.custom_dictionary.toArray();
      storedCustom = cu.map(r => ({
        sv: (r.word_in_sentence || r.base_form || '').toLowerCase(),
        base_form: (r.base_form || '').toLowerCase(),
        word_in_sentence: (r.word_in_sentence || '').toLowerCase(),
        en: r.en_translation,
        stage: r.stage_id,
        article: r.article_id,
        course_id: r.course_id,
        is_global_target: !!r.is_global_target
      }));
    } catch (e) {}

    setExcludedVocab(storedEx);
    setFsrsVocab(storedFsrs);
    setCustomVocab(storedCustom.map(r => ({
      sv: r.word_in_sentence || r.base_form || r.sv,
      baseForm: r.base_form,
      en: r.en || '',
      stage: r.stage || selectedStage,
      article: r.article || selectedArticleId,
      course_id: r.course_id || courseId || 'sfid',
      isGlobalTarget: r.is_global_target,
      timestamp: Date.now()
    })));

    const rawTokens = sent.sv.split(/(\s+)/);
    const parsedTokens: TokenState[] = rawTokens.map((token: string) => {
      if (/^\s+$/.test(token) || token === '') {
        return {
          token,
          cleanWord: '',
          cleanWordLower: '',
          isWord: false,
          type: 'plain',
          isSelected: false,
          isUnknown: false,
          initiallySelected: false
        };
      }

      const cleanWord = token.replace(/[.,!?;:()[\]{}”"“‘’«»\-\…]/g, '').trim();
      if (!cleanWord) {
        return {
          token,
          cleanWord: '',
          cleanWordLower: '',
          isWord: false,
          type: 'plain',
          isSelected: false,
          isUnknown: false,
          initiallySelected: false
        };
      }

      const cleanWordLower = cleanWord.toLowerCase();

      const targetObj = sent.target_words?.find((tw: any) =>
        (tw.base_form && tw.base_form.toLowerCase() === cleanWordLower) ||
        (tw.word_in_sentence && tw.word_in_sentence.toLowerCase() === cleanWordLower)
      );
      const isTarget = !!targetObj;

      const secondaryObj = !isTarget && sent.secondary_words?.find((sw: any) =>
        (sw.base_form && sw.base_form.toLowerCase() === cleanWordLower) ||
        (sw.word_in_sentence && sw.word_in_sentence.toLowerCase() === cleanWordLower)
      );
      const isSecondary = !!secondaryObj;

      const customObj = storedCustom.find(cv => 
        cleanWordLower === cv.sv ||
        cleanWordLower === cv.base_form ||
        cleanWordLower === cv.word_in_sentence
      );
      const isCustom = !!customObj;

      if (isTarget) {
        const baseForm = targetObj?.base_form || cleanWord;
        const isExcluded = storedEx.includes(baseForm.toLowerCase()) || storedEx.includes(cleanWordLower);
        const isInFsrs = storedFsrs.includes(cleanWordLower) || storedFsrs.includes(baseForm.toLowerCase());
        const initiallySelected = !isExcluded;
        return {
          token,
          cleanWord,
          cleanWordLower,
          baseForm,
          isWord: true,
          type: 'target',
          isSelected: initiallySelected,
          isUnknown: false,
          initiallySelected,
          isInFsrs
        };
      } else if (isSecondary) {
        const baseForm = secondaryObj?.base_form || cleanWord;
        const isInFsrs = storedFsrs.includes(cleanWordLower) || storedFsrs.includes(baseForm.toLowerCase());
        const initiallySelected = isCustom;
        return {
          token,
          cleanWord,
          cleanWordLower,
          baseForm,
          isWord: true,
          type: 'secondary',
          isSelected: initiallySelected,
          isUnknown: false,
          initiallySelected,
          isInFsrs
        };
      } else if (isCustom) {
        const baseForm = customObj?.base_form || cleanWord;
        const isInFsrs = storedFsrs.includes(cleanWordLower) || storedFsrs.includes(baseForm.toLowerCase());
        return {
          token,
          cleanWord,
          cleanWordLower,
          baseForm,
          isWord: true,
          type: 'custom',
          isSelected: true,
          isUnknown: false,
          initiallySelected: true,
          isGlobalTarget: customObj?.is_global_target,
          isInFsrs
        };
      } else {
        const isInFsrs = storedFsrs.includes(cleanWordLower);
        return {
          token,
          cleanWord,
          cleanWordLower,
          isWord: true,
          type: 'plain',
          isSelected: false,
          isUnknown: false,
          initiallySelected: false,
          isInFsrs
        };
      }
    });

    setEditingTokens(parsedTokens);
    setEditModeIndex(sentenceIndex);
    setHasChanged(false);
  }, [sentencesArray, stopPlayback, selectedStage, selectedArticleId, courseId]);

  // Karaoke Animation on Entering Edit Mode (replicating L)
  useEffect(() => {
    if (editModeIndex === null) return;
    const container = sentenceRefs.current[editModeIndex];
    if (!container) return;

    const words = container.querySelectorAll('.selectable-word');
    words.forEach((w, i) => {
      const htmlEl = w as HTMLElement;
      const t = htmlEl.dataset.type;
      const isGlobal = htmlEl.dataset.isglobaltarget === 'true';
      if (t === 'target') {
        htmlEl.style.setProperty('--k-bg', 'var(--accent, #8b5cf6)');
        htmlEl.style.setProperty('--k-color', 'white');
        htmlEl.style.setProperty('--k-border', 'none');
      } else if (t === 'secondary') {
        htmlEl.style.setProperty('--k-bg', '#3b82f6');
        htmlEl.style.setProperty('--k-color', 'white');
        htmlEl.style.setProperty('--k-border', 'none');
      } else if (isGlobal) {
        htmlEl.style.setProperty('--k-bg', '#a855f7');
        htmlEl.style.setProperty('--k-color', 'white');
        htmlEl.style.setProperty('--k-border', '1px dashed #e9d5ff');
      } else if (t === 'custom') {
        htmlEl.style.setProperty('--k-bg', '#10b981');
        htmlEl.style.setProperty('--k-color', 'white');
        htmlEl.style.setProperty('--k-border', 'none');
      } else {
        htmlEl.style.setProperty('--k-bg', 'transparent');
        htmlEl.style.setProperty('--k-color', 'var(--text, #e2e8f0)');
        htmlEl.style.setProperty('--k-border', '1px dashed var(--text-mute, #94a3b8)');
      }

      htmlEl.style.animationDelay = `${i * 35}ms`;
      htmlEl.classList.remove('karaoke-anim');
      void htmlEl.offsetWidth;
      htmlEl.classList.add('karaoke-anim');
    });

    const totalDuration = words.length * 35 + 500;
    const timeoutId = window.setTimeout(() => {
      words.forEach(w => {
        const htmlEl = w as HTMLElement;
        htmlEl.classList.remove('karaoke-anim');
        htmlEl.style.animationDelay = '';
        htmlEl.style.removeProperty('--k-bg');
        htmlEl.style.removeProperty('--k-color');
        htmlEl.style.removeProperty('--k-border');
      });
    }, totalDuration);

    return () => clearTimeout(timeoutId);
  }, [editModeIndex]);

  // Click Word in Edit Mode (Strictly replicating L's logic)
  const handleWordClickInEdit = (tIdx: number) => {
    setEditingTokens(prev => {
      const updated = prev.map((t, idx) => {
        if (idx !== tIdx || !t.isWord) return t;

        if (t.type === 'target') {
          // Simply toggle selection on target word
          return { ...t, isSelected: !t.isSelected };
        } else if (t.type === 'secondary') {
          // Simply toggle selection on secondary word
          return { ...t, isSelected: !t.isSelected };
        } else if (t.type === 'custom') {
          // Simply toggle selection on custom word
          return { ...t, isSelected: !t.isSelected };
        } else {
          // Plain text word
          if (t.isSelected) {
            // Deselect completely
            return { ...t, isSelected: false, isUnknown: false, baseForm: undefined, dictEn: undefined, isGlobalTarget: undefined };
          } else {
            // Check known dictionary translation
            const info = getKnownTranslationInfo(t.cleanWord);
            if (info) {
              if (info.baseForm !== t.cleanWordLower) {
                // Inflected word -> do not auto-fill, force user to input contextual meaning
                return { ...t, isSelected: true, isUnknown: true, baseForm: info.baseForm, dictEn: info.dictEn, isGlobalTarget: info.isGlobalTarget };
              } else {
                // Exact match -> auto-fill
                return { ...t, isSelected: true, isUnknown: false, baseForm: info.baseForm, dictEn: info.dictEn, isGlobalTarget: info.isGlobalTarget };
              }
            } else {
              return { ...t, isSelected: true, isUnknown: true };
            }
          }
        }
      });

      // Check if anything changed compared to initialStates
      const changed = updated.some(t => t.isWord && t.isSelected !== t.initiallySelected);
      setHasChanged(changed);

      return updated;
    });
  };

  // Cancel Edit Mode
  const handleCancelEdit = () => {
    setEditModeIndex(null);
    setEditingTokens([]);
    setHasChanged(false);
  };

  // Save Vocab (Strictly replicating L's saveVocab)
  const handleSaveVocab = async () => {
    if (editModeIndex === null) return;
    const sent = sentencesArray[editModeIndex];
    if (!sent) return;

    const exInDb = await db.excluded_dictionary.toArray();
    let updatedEx = exInDb.map(r => r.base_form.toLowerCase());
    let updatedCustom = [...customVocab];
    const missingQueueItems: MissingVocabItem[] = [];

    const currentCourseId = courseId || 'sfid';
    const stage = selectedStage || '';
    const article = selectedArticleId || '';

    editingTokens.forEach(t => {
      if (!t.isWord) return;
      const cleanW = t.cleanWordLower;

      if (t.type === 'target') {
        const baseFormLower = (t.baseForm || t.cleanWord).toLowerCase();
        if (t.isSelected) {
          // Remove from excluded
          updatedEx = updatedEx.filter(v => v !== cleanW && v !== baseFormLower);
        } else {
          // Add to excluded
          if (!updatedEx.includes(baseFormLower)) {
            updatedEx.push(baseFormLower);
          }
          if (!updatedEx.includes(cleanW)) {
            updatedEx.push(cleanW);
          }
        }
      } else if (t.type === 'secondary') {
        const isGloballyCustom = updatedCustom.some(v => v.sv.toLowerCase() === cleanW);
        if (t.isSelected && !isGloballyCustom) {
          let sw = sent.secondary_words?.find((w: any) =>
            (w.base_form || '').toLowerCase() === cleanW || (w.word_in_sentence || '').toLowerCase() === cleanW
          );
          const contextual = sw?.contextual_en || '';
          const globalEn = getKnownTranslation(cleanW);

          let translationStr = '';
          if (contextual && globalEn && contextual !== globalEn) translationStr = `${contextual} (${globalEn})`;
          else if (contextual) translationStr = contextual;
          else translationStr = globalEn || 'No translation';

          updatedCustom.push({
            sv: t.cleanWord,
            baseForm: t.baseForm || t.cleanWord,
            base_form: t.baseForm || t.cleanWord,
            word_in_sentence: t.cleanWord,
            en: translationStr,
            stage,
            article,
            course_id: currentCourseId,
            sentence_id: sent.sentence_id || sent.id || '',
            sentence: sent.sv,
            sentence_en: sent.en || '',
            context_sv: sent.sv,
            context_en: sent.en || '',
            timestamp: Date.now()
          });
        } else if (!t.isSelected) {
          updatedCustom = updatedCustom.filter(v => v.sv.toLowerCase() !== cleanW);
        }
      } else if (t.type === 'custom') {
        if (!t.isSelected) {
          updatedCustom = updatedCustom.filter(v => 
            v.sv.toLowerCase() !== cleanW && 
            (v.word_in_sentence || '').toLowerCase() !== cleanW &&
            (v.baseForm || v.base_form || '').toLowerCase() !== cleanW
          );
        }
      } else {
        // Plain word
        const isGloballyCustom = updatedCustom.some(v => 
          v.sv.toLowerCase() === cleanW ||
          (v.word_in_sentence || '').toLowerCase() === cleanW ||
          (v.baseForm || v.base_form || '').toLowerCase() === cleanW
        );
        if (t.isSelected && !isGloballyCustom) {
          if (t.isUnknown) {
            // Missing translation or inflected word -> queue for user input modal
            missingQueueItems.push({
              sv: t.cleanWord,
              stage,
              article,
              course_id: currentCourseId,
              sentence_id: sent.sentence_id || sent.id || '',
              context_sv: sent.sv,
              context_en: sent.en || '',
              baseForm: t.baseForm,
              dictEn: t.dictEn
            });
          } else {
            // Exact match known translation
            updatedCustom.push({
              sv: t.cleanWord,
              en: t.dictEn || getKnownTranslation(cleanW),
              stage,
              article,
              course_id: currentCourseId,
              timestamp: Date.now(),
              baseForm: t.baseForm,
              base_form: t.baseForm,
              word_in_sentence: t.cleanWord,
              dictEn: t.dictEn,
              sentence_id: sent.sentence_id || sent.id || '',
              sentence: sent.sv,
              sentence_en: sent.en || '',
              context_sv: sent.sv,
              context_en: sent.en || '',
              isGlobalTarget: t.isGlobalTarget
            });
          }
        } else if (!t.isSelected) {
          updatedCustom = updatedCustom.filter(v => 
            v.sv.toLowerCase() !== cleanW &&
            (v.word_in_sentence || '').toLowerCase() !== cleanW &&
            (v.baseForm || v.base_form || '').toLowerCase() !== cleanW
          );
        }
      }
    });

    // Save excluded and custom vocab
    setExcludedVocab(updatedEx);
    setCustomVocab(updatedCustom);

    // Sync to Dexie excluded_dictionary, custom_dictionary & clean up excluded words from learning_queue
    try {
      await db.transaction('rw', [db.excluded_dictionary, db.custom_dictionary, db.learning_queue], async () => {
        // Excluded words: Add new
        const allExInDb = await db.excluded_dictionary.toArray();
        const existingExSet = new Set(allExInDb.map(r => r.base_form.toLowerCase()));
        for (const exWord of updatedEx) {
          if (!existingExSet.has(exWord.toLowerCase())) {
            await db.excluded_dictionary.add({
              base_form: exWord.toLowerCase(),
              article_id: selectedArticleId,
              course_id: currentCourseId,
              synced: false
            });
          }
        }
        // Excluded words: Remove unexcluded
        for (const rec of allExInDb) {
          if (!updatedEx.includes(rec.base_form.toLowerCase()) && rec.id) {
            await db.excluded_dictionary.delete(rec.id);
          }
        }

        // Custom words: Add new
        const currentCustomInDb = await db.custom_dictionary.where('article_id').equals(selectedArticleId).toArray();
        for (const item of updatedCustom) {
          const baseFormToSave = item.baseForm || item.base_form || item.sv;
          const wordInSentenceToSave = item.word_in_sentence || item.sv;
          const existing = currentCustomInDb.find(c => 
            (c.base_form && c.base_form.toLowerCase() === baseFormToSave.toLowerCase()) ||
            (c.word_in_sentence && c.word_in_sentence.toLowerCase() === wordInSentenceToSave.toLowerCase())
          );
          if (!existing) {
            await db.custom_dictionary.add({
              base_form: baseFormToSave,
              word_in_sentence: wordInSentenceToSave,
              en_translation: item.en,
              dict_en: item.dictEn,
              article_id: item.article || article,
              stage_id: item.stage || stage,
              course_id: item.course_id || currentCourseId,
              sentence_id: sent.sentence_id || sent.id || '',
              sentence: sent.sv,
              sentence_en: sent.en || '',
              is_global_target: item.isGlobalTarget || false,
              synced: false
            } as unknown as WordObject);
          }
        }
        // Custom words: Delete unselected
        const updatedCustomSvSet = new Set(updatedCustom.map(c => c.sv.toLowerCase()));
        const updatedCustomBaseSet = new Set(updatedCustom.map(c => (c.baseForm || c.base_form || c.sv).toLowerCase()));
        const updatedCustomInSentSet = new Set(updatedCustom.map(c => (c.word_in_sentence || c.sv).toLowerCase()));
        for (const ec of currentCustomInDb) {
          const ecBase = (ec.base_form || '').toLowerCase();
          const ecInSent = (ec.word_in_sentence || '').toLowerCase();
          const isRetained = 
            (ecBase && (updatedCustomBaseSet.has(ecBase) || updatedCustomSvSet.has(ecBase) || updatedCustomInSentSet.has(ecBase))) ||
            (ecInSent && (updatedCustomInSentSet.has(ecInSent) || updatedCustomSvSet.has(ecInSent) || updatedCustomBaseSet.has(ecInSent)));
          if (!isRetained && ec.id) {
            await db.custom_dictionary.delete(ec.id);
          }
        }

        // Clean up excluded or unselected words from learning_queue for this article
        const articleLq = await db.learning_queue.where('article_id').equals(selectedArticleId).toArray();
        for (const item of articleLq) {
          const base = (item.base_form || '').toLowerCase();
          const inSent = (item.word_in_sentence || '').toLowerCase();
          const isEx = updatedEx.includes(base) || (inSent && updatedEx.includes(inSent));
          const isCustom = updatedCustomBaseSet.has(base) || updatedCustomSvSet.has(base) || updatedCustomInSentSet.has(inSent);
          
          let isTargetInCourse = false;
          if (courseData && (courseData as any).stages) {
            const currentArt = (courseData as any).stages.flatMap((s: any) => s.articles || []).find((a: any) => a.article_id === selectedArticleId);
            if (currentArt) {
              isTargetInCourse = (currentArt.sentences || []).some((s: any) =>
                (s.target_words || []).some((tw: any) => (tw.base_form || '').toLowerCase() === base || (tw.word_in_sentence || '').toLowerCase() === inSent)
              );
            }
          }

          if (isEx || (!isCustom && !isTargetInCourse)) {
            if (item.id) await db.learning_queue.delete(item.id);
          }
        }
      });
    } catch (e) {
      console.warn('Error syncing custom/excluded vocab to Dexie:', e);
    }

    if (missingQueueItems.length > 0) {
      setMissingQueue(missingQueueItems);
      setMissingIndex(0);
      setMissingInput('');
      setMissingError('');
    } else {
      window.dispatchEvent(new CustomEvent('fsrs-toast', { detail: 'Vocabulary updated' }));
      await loadVocabStorage();
      refreshCustomDictionary();
      refreshExcludedDictionary();
      refreshLearningQueue();
    }

    setEditModeIndex(null);
    setEditingTokens([]);
    setHasChanged(false);
  };

  // Missing Translation Modal Submit
  const handleMissingSubmit = async () => {
    if (missingIndex === null || !missingQueue[missingIndex]) return;
    const val = missingInput.trim();
    if (!val) {
      setMissingError('Translation cannot be empty. Please enter a translation.');
      return;
    }

    const currentItem = missingQueue[missingIndex];
    currentItem.user_en = val;

    const nextIndex = missingIndex + 1;
    if (nextIndex < missingQueue.length) {
      setMissingIndex(nextIndex);
      setMissingInput('');
      setMissingError('');
    } else {
      // Completed all missing translations
      let finalCustom = [...customVocab];

      for (const item of missingQueue) {
        if (item.user_en && !finalCustom.some(v => v.sv.toLowerCase() === item.sv.toLowerCase())) {
          finalCustom.push({
            sv: item.sv,
            baseForm: item.baseForm,
            base_form: item.baseForm,
            word_in_sentence: item.sv,
            dictEn: item.dictEn,
            en: item.user_en,
            stage: item.stage,
            article: item.article,
            course_id: item.course_id,
            sentence_id: item.sentence_id || '',
            sentence: item.context_sv,
            sentence_en: item.context_en || '',
            context_sv: item.context_sv,
            context_en: item.context_en || '',
            timestamp: Date.now()
          });

          // Add to Dexie custom_dictionary
          try {
            await db.custom_dictionary.add({
              base_form: item.baseForm || item.sv,
              word_in_sentence: item.sv,
              en_translation: item.user_en,
              dict_en: item.dictEn,
              article_id: item.article,
              stage_id: item.stage,
              course_id: item.course_id,
              sentence_id: item.sentence_id || '',
              sentence: item.context_sv,
              sentence_en: item.context_en,
              synced: false
            } as unknown as WordObject);
          } catch (e) {}
        }
      }

      setCustomVocab(finalCustom);
      window.dispatchEvent(new CustomEvent('fsrs-toast', { detail: '🎉 Added to vocabulary book!' }));
      refreshLearningQueue();

      setMissingQueue([]);
      setMissingIndex(null);
      setMissingInput('');
      setMissingError('');
      loadVocabStorage();
    }
  };

  // Extract and position words for Reading Mode (Swedish & English)
  const getSentenceWords = (sent: any, sentIdx: number) => {
    const svText = sent.sv || '';
    let allWords: any[] = [];

    if (sent.target_words) {
      allWords.push(...sent.target_words.map((w: any) => ({ ...w, type: 'target' })));
    }
    if (sent.secondary_words) {
      allWords.push(...sent.secondary_words.map((sw: any) => {
        const isCustom = customVocab.some(cv => {
          const cleanCv = (cv.sv || '').toLowerCase();
          const cleanBase = (cv.baseForm || cv.base_form || '').toLowerCase();
          const cleanInSent = (cv.word_in_sentence || '').toLowerCase();
          const targetW = (sw.base_form || sw.word_in_sentence || '').toLowerCase();
          return targetW === cleanCv || targetW === cleanBase || targetW === cleanInSent;
        });
        return {
          ...sw,
          type: 'secondary',
          isSelectedSecondary: isCustom
        };
      }));
    }

    // Filter out excluded target words and words already in active FSRS review schedule
    allWords = allWords.filter(w => {
      const base = (w.base_form || '').toLowerCase();
      const inSent = (w.word_in_sentence || '').toLowerCase();
      if (w.type === 'target') {
        const isEx = (base && excludedVocab.includes(base)) || (inSent && excludedVocab.includes(inSent));
        const isInFsrs = (base && fsrsVocab.includes(base)) || (inSent && fsrsVocab.includes(inSent));
        return !isEx && !isInFsrs;
      }
      return true;
    });

    // Custom vocab words that belong to this article/sentence (plain words added by user)
    customVocab.forEach(cv => {
      const cleanCv = (cv.sv || '').toLowerCase();
      const cleanWordInSent = (cv.word_in_sentence || '').toLowerCase();
      const cleanBase = (cv.base_form || cv.baseForm || '').toLowerCase();
      const alreadyIn = allWords.some(w => {
        const targetW = (w.base_form || w.word_in_sentence || '').toLowerCase();
        return targetW === cleanCv || targetW === cleanWordInSent || targetW === cleanBase;
      });
      if (!alreadyIn) {
        const searchWords = [cv.word_in_sentence, cv.base_form, cv.baseForm, cv.sv].filter(Boolean) as string[];
        const uniqueSearchWords = Array.from(new Set(searchWords));
        for (const searchWord of uniqueSearchWords) {
          const escaped = searchWord.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
          const regex = new RegExp(`(?<![\\p{L}\\p{N}])${escaped}(?![\\p{L}\\p{N}])`, 'gui');
          let match;
          while ((match = regex.exec(svText)) !== null) {
            const start = match.index;
            const end = match.index + match[0].length;
            const overlaps = allWords.some(w => w.position_start !== undefined && w.position_end !== undefined && !(end <= w.position_start || start >= w.position_end));
            if (!overlaps) {
              allWords.push({
                base_form: cv.baseForm || cv.base_form || cv.sv,
                word_in_sentence: match[0],
                contextual_en: cv.en || '',
                position_start: start,
                position_end: end,
                type: (cv.isGlobalTarget || cv.is_global_target) ? 'global_target' : 'custom'
              });
            }
          }
        }
      }
    });

    // Resolve positions for any words missing position_start/position_end
    const positionedWords: any[] = [];
    allWords.forEach(w => {
      if (w.position_start !== undefined && w.position_end !== undefined) {
        positionedWords.push(w);
      } else {
        const searchWord = w.word_in_sentence || w.base_form || '';
        if (searchWord) {
          const escaped = searchWord.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
          const regex = new RegExp(`(?<![\\p{L}\\p{N}])${escaped}(?![\\p{L}\\p{N}])`, 'gui');
          const match = regex.exec(svText);
          if (match) {
            positionedWords.push({
              ...w,
              position_start: match.index,
              position_end: match.index + match[0].length
            });
          }
        }
      }
    });

    positionedWords.sort((a, b) => a.position_start - b.position_start);
    positionedWords.forEach((w, idx) => {
      w._syncId = `sync-${sent.sentence_id || sent.id || sentIdx}-${idx}`;
    });

    return positionedWords;
  };

  // Render Swedish text with highlights in Reading Mode (matching L)
  const renderReadingSwedish = (sent: any, sentIdx: number, positionedWords: any[]) => {
    const svText = sent.sv || '';

    if (positionedWords.length > 0) {
      const chunks: React.ReactNode[] = [];
      let currentIndex = 0;

      positionedWords.forEach((w, idx) => {
        if (w.position_start >= currentIndex) {
          if (w.position_start > currentIndex) {
            chunks.push(<span key={`txt_${currentIndex}`}>{svText.substring(currentIndex, w.position_start)}</span>);
          }
          const exactWord = svText.substring(w.position_start, w.position_end);
          const baseWord = w.base_form || exactWord;
          const syncId = w._syncId || `sync-${sent.sentence_id || sent.id || sentIdx}-${idx}`;

          let cls = 'vocab-word';
          if (w.type === 'target') cls += ' target-word';
          else if (w.type === 'secondary') {
            cls += ' secondary-word';
            if (w.isSelectedSecondary) cls += ' selected-secondary-word';
          } else if (w.type === 'global_target') cls += ' global-target-word';
          else if (w.type === 'custom') cls += ' custom-word';
          if (hoverSyncId === syncId) cls += ' hover-sync';

          chunks.push(
            <span
              key={`w_${idx}_${currentIndex}`}
              className={cls}
              data-word={encodeURIComponent(baseWord)}
              data-sync-id={syncId}
              onMouseEnter={() => setHoverSyncId(syncId)}
              onMouseLeave={() => setHoverSyncId(null)}
              onClick={(e) => {
                e.stopPropagation();
                playWordAudio(baseWord);
              }}
            >
              {exactWord}
            </span>
          );
          currentIndex = w.position_end;
        }
      });

      if (currentIndex < svText.length) {
        chunks.push(<span key={`txt_end_${currentIndex}`}>{svText.substring(currentIndex)}</span>);
      }

      return chunks;
    } else {
      return <span>{svText}</span>;
    }
  };

  // Render English translation with highlights matching L
  const renderReadingEnglish = (sent: any, _sentIdx: number, positionedWords: any[]) => {
    let enText = sent.en || '';
    if (!enText) return null;

    const enWords = positionedWords
      .filter(w => w.contextual_en)
      .sort((a, b) => b.contextual_en.length - a.contextual_en.length);

    if (enWords.length === 0) {
      return <span>{enText}</span>;
    }

    type EnToken = { token: string; word: any; matchText: string };
    const tokens: EnToken[] = [];

    enWords.forEach((w, idx) => {
      const escaped = w.contextual_en.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
      let regex = new RegExp(`\\b${escaped}\\b`, 'i');
      if (!regex.test(enText)) {
        regex = new RegExp(escaped, 'i');
      }
      const match = enText.match(regex);
      if (match) {
        const token = `__TOKEN_${idx}__`;
        tokens.push({ token, word: w, matchText: match[0] });
        enText = enText.replace(regex, token);
      }
    });

    const parts: string[] = enText.split(/(__TOKEN_\d+__)/g);
    return (
      <>
        {parts.map((part: string, pIdx: number) => {
          const tok = tokens.find(t => t.token === part);
          if (tok) {
            const w = tok.word;
            const syncId = w._syncId;
            let cls = `vocab-word ${w.type}-word en-word`;
            if (w.type === 'secondary' && w.isSelectedSecondary) cls += ' selected-secondary-word';
            if (w.type === 'global_target') cls += ' global-target-word';
            if (hoverSyncId === syncId) cls += ' hover-sync';
            return (
              <span
                key={pIdx}
                className={cls}
                data-sync-id={syncId}
                onMouseEnter={() => setHoverSyncId(syncId)}
                onMouseLeave={() => setHoverSyncId(null)}
              >
                {tok.matchText}
              </span>
            );
          }
          return <span key={pIdx}>{part}</span>;
        })}
      </>
    );
  };

  return (
    <div className="glass-panel" style={{ width: '100%', maxWidth: '800px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {loading ? (
        <p>Loading article...</p>
      ) : sentencesArray.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ marginBottom: '16px' }}>
            <h2 style={{ margin: 0, color: 'var(--text-h, #ffffff)' }}>
              {(() => {
                const title = courseData?.stages?.find((s: any) => s.stage_id === selectedStage)?.articles?.find((a: any) => a.article_id === selectedArticleId)?.article_title;
                return title ? `${selectedArticleId} - ${title}` : (selectedArticleId || 'Article');
              })()}
            </h2>
          </div>

          {sentencesArray.map((sent: any, i: number) => {
            const isActive = i === activeIndex;
            const isEditing = editModeIndex === i;
            const isPlaying = playingIndex === i;
            const sentWords = !isEditing ? getSentenceWords(sent, i) : [];

            return (
              <article
                className={`sentence-card ${isPlaying ? 'playing' : ''} ${isEditing ? 'edit-mode' : ''}`}
                key={sent.id || sent.sentence_id || `sent_${i}`}
                ref={el => { sentenceRefs.current[i] = el; }}
                style={{
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  padding: '16px',
                  border: isActive ? '2px solid var(--accent, #8b5cf6)' : '1px solid var(--border, rgba(255,255,255,0.1))',
                  borderRadius: '12px',
                  background: isActive ? 'rgba(139, 92, 246, 0.08)' : 'var(--glass-bg, rgba(15, 23, 42, 0.6))',
                  transition: 'all 0.2s ease',
                  cursor: isEditing ? 'default' : 'pointer'
                }}
                onClick={(e) => {
                  if (isEditing) return;
                  if ((e.target as HTMLElement).closest('.vocab-word') || (e.target as HTMLElement).closest('.extract-vocab-btn')) {
                    return;
                  }
                  if (isPlaying) {
                    stopPlayback();
                  } else {
                    setActiveIndex(i);
                    const sId = sent.sentence_id || sent.id;
                    playAudio(`sentences_audio/${sId}.mp3`, i);
                  }
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  {!isEditing ? (
                    <div style={{ margin: 0, marginBottom: '0.5rem', fontSize: '1.4rem', fontWeight: 600, lineHeight: '1.6', color: 'var(--text-h, #ffffff)', paddingRight: '40px' }}>
                      {renderReadingSwedish(sent, i, sentWords)}
                    </div>
                  ) : (
                    /* Edit Mode Word Selection (Replicating L) */
                    <div style={{ margin: 0, marginBottom: '0.5rem', fontSize: '1.4rem', fontWeight: 600, lineHeight: '1.6', color: 'var(--text-h, #ffffff)', paddingRight: '40px' }}>
                      {editingTokens.map((t, tIdx) => {
                        if (!t.isWord) {
                          return <span key={tIdx}>{t.token}</span>;
                        }

                        let cls = 'selectable-word';
                        if (t.type === 'secondary') cls += ' secondary-word';
                        if (t.isSelected) {
                          if (t.type === 'target') cls += ' selected-word';
                          else if (t.type === 'secondary') cls += ' selected-secondary-word';
                          else if (t.isGlobalTarget) cls += ' selected-global-target-word';
                          else if (t.type === 'custom') cls += ' selected-custom-word';
                          else if (t.isUnknown) cls += ' selected-unknown-word';
                          else cls += ' selected-custom-word';
                        }

                        return (
                          <span
                            key={tIdx}
                            className={cls}
                            data-word={t.cleanWord}
                            data-type={t.type}
                            data-isglobaltarget={t.isGlobalTarget ? 'true' : 'false'}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleWordClickInEdit(tIdx);
                            }}
                          >
                            {t.token}
                            {t.isInFsrs && (
                              <span
                                className="fsrs-review-badge"
                                title="Already in FSRS review schedule"
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  fontSize: '0.7em',
                                  padding: '1px 3px',
                                  marginLeft: '2px',
                                  borderRadius: '3px',
                                  backgroundColor: 'rgba(34, 197, 94, 0.25)',
                                  color: '#4ade80',
                                  border: '1px solid rgba(34, 197, 94, 0.4)',
                                  verticalAlign: 'super',
                                  lineHeight: 1,
                                  fontWeight: 'bold'
                                }}
                              >
                                ✓
                              </span>
                            )}
                          </span>
                        );
                      })}
                    </div>
                  )}

                  {!isEditing ? (
                    <button
                      className="extract-vocab-btn"
                      title="Edit Vocabulary"
                      style={{
                        background: 'transparent',
                        border: 'none',
                        fontSize: '1.3rem',
                        cursor: 'pointer',
                        padding: '4px 8px',
                        borderRadius: '6px',
                        transition: 'transform 0.2s',
                        lineHeight: 1
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        enterEditMode(i);
                      }}
                    >
                      📖
                    </button>
                  ) : null}
                </div>

                {sent.en && !isEditing && (
                  <p
                    className="english-text"
                    style={{
                      margin: 0,
                      marginTop: '0.4rem',
                      fontSize: '1.15rem',
                      color: 'var(--text-mute, #94a3b8)',
                      lineHeight: '1.6',
                      fontStyle: 'italic'
                    }}
                  >
                    {renderReadingEnglish(sent, i, sentWords)}
                  </p>
                )}

                {isEditing && (
                  <div style={{ marginTop: '12px', display: 'flex', gap: '12px', alignItems: 'center' }}>
                    {hasChanged && (
                      <button
                        className="save-vocab-btn"
                        style={{
                          backgroundColor: 'var(--accent, #8b5cf6)',
                          color: 'white',
                          border: 'none',
                          padding: '8px 18px',
                          borderRadius: '20px',
                          fontSize: '0.9rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          boxShadow: '0 4px 12px rgba(139, 92, 246, 0.4)',
                          transition: 'all 0.2s ease'
                        }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSaveVocab();
                        }}
                      >
                        Save Changes
                      </button>
                    )}
                    <button
                      className="cancel-edit-btn"
                      style={{
                        background: 'transparent',
                        color: 'var(--text-mute, #94a3b8)',
                        border: 'none',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        fontSize: '0.9rem'
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCancelEdit();
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}

      {/* Missing Translation Step-by-Step Modal (Replicating L) */}
      {missingIndex !== null && missingQueue[missingIndex] && (
        <div
          className="learning-overlay"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10001
          }}
        >
          <div
            className="learning-modal glass-panel"
            style={{
              position: 'relative',
              width: '450px',
              maxWidth: '90vw',
              padding: '28px',
              borderRadius: '16px',
              background: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid var(--accent, #8b5cf6)',
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)'
            }}
          >
            <button
              onClick={() => {
                setMissingQueue([]);
                setMissingIndex(null);
              }}
              style={{
                position: 'absolute',
                top: '12px',
                right: '12px',
                background: 'transparent',
                border: 'none',
                color: '#cbd5e1',
                fontSize: '1.2rem',
                cursor: 'pointer'
              }}
            >
              ✕
            </button>

            <h3 style={{ margin: 0, color: 'var(--accent, #8b5cf6)', fontSize: '1.2rem' }}>
              Missing Translation ({missingIndex + 1}/{missingQueue.length})
            </h3>

            <div style={{ fontSize: '2rem', fontWeight: 700, margin: '1rem 0', textAlign: 'center', color: '#ffffff' }}>
              {missingQueue[missingIndex].sv}
            </div>

            <p style={{ fontSize: '1.05rem', lineHeight: '1.5', marginBottom: '0.5rem', color: '#e2e8f0' }}>
              {missingQueue[missingIndex].context_sv}
            </p>

            {missingQueue[missingIndex].context_en && (
              <p style={{ color: '#9ca3af', fontSize: '0.95rem', marginBottom: '1.5rem', fontStyle: 'italic' }}>
                {missingQueue[missingIndex].context_en}
              </p>
            )}

            {missingQueue[missingIndex].baseForm && missingQueue[missingIndex].dictEn && (
              <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '8px', padding: '12px', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#60a5fa', fontWeight: 600, marginBottom: '4px' }}>
                  <span style={{ fontSize: '1.1rem' }}>💡</span> Dictionary Reference
                </div>
                <div style={{ color: '#e2e8f0', fontSize: '0.95rem' }}>
                  Base form: <strong style={{ color: '#ffffff' }}>{missingQueue[missingIndex].baseForm}</strong> — "{missingQueue[missingIndex].dictEn}"
                </div>
              </div>
            )}

            <input
              type="text"
              placeholder={missingQueue[missingIndex].baseForm ? "Enter contextual translation for this sentence" : "Type English translation here..."}
              value={missingInput}
              onChange={(e) => {
                setMissingInput(e.target.value);
                setMissingError('');
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleMissingSubmit();
              }}
              autoFocus
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '1rem',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                background: 'rgba(0, 0, 0, 0.3)',
                color: 'white',
                marginBottom: '1rem',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />

            <button
              onClick={handleMissingSubmit}
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '1rem',
                fontWeight: 600,
                background: 'var(--accent, #8b5cf6)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              Save Translation
            </button>

            {missingError && (
              <div style={{ color: '#ef4444', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                {missingError}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

