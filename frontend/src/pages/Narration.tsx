import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useData } from '../contexts/DataContext';
import { parseEnglishSentence } from '../utils/parser';
import type { WordData } from '../utils/parser';
import { getMp3PublicUrl } from '../services/r2';
import VocabularyModal from '../components/VocabularyModal';

export function localParseSentence(svText: string, targetWords: any[] = [], secondaryWords: any[] = [], customVocab: Record<string, 'target'|'secondary'|'none'> = {}) {
    let allWords: any[] = [];
    if (targetWords) {
        allWords.push(...targetWords.map(w => typeof w === 'string' ? { word: w, type: 'target' } : { ...w, type: 'target' }));
    }
    if (secondaryWords) {
        allWords.push(...secondaryWords.map(w => typeof w === 'string' ? { word: w, type: 'secondary' } : { ...w, type: 'secondary' }));
    }
    Object.keys(customVocab).forEach(w => {
        if (customVocab[w] === 'target') allWords.push({ word: w, type: 'target' });
        if (customVocab[w] === 'secondary') allWords.push({ word: w, type: 'secondary' });
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
                let baseWord = encodeURIComponent(w.base_form || (w as any).word_in_sentence || (w as any).word || (w as any).word_in_sentence || (w as any).word_in_sentence || exactWord);
                let kBg = 'transparent';
                let kColor = 'inherit';
                let kBorder = 'none';
                if (w.type === 'target') {
                    kBg = 'rgba(239, 68, 68, 0.2)'; kColor = '#ef4444'; kBorder = '2px solid rgba(239, 68, 68, 0.5)';
                } else if (w.type === 'secondary') {
                    kBg = 'rgba(245, 158, 11, 0.2)'; kColor = '#f59e0b'; kBorder = '2px solid rgba(245, 158, 11, 0.5)';
                } else if (w.type === 'custom') {
                    kBg = 'rgba(16, 185, 129, 0.2)'; kColor = '#10b981'; kBorder = '2px solid rgba(16, 185, 129, 0.5)';
                }
                htmlChunks.push(`<span class="vocab-word ${w.type}-word" data-word="${baseWord}" style="--k-bg: ${kBg}; --k-color: ${kColor}; --k-border: ${kBorder}">${exactWord}</span>`);
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
            const wordStr = (w as any).word_in_sentence || (w as any).word || (w as any).word_in_sentence || (w as any).word_in_sentence || w.base_form;
            if (!wordStr) return;
            let escaped = wordStr.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            let regex = new RegExp(`\\b${escaped}\\b`, 'gi');
            if (!regex.test(processedText)) {
                regex = new RegExp(escaped, 'gi');
            }
            let match = processedText.match(regex);
            while (match) {
                let token = `__TOKEN_${idx}_${Math.random().toString(36).substring(7)}__`;
                let baseWord = encodeURIComponent(w.base_form || (w as any).word_in_sentence || (w as any).word_in_sentence || wordStr);
                let kBg = 'transparent';
                let kColor = 'inherit';
                let kBorder = 'none';
                if (w.type === 'target') {
                    kBg = 'rgba(239, 68, 68, 0.2)'; kColor = '#ef4444'; kBorder = '2px solid rgba(239, 68, 68, 0.5)';
                } else if (w.type === 'secondary') {
                    kBg = 'rgba(245, 158, 11, 0.2)'; kColor = '#f59e0b'; kBorder = '2px solid rgba(245, 158, 11, 0.5)';
                } else if (w.type === 'custom') {
                    kBg = 'rgba(16, 185, 129, 0.2)'; kColor = '#10b981'; kBorder = '2px solid rgba(16, 185, 129, 0.5)';
                }
                tokens.push({ token, html: `<span class="vocab-word ${w.type}-word" data-word="${baseWord}" style="--k-bg: ${kBg}; --k-color: ${kColor}; --k-border: ${kBorder}">${match[0]}</span>` });
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
  const [customVocab, setCustomVocab] = useState<Record<string, 'target' | 'secondary' | 'none'>>({});
  
  const [editModeIndex, setEditModeIndex] = useState<number | null>(null);
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const sentenceRefs = useRef<(HTMLElement | null)[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem('customVocab');
    if (saved) {
      try { setCustomVocab(JSON.parse(saved)); } catch (e) {}
    }
  }, []);



  useEffect(() => {
    if (courseId) {
      setLoading(true);
      loadCourse(courseId).finally(() => setLoading(false));
    }
  }, [courseId, loadCourse]);

  // Derive stages and articles from courseData

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








  // KTV Dynamic Effect
  useEffect(() => {
    if (playingIndex !== null) {
      const container = sentenceRefs.current[playingIndex];
      if (container) {
        // Select words. In Edit mode it's .selectable-word, in View mode it's .vocab-word
        const words = container.querySelectorAll('.vocab-word, .selectable-word');
        words.forEach((w, i) => {
          (w as HTMLElement).style.animationDelay = `${i * 0.15}s`;
          w.classList.remove('karaoke-anim');
          // Trigger reflow
          void (w as HTMLElement).offsetWidth;
          w.classList.add('karaoke-anim');
        });
      }
    } else {
      // Clear all animations
      sentenceRefs.current.forEach(ref => {
        if (ref) {
          const words = ref.querySelectorAll('.karaoke-anim');
          words.forEach(w => w.classList.remove('karaoke-anim'));
        }
      });
    }
  }, [playingIndex]);

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
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  {!isEditing ? (
                      <p style={{ margin: 0, fontSize: '20px', lineHeight: '1.6', color: 'var(--text-h)' }}
                         dangerouslySetInnerHTML={{ __html: localParseSentence(sent.sv, sent.target_words, sent.secondary_words, customVocab) }}
                      />
                  ) : (
                      <div style={{ margin: 0, fontSize: '20px', lineHeight: '1.6', color: 'var(--text-h)' }}>
                          {sent.sv.split(/(\s+)/).map((token: string, tIdx: number) => {
                              if (/^\s+$/.test(token)) return <span key={tIdx}>{token}</span>;
                              const cleanWord = token.replace(/[.,!?;:()[\]{}"”]/g, "").trim();
                              if (!cleanWord) return <span key={tIdx}>{token}</span>;
                              
                              const baseWordLower = cleanWord.toLowerCase();
                              let currentStatus = customVocab[baseWordLower];
                              if (!currentStatus) {
                                  const isTarget = combinedWords.some(w => w.type === 'target' && (w.base_form?.toLowerCase() === baseWordLower || (w as any).word_in_sentence || (w as any).word?.toLowerCase() === baseWordLower));
                                  const isSecondary = combinedWords.some(w => w.type === 'secondary' && (w.base_form?.toLowerCase() === baseWordLower || (w as any).word_in_sentence || (w as any).word?.toLowerCase() === baseWordLower));
                                  currentStatus = isTarget ? 'target' : (isSecondary ? 'secondary' : 'none');
                              }

                              const isTarget = currentStatus === 'target';
                              const isSecondary = currentStatus === 'secondary';

                              return (
                                  <span 
                                      key={tIdx} 
                                      className={`selectable-word ${isTarget ? 'selected-word' : ''} ${isSecondary ? 'selected-secondary-word' : ''}`}
                                      style={{ cursor: 'pointer', borderRadius: '4px', padding: '0 2px' }}
                                      onClick={(e) => {
                                          e.stopPropagation();
                                          setCustomVocab(prev => ({
                                              ...prev,
                                              [baseWordLower]: currentStatus === 'target' ? 'secondary' : (currentStatus === 'secondary' ? 'none' : 'target')
                                          }));
                                      }}
                                  >
                                      {token}
                                  </span>
                              );
                          })}
                      </div>
                  )}
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  </div>
                </div>
                {sent.en && (
                  <p 
                    style={{ margin: 0, fontSize: '16px', color: 'var(--text)', lineHeight: '1.6' }} 
                    dangerouslySetInnerHTML={{ __html: parseEnglishSentence(sent.en, combinedWords) }} 
                  />
                )}
                {!isEditing ? (
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
                ) : (
                    <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
                        <button onClick={(e) => {
                            e.stopPropagation();
                            localStorage.setItem('customVocab', JSON.stringify(customVocab));
                            setEditModeIndex(null);
                        }} style={{ padding: '6px 12px', background: 'var(--accent)', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>保存修改</button>
                        <button onClick={(e) => {
                            e.stopPropagation();
                            setEditModeIndex(null);
                        }} style={{ padding: '6px 12px', background: 'transparent', color: 'var(--text-mute)', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}>取消</button>
                    </div>
                )}
              </article>
            );
          })}
        </div>
      )}




      {selectedWord && courseId && (
        <VocabularyModal 
          courseId={courseId}
          word={selectedWord.word} 
          en={selectedWord.en} 
          onClose={() => setSelectedWord(null)} 
        />
      )}
    </div>
  );
}
