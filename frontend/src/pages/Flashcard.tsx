import { useState, useEffect, useRef, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { db } from '../db/dexie';
import { submitGatePass } from '../utils/fsrs';
import { getMp3PublicUrl } from '../services/r2';
import { useData } from '../contexts/DataContext';

export default function Flashcard() {
  const { courseId } = useParams();
  const { courseData, dictionary, loadCourse } = useData();
  const [queue, setQueue] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [input, setInput] = useState('');
  const [startTime, setStartTime] = useState(Date.now());
  const [appMode, setAppMode] = useState(localStorage.getItem('appMode') || 'study');
  const [wrongCount, setWrongCount] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const [selectedStage, setSelectedStage] = useState('');
  const [selectedArticleId, setSelectedArticleId] = useState('');
  const [inputState, setInputState] = useState<'default' | 'correct' | 'incorrect'>('default');
  const [timerFill, setTimerFill] = useState('0%');

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<any>(null);
  const intervalRef = useRef<any>(null);
  const nextWordTimeoutRunning = useRef(false);

  useEffect(() => {
    const handleModeChange = () => {
      setAppMode(localStorage.getItem('appMode') || 'study');
      setCurrentIndex(0);
      setWrongCount(0);
      setInput('');
      setShowAnswer(false);
      setInputState('default');
      setTimerFill('0%');
      nextWordTimeoutRunning.current = false;
      if (timerRef.current) clearTimeout(timerRef.current);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
    window.addEventListener('appModeChanged', handleModeChange);
    return () => window.removeEventListener('appModeChanged', handleModeChange);
  }, []);

  useEffect(() => {
    if (courseId) loadCourse(courseId);
  }, [courseId, loadCourse]);

  const stages = useMemo(() => {
    if (!courseData) return [];
    const baseStages = Object.keys(courseData).map(stageName => {
      const stageObj = courseData[stageName];
      return {
        id: stageName,
        title: stageName,
        articles: Object.keys(stageObj).map(articleTitle => ({
          id: articleTitle,
          title: articleTitle
        }))
      };
    });
    baseStages.push({ id: 'review', title: 'Review (Mistakes)', articles: [] });
    return baseStages;
  }, [courseData]);

  useEffect(() => {
    if (stages.length > 0 && !selectedStage) {
      setSelectedStage(stages[0]?.id || '');
      setSelectedArticleId(stages[0]?.articles?.[0]?.id || '');
    }
  }, [stages, selectedStage]);

  const handleStageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const stageId = e.target.value;
    setSelectedStage(stageId);
    const stage = stages.find(s => s.id === stageId);
    if (stage && stage.articles && stage.articles.length > 0) {
      setSelectedArticleId(stage.articles[0].id);
    } else {
      setSelectedArticleId('');
    }
  };

  const updateMasteryAndVocab = (wordId: string, isCorrect: boolean) => {
    let vb = JSON.parse(localStorage.getItem('vocabBook') || '[]');
    let mw = JSON.parse(localStorage.getItem('flashcardMasteredWords') || '[]');
    
    if (isCorrect) {
      vb = vb.filter((w: string) => w !== wordId);
      if (!mw.includes(wordId)) mw.push(wordId);
    } else {
      mw = mw.filter((w: string) => w !== wordId);
      if (!vb.includes(wordId)) vb.push(wordId);
    }
    
    localStorage.setItem('vocabBook', JSON.stringify(vb));
    localStorage.setItem('flashcardMasteredWords', JSON.stringify(mw));
  };

  const fetchQueue = async () => {
    setLoading(true);
    if (appMode === 'review') {
      const now = new Date();
      const records = await db.fsrs_progress.filter(r => {
        if (r.course_id && r.course_id !== courseId) return false;
        if (r.state === 0) return true; // new
        if (r.due > now) return false;
        if (r.todayFlashcardPassed) return false;
        return true;
      }).toArray();
      setQueue(records);
    } else {
      const mw = JSON.parse(localStorage.getItem('flashcardMasteredWords') || '[]');
      if (selectedStage === 'review') {
        const vb = JSON.parse(localStorage.getItem('vocabBook') || '[]');
        const queueItems = vb
          .filter((w: string) => !mw.includes(w))
          .map((w: string) => ({ word_id: w, en: '', sentence: '' }));
        setQueue(queueItems.sort(() => 0.5 - Math.random()));
      } else if (courseData && selectedStage && selectedArticleId) {
        const sentences = courseData[selectedStage]?.[selectedArticleId] || [];
        let sentsArray = sentences;
        if (!Array.isArray(sentences) && typeof sentences === 'object') {
          sentsArray = Object.keys(sentences).sort((a,b) => Number(a) - Number(b)).map(k => (sentences as any)[k]);
        }
        const wordsMap = new Map<string, { sentence: string, en: string }>();
        sentsArray.forEach((s: any) => {
          if (s.target_words) {
            s.target_words.forEach((w: any) => {
              const base = (w.base_form || w.word_in_sentence).toLowerCase();
              if (!wordsMap.has(base)) wordsMap.set(base, { sentence: s.sentence || s.sv, en: w.en || s.en || '' });
            });
          }
        });
        
        const queueItems = Array.from(wordsMap.entries())
          .filter(([w]) => !mw.includes(w))
          .map(([w, data]) => ({ word_id: w, en: data.en, sentence: data.sentence }));
        setQueue(queueItems.sort(() => 0.5 - Math.random()));
      } else {
        setQueue([]);
      }
    }
    setCurrentIndex(0);
    setLoading(false);
  };

  useEffect(() => {
    fetchQueue();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [appMode, courseData, courseId, selectedStage, selectedArticleId]);

  const handleResetProgress = () => {
    if (appMode !== 'study') return;
    
    const mw = JSON.parse(localStorage.getItem('flashcardMasteredWords') || '[]');
    let currentScopeWords: string[] = [];
    
    if (selectedStage === 'review') {
      currentScopeWords = JSON.parse(localStorage.getItem('vocabBook') || '[]');
    } else if (courseData && selectedStage && selectedArticleId) {
      const sentences = courseData[selectedStage]?.[selectedArticleId] || [];
      let sentsArray = sentences;
      if (!Array.isArray(sentences) && typeof sentences === 'object') {
        sentsArray = Object.keys(sentences).sort((a,b) => Number(a) - Number(b)).map(k => (sentences as any)[k]);
      }
      sentsArray.forEach((s: any) => {
        if (s.target_words) {
          s.target_words.forEach((w: any) => {
            currentScopeWords.push((w.base_form || w.word_in_sentence).toLowerCase());
          });
        }
      });
    }
    
    const newMw = mw.filter((w: string) => !currentScopeWords.includes(w));
    localStorage.setItem('flashcardMasteredWords', JSON.stringify(newMw));
    fetchQueue(); // refresh pool
  };

  const currentRecord = queue[currentIndex];
  
  const enPrompt = currentRecord?.en || dictionary?.[currentRecord?.word_id] || dictionary?.[Object.keys(dictionary || {}).find(k => k.toLowerCase() === currentRecord?.word_id?.toLowerCase()) || ''] || 'Custom Word';
  
  const currentWord = currentRecord ? { 
    id: currentRecord.word_id, 
    word: currentRecord.word_id, 
    definition: enPrompt,
    sentence: currentRecord.sentence,
    audio: `words_audio/${currentRecord.word_id}.mp3` 
  } : null;

  const playAudio = () => {
    if (currentWord?.audio) {
      const url = getMp3PublicUrl(currentWord.audio);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        audioRef.current.src = url;
        audioRef.current.play().catch(console.error);
      } else {
        const audio = new Audio(url);
        audioRef.current = audio;
        audio.play().catch(console.error);
      }
    }
  };

  const proceedToNext = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (intervalRef.current) clearInterval(intervalRef.current);
    nextWordTimeoutRunning.current = false;
    setWrongCount(0);
    setInput('');
    setShowAnswer(false);
    setInputState('default');
    setTimerFill('0%');
    setCurrentIndex(prev => prev + 1);
    setStartTime(Date.now());
  };

  const handleRate = async (rating: number) => {
    if (!currentWord || !courseId) return;
    const timeSpent = (Date.now() - startTime) / 1000;
    const res = await submitGatePass(courseId, currentWord.id, 'flashcard', wrongCount, timeSpent, true, rating);
    if (res.completed) {
      window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Rated: ${res.rating}` }));
    }
    proceedToNext();
  };
  
  const handleReveal = async () => {
    if (!currentWord || !courseId) return;
    setShowAnswer(true);
    setInputState('incorrect');
    if (appMode === 'study') {
      updateMasteryAndVocab(currentWord.id, false);
    }
    playAudio();
  };

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        if (wrongCount >= 2 || showAnswer) playAudio();
        return;
      }
      
      // Legacy audio replay
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault();
        playAudio();
        return;
      }
      
      // Legacy reveal / skip countdown
      if (e.key === 'Escape' || (e.key === '/' && e.metaKey)) {
        e.preventDefault();
        if (nextWordTimeoutRunning.current) {
          proceedToNext();
        } else if (!showAnswer) {
          handleReveal();
        }
        return;
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  });

  const handleKeyDown = async (e: React.KeyboardEvent) => {
    if (e.key === 'Tab' || e.key === 'Escape' || (e.key === '/' && e.metaKey)) {
      // Handled globally
      return;
    }

    if (!showAnswer && e.key === 'Enter') {
      e.preventDefault();
      if (!currentWord || !courseId) return;
      
      const isCorrect = input.toLowerCase().trim() === currentWord.word.toLowerCase();
      
      if (!isCorrect) {
        setWrongCount(prev => prev + 1);
        setInput('');
        setInputState('incorrect');
        if (appMode === 'study') {
          updateMasteryAndVocab(currentWord.id, false);
        }
        return;
      }

      setInputState('correct');
      const timeSpent = (Date.now() - startTime) / 1000;
      
      if (appMode === 'study') {
        updateMasteryAndVocab(currentWord.id, true);
        await submitGatePass(courseId, currentWord.id, 'flashcard', wrongCount, timeSpent, false, 0);
      } else {
        const res = await submitGatePass(courseId, currentWord.id, 'flashcard', wrongCount, timeSpent, false, 0);
        if (res.completed) {
          window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Rated: ${res.rating}` }));
        }
      }
      
      // Auto-Advance Timer
      const svLen = currentWord.word.length;
      const enLen = currentWord.definition.length;
      const delay = Math.max(1200, Math.min(8000, 1000 + (svLen + enLen) * 140));
      
      nextWordTimeoutRunning.current = true;
      let start = Date.now();
      
      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = setInterval(() => {
        const percent = ((Date.now() - start) / delay) * 100;
        setTimerFill(`${percent}%`);
      }, 16);
      
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        clearInterval(intervalRef.current);
        proceedToNext();
      }, delay);
      
      return;
    }
    
    if (showAnswer && e.key === 'Enter') {
      e.preventDefault();
      if (appMode !== 'review') proceedToNext();
      else handleRate(wrongCount > 0 ? 1 : 3);
      return;
    }

    if (showAnswer && appMode === 'review') {
      if (e.key === '1') { e.preventDefault(); handleRate(1); }
      if (e.key === '2') { e.preventDefault(); handleRate(2); }
      if (e.key === '3') { e.preventDefault(); handleRate(3); }
      if (e.key === '4') { e.preventDefault(); handleRate(4); }
    }
  };

  const getBorderColor = () => {
    if (inputState === 'correct') return 'var(--success, #28a745)';
    if (inputState === 'incorrect') return 'var(--error, #dc3545)';
    return 'var(--border)';
  };

  if (loading) return <div className="glass-panel view-container" style={{ padding: '48px', fontSize: '20px', textAlign: 'center' }}>Loading flashcards...</div>;
  if (!queue.length) return (
    <div className="glass-panel view-container" style={{ padding: '48px', fontSize: '20px', textAlign: 'center' }}>
      No cards available!
      {appMode === 'study' && (
        <div style={{ marginTop: '16px' }}>
          <button className="btn-primary" onClick={handleResetProgress}>Reset Progress</button>
        </div>
      )}
    </div>
  );
  if (currentIndex >= queue.length) return (
    <div className="glass-panel view-container" style={{ padding: '48px', fontSize: '20px', textAlign: 'center' }}>
      Session complete!
      {appMode === 'study' && (
        <div style={{ marginTop: '16px' }}>
          <button className="btn-primary" onClick={handleResetProgress}>Reset Progress</button>
        </div>
      )}
    </div>
  );

  const showSelectors = appMode === 'study' && stages.length > 0;

  return (
    <div className="glass-panel view-container" style={{ position: 'relative', overflow: 'hidden' }}>
      {nextWordTimeoutRunning.current && (
        <div style={{ position: 'absolute', top: 0, left: 0, height: '4px', background: 'var(--success, #28a745)', width: timerFill, transition: 'width 16ms linear' }}></div>
      )}
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {!showSelectors && <h3 style={{ margin: 0, fontSize: '24px' }}>Flashcard ({appMode})</h3>}
        {showSelectors && (
          <div style={{ display: 'flex', gap: '8px', width: '100%', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
              <select className="module-selector" value={selectedStage} onChange={handleStageChange}>
                <option value="review">Review Ready ({Math.max(0, Object.keys(dictionary || {}).length - JSON.parse(localStorage.getItem('flashcardMasteredWords') || '[]').length)})</option>
                {stages.map(s => <option key={s.id} value={s.id}>{s.title}</option>)}
              </select>
              {selectedStage !== 'review' && (
                <select className="module-selector" value={selectedArticleId} onChange={e => setSelectedArticleId(e.target.value)}>
                  {stages.find(s => s.id === selectedStage)?.articles?.map(a => <option key={a.id} value={a.id}>{a.title}</option>)}
                </select>
              )}
            </div>
            <button className="btn-primary" onClick={handleResetProgress} style={{ fontSize: '14px', padding: '6px 12px' }}>Reset Progress</button>
          </div>
        )}
      </div>
      <div className="flashcard-progress" style={{ marginTop: '16px' }}>Card {currentIndex + 1} of {queue.length}</div>
      
      <div style={{ padding: '32px 0', fontSize: '24px', fontWeight: 'bold', color: 'var(--text-h)' }}>
        {currentWord?.definition}
      </div>

      <input 
        autoFocus
        type="text" 
        value={input} 
        onChange={e => { setInput(e.target.value); setInputState('default'); }} 
        onKeyDown={handleKeyDown}
        placeholder="Translate to Swedish..."
        disabled={showAnswer || nextWordTimeoutRunning.current}
        style={{ 
          width: '100%', 
          padding: '16px', 
          fontSize: '24px', 
          borderRadius: '12px', 
          border: '2px solid', 
          textAlign: 'center', 
          borderColor: getBorderColor(),
          color: inputState === 'correct' ? 'var(--success, #28a745)' : (inputState === 'incorrect' ? 'var(--error, #dc3545)' : 'var(--text)'),
          marginBottom: '16px',
          outline: 'none'
        }}
      />
      
      {wrongCount >= 2 && !showAnswer && (
        <div style={{ color: 'var(--accent)', cursor: 'pointer', marginBottom: '8px', fontSize: '14px' }} onClick={playAudio}>
          🔊 Audio Hint (Press Tab)
        </div>
      )}
      {wrongCount >= 3 && !showAnswer && currentWord?.sentence && (
        <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', marginBottom: '16px' }}>
          {currentWord.sentence.replace(new RegExp(`(${currentWord.word})`, 'gi'), '_____')}
        </div>
      )}

      <div style={{ minHeight: '160px', width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        {!showAnswer ? (
          <button onClick={handleReveal} className="btn-primary" style={{ background: 'transparent', border: '1px solid var(--accent)', color: 'var(--accent)', maxWidth: '200px' }}>Reveal Answer</button>
        ) : (
          <div className="reveal-animation" style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div className="flashcard-word" onClick={playAudio} style={{ cursor: 'pointer', color: 'var(--accent)' }}>
              {currentWord?.word}
              <span className="flashcard-audio-hint" style={{ fontSize: '14px', marginLeft: '8px' }}>🔊</span>
            </div>
            
            <div style={{ marginTop: '24px', display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
              {appMode === 'review' ? (
                <>
                  <button className="btn-primary" style={{ background: 'var(--error)' }} onClick={() => handleRate(1)}>Again (1)</button>
                  <button className="btn-primary" style={{ background: 'var(--warning)' }} onClick={() => handleRate(2)}>Hard (2)</button>
                  <button className="btn-primary" style={{ background: 'var(--success)' }} onClick={() => handleRate(3)}>Good (3)</button>
                  <button className="btn-primary" style={{ background: 'var(--info)' }} onClick={() => handleRate(4)}>Easy (4)</button>
                </>
              ) : (
                <button className="btn-primary" onClick={proceedToNext}>Next</button>
              )}
            </div>
            <p style={{ color: 'var(--text)', fontStyle: 'italic', marginTop: '16px' }}>Press Enter to continue</p>
          </div>
        )}
      </div>
    </div>
  );
}
