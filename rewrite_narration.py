import re

with open('frontend/src/pages/Narration.tsx', 'r') as f:
    content = f.read()

# Replace state variables
content = re.sub(
    r'const \[activeIndex, setActiveIndex\] = useState\(0\);.*?const sentenceRefs = useRef<\(HTMLElement \| null\)\[\]>\(\[\]\);',
    '''const [activeIndex, setActiveIndex] = useState(0);
  const [customVocab, setCustomVocab] = useState<Record<string, 'target' | 'secondary' | 'none'>>({});
  
  const [editModeIndex, setEditModeIndex] = useState<number | null>(null);
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const sentenceRefs = useRef<(HTMLElement | null)[]>([]);''',
    content,
    flags=re.DOTALL
)

# Remove saveLearningModal
content = re.sub(
    r'const saveLearningModal = \(\) => \{.*?setIsLearningModalOpen\(false\);\n  \};',
    '',
    content,
    flags=re.DOTALL
)

# Rewrite playAudio
content = re.sub(
    r'const playAudio = useCallback\(\(audioPath: string\) => \{.*?audio\.play\(\)\.catch\(console\.error\);\n  \}, \[\]\);',
    '''const playAudio = useCallback((audioPath: string, index?: number) => {
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
  }, [activeIndex]);''',
    content,
    flags=re.DOTALL
)

# Rewrite handleKeyDown
content = re.sub(
    r'const handleKeyDown = \(e: KeyboardEvent\) => \{.*?window\.removeEventListener\(\'keydown\', handleKeyDown\);\n  \}, \[sentencesArray, activeIndex, playAudio\]\);',
    '''const handleKeyDown = (e: KeyboardEvent) => {
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
  }, [sentencesArray, activeIndex, playAudio]);''',
    content,
    flags=re.DOTALL
)

# Rewrite article rendering
article_replacement = '''
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
                        // Stop audio if already playing
                        if (audioRef.current) {
                            audioRef.current.pause();
                            audioRef.current.currentTime = 0;
                        }
                        setPlayingIndex(null);
                    } else {
                        setActiveIndex(i);
                        playAudio(`sentences_audio/${sent.id}.mp3`, i);
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
                          {sent.sv.split(/(\\s+)/).map((token: string, tIdx: number) => {
                              if (/^\\s+$/.test(token)) return <span key={tIdx}>{token}</span>;
                              const cleanWord = token.replace(/[.,!?;:()[\\]{}"”]/g, "").trim();
                              if (!cleanWord) return <span key={tIdx}>{token}</span>;
                              
                              const baseWordLower = cleanWord.toLowerCase();
                              let currentStatus = customVocab[baseWordLower];
                              if (!currentStatus) {
                                  // Determine initial
                                  const isTarget = combinedWords.some(w => w.type === 'target' && (w.base_form?.toLowerCase() === baseWordLower || w.word?.toLowerCase() === baseWordLower));
                                  const isSecondary = combinedWords.some(w => w.type === 'secondary' && (w.base_form?.toLowerCase() === baseWordLower || w.word?.toLowerCase() === baseWordLower));
                                  currentStatus = isTarget ? 'target' : (isSecondary ? 'secondary' : 'none');
                              }

                              const isTarget = currentStatus === 'target';
                              const isSecondary = currentStatus === 'secondary';

                              return (
                                  <span 
                                      key={tIdx} 
                                      className={`selectable-word ${isTarget ? 'selected-word' : ''} ${isSecondary ? 'selected-secondary-word' : ''}`}
                                      style={{ cursor: 'pointer', borderRadius: '4px', padding: '0 2px', background: isTarget ? 'rgba(239, 68, 68, 0.2)' : isSecondary ? 'rgba(245, 158, 11, 0.2)' : 'transparent', textDecoration: (isTarget||isSecondary) ? 'underline' : 'none', color: isTarget ? '#ef4444' : isSecondary ? '#f59e0b' : 'inherit' }}
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
                            // If we want to restore strictly, we'd need a ref to previous state, but this is acceptable for now.
                            setEditModeIndex(null);
                        }} style={{ padding: '6px 12px', background: 'transparent', color: 'var(--text-mute)', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}>取消</button>
                    </div>
                )}
              </article>
            );'''

content = re.sub(
    r'const isActive = i === activeIndex;.*?<\/article>\n\s*\);\n\s*\}\)',
    article_replacement + '\n          })',
    content,
    flags=re.DOTALL
)

# Remove the learning modal completely
content = re.sub(
    r'\{isLearningModalOpen && \(.*?<\/div>\n\s*\)\}',
    '',
    content,
    flags=re.DOTALL
)

with open('frontend/src/pages/Narration.tsx', 'w') as f:
    f.write(content)

