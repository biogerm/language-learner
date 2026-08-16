import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { db } from '../db/dexie';
import { submitGatePass } from '../utils/fsrs';
import { getMp3PublicUrl } from '../services/r2';
import { useData } from '../contexts/DataContext';

export default function Dictation() {
  const { courseId } = useParams();
  const { courseData, loadCourse } = useData();
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

  const [selectedStage, setSelectedStage] = useState('');
  const [selectedArticleId, setSelectedArticleId] = useState('');
  
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

  const stages = useMemo(() => {
    if (!courseData) return [];
    return Object.keys(courseData).map(stageName => {
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
    if (stage && stage.articles.length > 0) {
      setSelectedArticleId(stage.articles[0].id);
    } else {
      setSelectedArticleId('');
    }
  };

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
             Object.keys(cv).forEach(k => {
               if (cv[k] !== 'none') words.add(k.toLowerCase());
             });
          }
          const queueItems = Array.from(words).map(w => ({ word_id: w }));
          setQueue(queueItems.sort(() => 0.5 - Math.random()));
        } else {
          setQueue([]);
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

  // Clean text function
  const cleanText = (text: string) => {
    return text.replace(/[.,!?"':;()\-\u2019\u2018]/g, '').trim().toLowerCase();
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
    
    const timeSpent = (Date.now() - startTime) / 1000;
    if (courseId && currentRecord) {
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

  if (loading) return <div className="glass-panel view-container" style={{ padding: '48px', fontSize: '20px', textAlign: 'center' }}>Loading dictation...</div>;
  if (!queue.length) return <div className="glass-panel view-container" style={{ padding: '48px', fontSize: '20px', textAlign: 'center' }}>No words available!</div>;
  if (currentIndex >= queue.length) return <div className="glass-panel view-container" style={{ padding: '48px', fontSize: '20px', textAlign: 'center' }}>Session complete!</div>;

  const showSelectors = appMode === 'study' && stages.length > 0;
  const inputBorderColor = status === 'correct' ? 'var(--success)' : status === 'revealed' || wrongCount > 0 ? 'var(--error)' : 'var(--border)';
  const inputBgColor = status === 'correct' ? 'rgba(0, 255, 0, 0.1)' : status === 'revealed' ? 'rgba(255, 0, 0, 0.1)' : 'transparent';

  return (
    <div className="glass-panel view-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        {!showSelectors && <h3 style={{ margin: 0, fontSize: '24px' }}>Dictation ({appMode})</h3>}
        {showSelectors && (
          <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
            <select className="module-selector" value={selectedStage} onChange={handleStageChange}>
              {stages.map(s => <option key={s.id} value={s.id}>{s.title}</option>)}
            </select>
            <select className="module-selector" value={selectedArticleId} onChange={e => setSelectedArticleId(e.target.value)}>
              {stages.find(s => s.id === selectedStage)?.articles?.map(a => <option key={a.id} value={a.id}>{a.title}</option>)}
            </select>
          </div>
        )}
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <p style={{ margin: 0, color: 'var(--text)' }}>Card {currentIndex + 1} of {queue.length}</p>
        <button 
          onClick={playAudio} 
          style={{ 
            background: 'transparent', 
            border: 'none', 
            fontSize: '32px', 
            cursor: 'pointer',
            padding: '8px',
            opacity: 0.8,
            transition: 'opacity 0.2s'
          }}
          title="Play Audio (Tab)"
          onMouseEnter={e => e.currentTarget.style.opacity = '1'}
          onMouseLeave={e => e.currentTarget.style.opacity = '0.8'}
        >
          🔊
        </button>
      </div>

      <div style={{ position: 'relative', marginTop: '16px' }}>
        <input 
          autoFocus
          type="text" 
          value={input} 
          onChange={e => {
            if (status === 'typing') setInput(e.target.value);
          }} 
          onKeyDown={handleKeyDown}
          placeholder="Type what you hear..."
          disabled={status !== 'typing'}
          style={{ 
            width: '100%', 
            padding: '16px', 
            fontSize: '24px', 
            borderRadius: '12px', 
            border: `2px solid ${inputBorderColor}`,
            backgroundColor: inputBgColor,
            textAlign: 'center', 
            marginBottom: '8px',
            transition: 'all 0.3s ease'
          }}
        />
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', minHeight: '30px' }}>
          <div style={{ color: status === 'correct' ? 'var(--success, #28a745)' : 'var(--error, #dc3545)', fontWeight: 'bold' }}>
            {feedbackMsg}
          </div>
          
          {status === 'typing' && (
            <button 
              onClick={handleReveal} 
              className="btn-primary" 
              style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.4)', color: 'white', padding: '4px 12px', fontSize: '14px' }}
            >
              Reveal Answer
            </button>
          )}
        </div>
      </div>

      {status !== 'typing' && (
        <div className="reveal-animation" style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '16px' }}>
          <div className="flashcard-word" onClick={playAudio} style={{ cursor: 'pointer', color: 'var(--accent)' }}>
            {currentWord?.word}
          </div>
          
          <div style={{ width: '100%', height: '4px', background: 'var(--glass-border)', marginTop: '24px', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{ 
              height: '100%', 
              background: 'var(--accent)', 
              width: '100%', 
              animation: `timerFill ${1000 + (currentWord?.word.length || 0) * 140}ms linear forwards` 
            }} />
          </div>
          <style>{`
            @keyframes timerFill {
              from { width: 100%; }
              to { width: 0%; }
            }
          `}</style>
          
          <p style={{ color: 'var(--text)', fontStyle: 'italic', marginTop: '16px' }}>Press Enter or Escape to skip timer</p>
        </div>
      )}
    </div>
  );
}

