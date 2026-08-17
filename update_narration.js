const fs = require('fs');

const path = 'frontend/src/pages/Narration.tsx';
let content = fs.readFileSync(path, 'utf8');

// 1. imports and refs
content = content.replace(
  "import { useState, useEffect, useCallback, useMemo } from 'react';",
  "import { useState, useEffect, useCallback, useMemo, useRef } from 'react';"
);

// 2. states
content = content.replace(
  `  const [activeIndex, setActiveIndex] = useState(0);
  const [customVocab, setCustomVocab] = useState<Record<string, 'target' | 'secondary' | 'none'>>({});
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [tempCustomVocab, setTempCustomVocab] = useState<Record<string, 'target' | 'secondary' | 'none'>>({});`,
  `  const [activeIndex, setActiveIndex] = useState(0);
  const [customVocab, setCustomVocab] = useState<Record<string, 'target' | 'secondary' | 'none'>>({});
  
  const [isLearningModalOpen, setIsLearningModalOpen] = useState(false);
  const [vocabInput, setVocabInput] = useState('');
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const sentenceRefs = useRef<(HTMLDivElement | null)[]>([]);`
);

// 3. saveVocab
content = content.replace(
  `  const saveVocab = () => {
    setCustomVocab(tempCustomVocab);
    localStorage.setItem('customVocab', JSON.stringify(tempCustomVocab));
    setEditingIndex(null);
  };`,
  `  const saveLearningModal = () => {
    const words = vocabInput.split(/[\\s,]+/).filter(w => w.trim().length > 0);
    const nextVocab = {} as Record<string, 'target'|'secondary'|'none'>;
    words.forEach(w => nextVocab[w.toLowerCase()] = 'target');
    setCustomVocab(nextVocab);
    localStorage.setItem('customVocab', JSON.stringify(nextVocab));
    setIsLearningModalOpen(false);
  };`
);

// 4. scrollIntoView effect
content = content.replace(
  `  useEffect(() => {
    // Reset active index when article changes
    setActiveIndex(0);
  }, [selectedArticleId]);`,
  `  useEffect(() => {
    // Reset active index when article changes
    setActiveIndex(0);
  }, [selectedArticleId]);

  useEffect(() => {
    if (sentenceRefs.current[activeIndex]) {
      sentenceRefs.current[activeIndex]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [activeIndex]);`
);

// 5. playAudio
content = content.replace(
  `  const playAudio = useCallback((audioPath: string) => {
    const url = getMp3PublicUrl(audioPath);
    new Audio(url).play().catch(console.error);
  }, []);`,
  `  const playAudio = useCallback((audioPath: string) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    const url = getMp3PublicUrl(audioPath);
    const audio = new Audio(url);
    audioRef.current = audio;
    audio.play().catch(console.error);
  }, []);`
);

// 6. keydown listener
content = content.replace(
  `  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setEditingIndex(null);
      }
      
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      if (e.key === 'ArrowRight') {
        setActiveIndex(prev => sentencesArray ? Math.min(prev + 1, sentencesArray.length - 1) : prev);
      } else if (e.key === 'ArrowLeft') {
        setActiveIndex(prev => Math.max(prev - 1, 0));
      } else if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault();
        if (sentencesArray?.[activeIndex]) {
          playAudio(\`sentences_audio/\${sentencesArray[activeIndex].id}.mp3\`);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [sentencesArray, activeIndex, playAudio]);`,
  `  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      if (e.code === 'Space') {
        e.preventDefault();
        if (e.shiftKey) {
          setActiveIndex(prev => Math.max(prev - 1, 0));
        } else {
          setActiveIndex(prev => sentencesArray ? Math.min(prev + 1, sentencesArray.length - 1) : prev);
        }
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (sentencesArray?.[activeIndex]) {
          playAudio(\`sentences_audio/\${sentencesArray[activeIndex].id}.mp3\`);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [sentencesArray, activeIndex, playAudio]);`
);

// 7. remove handleEditWordClick and renderSentenceWithHighlights
content = content.replace(/  const handleEditWordClick = [\s\S]*?  };/, '');
content = content.replace(/  const renderSentenceWithHighlights = [\s\S]*?  };/, '');

// 8. Add book button
content = content.replace(
  `        <div style={{ display: 'flex', gap: '8px' }}>
        </div>`,
  `        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={() => {
            setVocabInput(Object.keys(customVocab).filter(k => customVocab[k] === 'target').join(', '));
            setIsLearningModalOpen(true);
          }} style={{ background: 'transparent', border: '1px solid var(--border)', borderRadius: '8px', padding: '8px 16px', cursor: 'pointer', fontSize: '20px' }}>📖</button>
        </div>`
);

// 9. replace rendering sentence mapping
content = content.replace(
  `              <div 
                key={i} 
                style={{ `,
  `              <div 
                key={i} 
                ref={el => sentenceRefs.current[i] = el}
                style={{ `
);

// replace isEditing checks
content = content.replace(
  `            const isEditing = i === editingIndex;`,
  `            const isEditing = false;`
);

// replace rendering parts:
const renderingToReplace = `<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  {isEditing ? (
                    <p style={{ margin: 0, fontSize: '20px', lineHeight: '1.6', color: 'var(--text-h)' }}>
                      {renderSentenceWithHighlights(sent.sv, sent, isEditing)}
                    </p>
                  ) : (
                    <p style={{ margin: 0, fontSize: '20px', lineHeight: '1.6', color: 'var(--text-h)' }}
                       dangerouslySetInnerHTML={{ __html: parseSentence(sent.sv, sent.target_words, sent.secondary_words) }}
                    />
                  )}
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    {isEditing ? (
                      <>
                        <button onClick={(e) => { e.stopPropagation(); saveVocab(); }} style={{ padding: '4px 8px', borderRadius: '4px', background: 'var(--accent)', color: 'white', border: 'none', cursor: 'pointer' }}>Save</button>
                        <button onClick={(e) => { e.stopPropagation(); setEditingIndex(null); }} style={{ padding: '4px 8px', borderRadius: '4px', background: 'transparent', color: 'var(--text-mute)', border: '1px solid var(--border)', cursor: 'pointer' }}>Cancel</button>
                      </>
                    ) : (
                      <>
                        <button disabled={editingIndex !== null} onClick={(e) => { e.stopPropagation(); setTempCustomVocab({ ...customVocab }); setEditingIndex(i); }} style={{ background: 'transparent', border: 'none', cursor: editingIndex !== null ? 'not-allowed' : 'pointer', fontSize: '16px', opacity: editingIndex !== null ? 0.5 : 1 }} title="Edit sentence">✏️</button>
                        <button 
                          onClick={(e) => { e.stopPropagation(); playAudio(\`sentences_audio/\${sent.id}.mp3\`); }} 
                          style={{ background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '20px' }}
                          title="Play sentence"
                        >
                          🔊
                        </button>
                      </>
                    )}
                  </div>
                </div>`;

const newRendering = `<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <p style={{ margin: 0, fontSize: '20px', lineHeight: '1.6', color: 'var(--text-h)' }}
                     dangerouslySetInnerHTML={{ __html: parseSentence(sent.sv, sent.target_words, sent.secondary_words) }}
                  />
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <button 
                      onClick={(e) => { e.stopPropagation(); playAudio(\`sentences_audio/\${sent.id}.mp3\`); }} 
                      style={{ background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '20px' }}
                      title="Play sentence"
                    >
                      🔊
                    </button>
                  </div>
                </div>`;

content = content.replace(renderingToReplace, newRendering);

// 10. add learning-modal at the bottom
const modalHtml = `
      {isLearningModalOpen && (
        <div className="learning-modal-overlay" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="learning-modal" style={{ background: 'var(--bg)', padding: '24px', borderRadius: '12px', width: '400px', maxWidth: '90%', border: '1px solid var(--border)' }}>
            <h3 style={{ marginTop: 0 }}>Learning Modal</h3>
            <textarea 
              value={vocabInput} 
              onChange={e => setVocabInput(e.target.value)} 
              rows={5} 
              style={{ width: '100%', marginBottom: '16px', padding: '8px', borderRadius: '8px', background: 'var(--glass-bg)', color: 'var(--text)', border: '1px solid var(--border)' }} 
              placeholder="Enter vocabulary words..." 
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
              <button onClick={() => setIsLearningModalOpen(false)} style={{ padding: '8px 16px', borderRadius: '8px', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', cursor: 'pointer' }}>Cancel</button>
              <button onClick={saveLearningModal} style={{ padding: '8px 16px', borderRadius: '8px', background: 'var(--accent)', border: 'none', color: 'white', cursor: 'pointer' }}>Save</button>
            </div>
          </div>
        </div>
      )}`;

content = content.replace(
  `      {selectedWord && courseId && editingIndex === null && (`,
  modalHtml + `\n\n      {selectedWord && courseId && (`
);

content = content.replace(`&& editingIndex === null `, ``);

fs.writeFileSync(path, content);
console.log('updated Narration');
