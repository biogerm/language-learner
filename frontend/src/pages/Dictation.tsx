import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { db } from '../db/dexie';
import { submitGatePass } from '../utils/fsrs';
import { getMp3PublicUrl } from '../services/r2';
import { useData } from '../contexts/DataContext';

export default function Dictation() {
  const { courseId } = useParams();
  const { courseData, loadCourse, selectedStage, selectedArticleId } = useData();
  const [queue, setQueue] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [input, setInput] = useState('');
  const [startTime, setStartTime] = useState(Date.now());
  const [appMode, setAppMode] = useState(localStorage.getItem('appMode') || 'study');
  const [wrongCount, setWrongCount] = useState(0);
  
  // Status: 'typing' | 'correct' | 'revealed'
  const [status, setStatus] = useState<'typing' | 'correct' | 'revealed'>('typing');
  const [feedbackMsg, setFeedbackMsg] = useState('');
  
  const [loading, setLoading] = useState(true);

  const [stats, setStats] = useState({ total: 0, mastered: 0, remaining: 0 });
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    const handleModeChange = () => {
      setAppMode(localStorage.getItem('appMode') || 'study');
      setCurrentIndex(0);
      setWrongCount(0);
      setInput('');
      setStatus('typing');
      setFeedbackMsg('');
      if (timerRef.current) clearTimeout(timerRef.current);
    };
    window.addEventListener('appModeChanged', handleModeChange);
    return () => window.removeEventListener('appModeChanged', handleModeChange);
  }, []);

  useEffect(() => {
    if (courseId) loadCourse(courseId);
  }, [courseId, loadCourse]);

  useEffect(() => {
    const fetchQueue = async () => {
      setLoading(true);
      if (appMode === 'review') {
        const now = new Date();
        const records = await db.fsrs_progress.filter(r => {
          if (r.course_id && r.course_id !== courseId) return false;
          if (r.state === 0) return true; // new
          if (r.due > now) return false;
          if (r.todayDictationPassed) return false;
          return true;
        }).toArray();
        setQueue(records);
      } else {
        if (courseData && selectedStage && selectedArticleId) {
          const sentences = courseData[selectedStage]?.[selectedArticleId] || [];
          let sentsArray = sentences;
          if (!Array.isArray(sentences) && typeof sentences === 'object') {
            sentsArray = Object.keys(sentences).sort((a,b) => Number(a) - Number(b)).map(k => (sentences as any)[k]);
          }
          const words = new Set<string>();
          sentsArray.forEach((s: any) => {
            if (s.target_words) s.target_words.forEach((w: any) => words.add((w.base_form || w.word_in_sentence).toLowerCase()));
            if (s.secondary_words) s.secondary_words.forEach((w: any) => words.add((w.base_form || w.word_in_sentence).toLowerCase()));
          });
          const customStr = localStorage.getItem('customVocab');
          if (customStr) {
             const cv = JSON.parse(customStr);
             cv.forEach((v: any) => {
                 if (v.stage === selectedStage && v.article === selectedArticleId) {
                     words.add(v.sv.toLowerCase());
                 }
             });
          }
          const mw = JSON.parse(localStorage.getItem('dictationMasteredWords') || '[]');
          
          const total = words.size;
          const queueItems = Array.from(words)
              .filter(w => !mw.includes(w))
              .map(w => ({ word_id: w }));
          
          setQueue(queueItems.sort(() => 0.5 - Math.random()));
          
          const remaining = queueItems.length;
          const mastered = total - remaining;
          setStats({ total, mastered, remaining });
        } else {
          setQueue([]);
          setStats({ total: 0, mastered: 0, remaining: 0 });
        }
      }
      setCurrentIndex(0);
      setLoading(false);
    };
    fetchQueue();
  }, [appMode, courseData, courseId, selectedStage, selectedArticleId]);

  const currentRecord = queue[currentIndex];
  const currentWord = currentRecord ? { word: currentRecord.word_id, audio: `words_audio/${currentRecord.word_id}.mp3` } : null;

  const playAudio = useCallback(() => {
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
  }, [currentWord]);

  const cleanText = (text: string) => {
    return text.replace(/[.,!?"':;()\-\u2019\u2018]/g, '').trim().toLowerCase();
  };

  const updateMastery = (wordId: string, correct: boolean) => {
    const mw = JSON.parse(localStorage.getItem('dictationMasteredWords') || '[]');
    if (correct) {
        if (!mw.includes(wordId.toLowerCase())) {
            mw.push(wordId.toLowerCase());
            localStorage.setItem('dictationMasteredWords', JSON.stringify(mw));
        }
    } else {
        const newMw = mw.filter((w: string) => w !== wordId.toLowerCase());
        if (newMw.length !== mw.length) {
            localStorage.setItem('dictationMasteredWords', JSON.stringify(newMw));
        }
    }
  };

  const proceedToNext = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setWrongCount(0);
    setInput('');
    setStatus('typing');
    setFeedbackMsg('');
    setCurrentIndex(prev => prev + 1);
    setStartTime(Date.now());
  }, []);

  const triggerAutoAdvance = useCallback(() => {
    if (!currentWord) return;
    const wordLen = currentWord.word.length;
    let duration = 1000 + wordLen * 140;
    if (duration < 1200) duration = 1200;
    if (duration > 8000) duration = 8000;
    
    timerRef.current = window.setTimeout(() => {
      proceedToNext();
    }, duration);
  }, [currentWord, proceedToNext]);

  const handleCorrect = async () => {
    setStatus('correct');
    setFeedbackMsg('Correct!');
    playAudio();
    
    if (appMode === 'study' && currentWord) {
        updateMastery(currentWord.word, true);
    }

    const timeSpent = (Date.now() - startTime) / 1000;
    if (appMode === 'review' && courseId && currentRecord) {
       const res = await submitGatePass(courseId, currentRecord.word_id, 'dictation', wrongCount, timeSpent, false, 0);
       if (res.completed) {
         window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Rated: ${res.rating}` }));
       }
    }
    
    triggerAutoAdvance();
  };

  const handleReveal = async () => {
    if (status !== 'typing') return;
    if (!currentWord || !courseId) return;
    
    setStatus('revealed');
    setFeedbackMsg('已Reveal Answer');
    
    if (appMode === 'study') {
        updateMastery(currentWord.word, false);
    }

    playAudio();
    
    const timeSpent = (Date.now() - startTime) / 1000;
    const res = await submitGatePass(courseId, currentRecord.word_id, 'dictation', wrongCount, timeSpent, true, 1);
    if (res.completed) {
      window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Rated: ${res.rating}` }));
    }
    
    triggerAutoAdvance();
  };

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        playAudio();
        return;
      }
      if (e.key === 'Escape' || (e.key === '/' && e.metaKey)) {
        e.preventDefault();
        if (status === 'typing') {
          handleReveal();
        } else {
          proceedToNext();
        }
        return;
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, [status, handleReveal, proceedToNext, playAudio]);

  const handleKeyDown = async (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (!currentWord || !courseId) return;
      
      if (status !== 'typing') {
        proceedToNext();
        return;
      }

      const cleanUserText = cleanText(input);
      const cleanCorrectText = cleanText(currentWord.word);
      
      if (cleanUserText === cleanCorrectText) {
        handleCorrect();
      } else {
        const newWrongCount = wrongCount + 1;
        setWrongCount(newWrongCount);
        
        let fb = '';
        if (cleanUserText.length > cleanCorrectText.length) fb = 'Too long';
        else if (cleanUserText.length < cleanCorrectText.length) fb = 'Too short';
        else fb = 'Incorrect letters';
        
        setFeedbackMsg(fb);
      }
    }
  };

  const handleResetProgress = () => {
    if (appMode !== 'study') return;
    const mw = JSON.parse(localStorage.getItem('dictationMasteredWords') || '[]');
    let currentScopeWords: string[] = [];
    
    if (courseData && selectedStage && selectedArticleId) {
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
      const customStr = localStorage.getItem('customVocab');
      if (customStr) {
         const cv = JSON.parse(customStr);
         cv.forEach((v: any) => {
             if (v.stage === selectedStage && v.article === selectedArticleId) {
                 currentScopeWords.push(v.sv.toLowerCase());
             }
         });
      }
    }
    const newMw = mw.filter((w: string) => !currentScopeWords.includes(w));
    localStorage.setItem('dictationMasteredWords', JSON.stringify(newMw));
    window.location.reload();
  };

  if (loading) return <div className="glass-panel view-container" style={{ padding: '48px', fontSize: '20px', textAlign: 'center' }}>Loading dictation...</div>;
  if (!queue.length) return <div className="glass-panel view-container" style={{ padding: '48px', fontSize: '20px', textAlign: 'center' }}>No words available!</div>;
  if (currentIndex >= queue.length) return <div className="glass-panel view-container" style={{ padding: '48px', fontSize: '20px', textAlign: 'center' }}>Session complete!</div>;

  const inputBorderColor = status === 'correct' ? 'var(--success)' : status === 'revealed' || wrongCount > 0 ? 'var(--error)' : 'var(--border)';
  const inputBgColor = status === 'correct' ? 'rgba(0, 255, 0, 0.1)' : status === 'revealed' ? 'rgba(255, 0, 0, 0.1)' : 'transparent';

  return (
    <main className="dictation-container glass-panel" style={{ width: '100%', maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
      {appMode === 'study' && (
        <div id="progress-stats" style={{ marginBottom: '1.5rem', color: '#cbd5e1', fontSize: '1rem', display: 'flex', gap: '15px', alignItems: 'center', flexWrap: 'wrap', justifyContent: 'center' }}>
          <span id="stat-total">Total: {stats.total}</span>
          <span id="stat-correct" style={{ color: '#4ade80' }}>Mastered: {stats.mastered}</span>
          <span id="stat-remaining" style={{ color: '#f87171' }}>Remaining: {stats.remaining}</span>
          <button id="reset-progress-btn" onClick={handleResetProgress} style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.3)', color: 'white', borderRadius: '10px', padding: '4px 10px', cursor: 'pointer', fontSize: '0.8rem', transition: 'background 0.3s' }}>Reset Progress</button>
        </div>
      )}
      
      <div id="feedback-msg" className={`feedback ${status === 'correct' ? 'correct' : (wrongCount > 0 ? 'incorrect' : '')}`}>
        {feedbackMsg}
      </div>
      
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '2rem' }}>
        <button id="play-btn" className="play-btn" onClick={playAudio} style={{ marginBottom: '0', position: 'relative' }}>
          ▶
          <span style={{ position: 'absolute', bottom: '-20px', left: '50%', transform: 'translateX(-50%)', fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', fontFamily: "'Outfit', sans-serif" }}>Tab</span>
        </button>
        <button id="redo-btn" className="play-btn" style={{ marginBottom: '0', background: 'transparent', display: 'none', fontSize: '2rem', paddingLeft: '0' }}>
          ↻
        </button>
      </div>
      
      <div className="input-group">
        <div id="hint-display" style={{ color: '#9ca3af', fontStyle: 'italic', marginBottom: '0.5rem', display: 'none' }}></div>
        <input 
          type="text" 
          id="spell-input" 
          className="spell-input" 
          placeholder="Type here and hit Enter" 
          autoComplete="off" 
          spellCheck="false"
          autoFocus
          value={input}
          onChange={e => { if (status === 'typing') setInput(e.target.value); }}
          onKeyDown={handleKeyDown}
          disabled={status !== 'typing'}
          style={{ 
            borderColor: inputBorderColor,
            background: inputBgColor,
            color: 'white'
          }}
        />
        
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
          <button 
            id="reveal-btn" 
            className={`reveal-btn ${(status === 'typing' && wrongCount >= 3) || status === 'revealed' ? 'show' : ''}`}
            onClick={handleReveal}
          >
            Reveal Answer
          </button>
        </div>
        
        <div id="answer-display" className={`answer-display ${status === 'correct' || status === 'revealed' ? 'show' : ''}`}>
          <strong style={{ fontSize: '1.5rem', color: 'var(--accent-color)' }} id="correct-sv">{currentWord?.word}</strong>
          <span style={{ color: '#9ca3af', fontStyle: 'italic' }} id="correct-en">{currentRecord?.en_translation}</span>
        </div>
      </div>
      
      <div id="timer-bar" className="timer-bar" style={{ display: (status === 'correct' || status === 'revealed') ? 'block' : 'none' }}>
        <div id="timer-fill" className="timer-fill" style={{ width: '100%', transition: 'width 2s linear' }}></div>
      </div>
    </main>
  );
}