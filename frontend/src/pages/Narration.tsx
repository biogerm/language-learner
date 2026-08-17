import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useData } from '../contexts/DataContext';
import { parseEnglishSentence } from '../utils/parser';
import type { WordData } from '../utils/parser';
import { getMp3PublicUrl } from '../services/r2';
import EditableSentence from '../components/EditableSentence';

export function localParseSentence(svText: string, targetWords: any[] = [], secondaryWords: any[] = [], customVocabArray: any[] = [], excludedVocabArray: string[] = []) {
    let allWords: any[] = [];
    if (targetWords) {
        allWords.push(...targetWords.map(w => typeof w === 'string' ? { word: w, type: 'target' } : { ...w, type: 'target' }));
    }
    if (secondaryWords) {
        allWords.push(...secondaryWords.map(w => typeof w === 'string' ? { word: w, type: 'secondary' } : { ...w, type: 'secondary' }));
    }
    customVocabArray.forEach(v => {
        allWords.push({ word: v.sv, type: 'secondary' }); // Custom words display as secondary
    });
    
    // Filter out excluded words
    allWords = allWords.filter(w => {
        const baseWordLower = (w.base_form || w.word || w.word_in_sentence || '').toLowerCase();
        return !excludedVocabArray.includes(baseWordLower);
    });
    
    const hasPositions = allWords.length > 0 && allWords.every(w => w.position_start !== undefined && w.position_end !== undefined);
    
    if (hasPositions) {
        allWords.sort((a, b) => a.position_start - b.position_start);
        let htmlChunks: string[] = [];
        let currentIndex = 0;
        allWords.forEach(w => {
            if (w.position_start >= currentIndex) {
                htmlChunks.push(svText.substring(currentIndex, w.position_start));
                let exactWord = svText.substring(w.position_start, w.position_end);
                let baseWord = encodeURIComponent(w.base_form || w.word || w.word_in_sentence || exactWord);
                htmlChunks.push(`<span class="vocab-word ${w.type}-word" data-word="${baseWord}">${exactWord}</span>`);
                currentIndex = w.position_end;
            }
        });
        htmlChunks.push(svText.substring(currentIndex));
        return htmlChunks.join("");
    } else {
        let processedText = svText || "";
        let tokens: {token: string, html: string}[] = [];
        allWords.sort((a, b) => {
            const aWord = a.word || a.word_in_sentence || a.base_form || '';
            const bWord = b.word || b.word_in_sentence || b.base_form || '';
            return bWord.length - aWord.length;
        });

        allWords.forEach((w, idx) => {
            const wordStr = w.word || w.word_in_sentence || w.base_form;
            if (!wordStr) return;
            let escaped = wordStr.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            let regex = new RegExp(`\\b${escaped}\\b`, 'gi');
            if (!regex.test(processedText)) {
                regex = new RegExp(escaped, 'gi');
            }
            let match = processedText.match(regex);
            while (match) {
                let token = `__TOKEN_${idx}_${Math.random().toString(36).substring(7)}__`;
                let baseWord = encodeURIComponent(w.base_form || w.word_in_sentence || wordStr);
                tokens.push({ token, html: `<span class="vocab-word ${w.type}-word" data-word="${baseWord}">${match[0]}</span>` });
                processedText = processedText.replace(regex, token);
                match = processedText.match(regex);
            }
        });

        tokens.forEach(t => {
            processedText = processedText.replace(t.token, t.html);
        });

        return processedText;
    }
}
export default function Narration() {
  const { courseId } = useParams();
  const { courseData, loadCourse, selectedStage, selectedArticleId } = useData();
  const [loading, setLoading] = useState(false);
  const [selectedWord, setSelectedWord] = useState<{word: string, en: string} | null>(null);

  // New states
  const [activeIndex, setActiveIndex] = useState(0);
  const [editModeIndex, setEditModeIndex] = useState<number | null>(null);
  // Global custom vocab reload
  const [customVocabArray, setCustomVocabArray] = useState<any[]>([]);
  const [excludedVocabArray, setExcludedVocabArray] = useState<string[]>([]);
  
  const loadVocab = useCallback(() => {
    try { setCustomVocabArray(JSON.parse(localStorage.getItem('customVocab') || '[]')); } catch (e) {}
    try { setExcludedVocabArray(JSON.parse(localStorage.getItem('excludedVocab') || '[]')); } catch (e) {}
  }, []);

  useEffect(() => {
    loadVocab();
    window.addEventListener('vocabUpdated', loadVocab);
    return () => window.removeEventListener('vocabUpdated', loadVocab);
  }, [loadVocab]);

  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const sentenceRefs = useRef<(HTMLElement | null)[]>([]);

  useEffect(() => {
    if (courseId) {
      setLoading(true);
      loadCourse(courseId).finally(() => setLoading(false));
    }
  }, [courseId, loadCourse]);

  useEffect(() => {
    // Reset active index when article changes
    setActiveIndex(0);
  }, [selectedArticleId]);

  useEffect(() => {
    if (sentenceRefs.current[activeIndex]) {
      sentenceRefs.current[activeIndex]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [activeIndex]);

  const sentencesArray = useMemo(() => {
    if (!courseData || !selectedStage || !selectedArticleId) return [];
    const stageData = courseData[selectedStage];
    if (!stageData) return [];
    let sentences = stageData[selectedArticleId] || [];
    // If it's parsed as an object with numeric keys, convert to array
    if (!Array.isArray(sentences) && typeof sentences === 'object') {
      sentences = Object.keys(sentences).sort((a,b) => Number(a) - Number(b)).map(k => sentences[k]);
    }
    return sentences;
  }, [courseData, selectedStage, selectedArticleId]);

  const playAudio = useCallback((audioPath: string, index?: number) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    const idx = index !== undefined ? index : activeIndex;
    setPlayingIndex(idx);
    const url = getMp3PublicUrl(audioPath);
    const audio = new Audio(url);
    audioRef.current = audio;
    audio.onended = () => {
      setPlayingIndex(null);
    };
    audio.play().catch(console.error);
  }, [activeIndex]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      if (e.code === 'Space') {
        e.preventDefault();
        const nextIdx = e.shiftKey ? Math.max(activeIndex - 1, 0) : Math.min(activeIndex + 1, (sentencesArray?.length || 1) - 1);
        setActiveIndex(nextIdx);
        if (sentencesArray?.[nextIdx]) {
          playAudio(`sentences_audio/${sentencesArray[nextIdx].id}.mp3`, nextIdx);
        }
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (sentencesArray?.[activeIndex]) {
          playAudio(`sentences_audio/${sentencesArray[activeIndex].id}.mp3`, activeIndex);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [sentencesArray, activeIndex, playAudio]);

  return (
    <div className="glass-panel" style={{ width: '100%', maxWidth: '800px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {loading ? <p>Loading article...</p> : sentencesArray.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h2>{selectedArticleId || 'Article'}</h2>
          {sentencesArray.map((sent: any, i: number) => {
            const isActive = i === activeIndex;
            const combinedWords: WordData[] = [
              ...(sent.target_words || []).map((w: any) => ({ ...w, type: 'target' })),
              ...(sent.secondary_words || []).map((w: any) => ({ ...w, type: 'secondary' }))
            ];
            const isEditing = editModeIndex === i;

            return (
              <article 
                className={`sentence-card ${playingIndex === i ? 'playing' : ''}`}
                key={i} 
                ref={el => { sentenceRefs.current[i] = el; }}
                style={{ 
                  position: 'relative',
                  display: 'flex', 
                  flexDirection: 'column', 
                  gap: '8px', 
                  padding: '16px', 
                  border: isActive ? '2px solid var(--accent)' : '1px solid var(--border)', 
                  borderRadius: '12px', 
                  background: isActive ? 'rgba(139, 92, 246, 0.05)' : 'var(--glass-bg)',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer'
                }}
                onClick={(e) => {
                  if (isEditing) return;
                  if (!(e.target as HTMLElement).closest('.vocab-word')) {
                    if (playingIndex === i) {
                        if (audioRef.current) {
                            audioRef.current.pause();
                            audioRef.current.currentTime = 0;
                        }
                        setPlayingIndex(null);
                    } else {
                        setActiveIndex(i);
                        playAudio(`sentences_audio/${sent.id}.mp3`, i);
                    }
                  } else {
                    const target = (e.target as HTMLElement).closest('.vocab-word');
                    if (target) {
                        const word = target.getAttribute('data-word') || target.textContent;
                        if (word) {
                            playAudio(`words_audio/${word}.mp3`);
                            setSelectedWord({ word: decodeURIComponent(word), en: 'Dictionary translation pending implementation' }); 
                        }
                    }
                  }
                }}
              >
                {!isEditing ? (
                    <p style={{ margin: 0, fontSize: '20px', lineHeight: '1.6', color: 'var(--text-h)' }}
                        dangerouslySetInnerHTML={{ __html: localParseSentence(sent.sv, sent.target_words, sent.secondary_words, customVocabArray, excludedVocabArray) }}
                    />
                ) : (
                    <EditableSentence 
                        sent={sent}
                        combinedWords={combinedWords}
                        courseId={courseId || ''}
                        stage={selectedStage}
                        article={selectedArticleId}
                        onSaveComplete={() => setEditModeIndex(null)}
                        onCancel={() => setEditModeIndex(null)}
                    />
                )}
                
                {sent.en && !isEditing && (
                  <p 
                    style={{ margin: 0, fontSize: '16px', color: 'var(--text)', lineHeight: '1.6' }} 
                    dangerouslySetInnerHTML={{ __html: parseEnglishSentence(sent.en, combinedWords) }} 
                  />
                )}
                {!isEditing && (
                    <button 
                      className="extract-vocab-btn"
                      title="Extract Vocab"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditModeIndex(i);
                      }}
                    >
                      📖
                    </button>
                )}
              </article>
            );
          })}
        </div>
      )}

      {selectedWord && (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
            background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
            <div className="glass-panel" style={{ padding: '24px', width: '300px', maxWidth: '90vw', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <h3 style={{ margin: 0 }}>{selectedWord.word}</h3>
                <p style={{ margin: 0 }}>{selectedWord.en}</p>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button className="btn-primary" style={{ padding: '8px 16px', background: 'transparent', color: 'var(--text)', border: '1px solid var(--border)' }} onClick={() => setSelectedWord(null)}>Close</button>
                </div>
            </div>
        </div>
      )}
    </div>
  );
}
