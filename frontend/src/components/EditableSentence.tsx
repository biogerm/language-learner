import React, { useState, useMemo } from 'react';
import { global_dict } from '../data/global_dict';

interface CustomVocabWord {
    sv: string;
    en: string;
    stage: string;
    article: string;
    course_id?: string;
    timestamp: number;
}

interface EditableSentenceProps {
    sent: any;
    combinedWords: any[];
    courseId: string;
    stage: string;
    article: string;
    onSaveComplete: () => void;
    onCancel: () => void;
}

export default function EditableSentence({ sent, combinedWords, courseId, stage, article, onSaveComplete, onCancel }: EditableSentenceProps) {
    // We load the current state from localStorage
    const [customVocab, setCustomVocab] = useState<CustomVocabWord[]>(() => {
        try { return JSON.parse(localStorage.getItem('customVocab') || '[]'); } catch { return []; }
    });
    const [excludedVocab, setExcludedVocab] = useState<string[]>(() => {
        try { return JSON.parse(localStorage.getItem('excludedVocab') || '[]'); } catch { return []; }
    });

    const [toggledStates, setToggledStates] = useState<Record<string, boolean>>({});
    const [queue, setQueue] = useState<any[]>([]);
    const [queueIndex, setQueueIndex] = useState(0);
    const [userTranslation, setUserTranslation] = useState("");

    // Build the interactive nodes
    const { nodes, hasChanges } = useMemo(() => {
        let allWords: any[] = [];
        if (sent.target_words) {
            allWords.push(...sent.target_words.map((w: any) => typeof w === 'string' ? { word: w, type: 'target' } : { ...w, type: 'target' }));
        }
        if (sent.secondary_words) {
            allWords.push(...sent.secondary_words.map((w: any) => typeof w === 'string' ? { word: w, type: 'secondary' } : { ...w, type: 'secondary' }));
        }
        
        const hasPositions = allWords.length > 0 && allWords.every(w => w.position_start !== undefined && w.position_end !== undefined);
        
        let localNodes: React.ReactNode[] = [];
        let anyChanged = false;

        const processToken = (token: string, keyPrefix: string) => {
            if (/^\s+$/.test(token)) return <span key={keyPrefix}>{token}</span>;
            const cleanWord = token.replace(/[.,!?;:()[\]{}"”]/g, "").trim();
            if (!cleanWord) return <span key={keyPrefix}>{token}</span>;
            
            const baseWordLower = cleanWord.toLowerCase();
            const isGloballyCustom = customVocab.some(v => v.sv.toLowerCase() === baseWordLower);
            
            const initialState = isGloballyCustom;
            const currentState = toggledStates[baseWordLower] ?? initialState;
            
            if (currentState !== initialState) anyChanged = true;

            return (
                <span 
                    key={keyPrefix} 
                    className={`selectable-word ${currentState ? 'selected-word' : ''}`}
                    style={{ 
                        cursor: 'pointer', borderRadius: '4px', padding: '0 2px', 
                        background: currentState ? 'rgba(239, 68, 68, 0.2)' : 'transparent', 
                        textDecoration: currentState ? 'underline' : 'none', 
                        color: currentState ? '#ef4444' : 'inherit' 
                    }}
                    onClick={(e) => {
                        e.stopPropagation();
                        setToggledStates(prev => ({ ...prev, [baseWordLower]: !currentState }));
                    }}
                >
                    {token}
                </span>
            );
        };

        const processPredefined = (w: any, exactWord: string, keyPrefix: string) => {
            const baseWord = w.base_form || w.word || w.word_in_sentence || exactWord;
            const baseWordLower = baseWord.toLowerCase();
            
            let initialState = false;
            if (w.type === 'secondary') {
                initialState = customVocab.some(v => v.sv.toLowerCase() === baseWordLower);
            } else if (w.type === 'target') {
                initialState = !excludedVocab.includes(baseWordLower);
            }

            const currentState = toggledStates[baseWordLower] ?? initialState;
            if (currentState !== initialState) anyChanged = true;

            return (
                <span 
                    key={keyPrefix} 
                    className={`selectable-word ${currentState ? (w.type === 'secondary' ? 'selected-secondary-word' : 'selected-word') : ''}`}
                    style={{ 
                        cursor: 'pointer', borderRadius: '4px', padding: '0 2px', 
                        background: currentState ? (w.type === 'secondary' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)') : 'transparent', 
                        textDecoration: currentState ? 'underline' : 'none', 
                        color: currentState ? (w.type === 'secondary' ? '#f59e0b' : '#ef4444') : 'inherit' 
                    }}
                    onClick={(e) => {
                        e.stopPropagation();
                        setToggledStates(prev => ({ ...prev, [baseWordLower]: !currentState }));
                    }}
                >
                    {exactWord}
                </span>
            );
        };

        if (hasPositions) {
            allWords.sort((a, b) => a.position_start - b.position_start);
            let currentIndex = 0;
            
            allWords.forEach((w, wIdx) => {
                if (w.position_start >= currentIndex) {
                    let beforeText = sent.sv.substring(currentIndex, w.position_start);
                    if (beforeText) {
                        beforeText.split(/(\s+)/).forEach((token: string, tIdx: number) => {
                            localNodes.push(processToken(token, `before-${wIdx}-${tIdx}`));
                        });
                    }
                    
                    let exactWord = sent.sv.substring(w.position_start, w.position_end);
                    localNodes.push(processPredefined(w, exactWord, `word-${wIdx}`));
                    currentIndex = w.position_end;
                }
            });
            
            let afterText = sent.sv.substring(currentIndex);
            if (afterText) {
                afterText.split(/(\s+)/).forEach((token: string, tIdx: number) => {
                    localNodes.push(processToken(token, `after-${tIdx}`));
                });
            }
        } else {
            sent.sv.split(/(\s+)/).forEach((token: string, tIdx: number) => {
                const cleanWord = token.replace(/[.,!?;:()[\]{}"”]/g, "").trim();
                const baseWordLower = cleanWord.toLowerCase();
                const predefined = combinedWords.find(w => (w.base_form?.toLowerCase() === baseWordLower || w.word?.toLowerCase() === baseWordLower));
                if (predefined && cleanWord) {
                    localNodes.push(processPredefined(predefined, token, `all-${tIdx}`));
                } else {
                    localNodes.push(processToken(token, `all-${tIdx}`));
                }
            });
        }

        return { nodes: localNodes, hasChanges: anyChanged };
    }, [sent, combinedWords, customVocab, excludedVocab, toggledStates]);


    const handleSave = () => {
        let newCustom = [...customVocab];
        let newExcluded = [...excludedVocab];
        let newQueue: any[] = [];
        
        let excludedChanged = false;
        let customChanged = false;

        Object.keys(toggledStates).forEach(baseWordLower => {
            const currentState = toggledStates[baseWordLower];
            
            const isTarget = combinedWords.some(w => w.type === 'target' && (w.base_form?.toLowerCase() === baseWordLower || w.word?.toLowerCase() === baseWordLower));
            const isSecondary = combinedWords.some(w => w.type === 'secondary' && (w.base_form?.toLowerCase() === baseWordLower || w.word?.toLowerCase() === baseWordLower));
            
            const originalW = combinedWords.find(w => (w.base_form?.toLowerCase() === baseWordLower || w.word?.toLowerCase() === baseWordLower));
            const svWord = originalW ? (originalW.base_form || originalW.word) : baseWordLower;

            if (isTarget) {
                if (currentState) {
                    if (newExcluded.includes(baseWordLower)) {
                        newExcluded = newExcluded.filter(v => v !== baseWordLower);
                        excludedChanged = true;
                    }
                } else {
                    if (!newExcluded.includes(baseWordLower)) {
                        newExcluded.push(baseWordLower);
                        excludedChanged = true;
                    }
                }
            } else if (isSecondary) {
                if (currentState) {
                    let contextual = originalW?.contextual_en || "";
                    let globalEn = (global_dict as any)[baseWordLower] || "";
                    let translationStr = "";
                    if (contextual && globalEn && contextual !== globalEn) translationStr = `${contextual} (${globalEn})`;
                    else if (contextual) translationStr = `${contextual}`;
                    else translationStr = globalEn || "No translation";

                    // Only add if not already in customVocab
                    if (!newCustom.some(v => v.sv.toLowerCase() === baseWordLower)) {
                        newCustom.push({
                            sv: svWord,
                            en: translationStr,
                            stage, article, course_id: courseId, timestamp: Date.now()
                        });
                        customChanged = true;
                    }
                } else {
                    const prevLen = newCustom.length;
                    newCustom = newCustom.filter(v => v.sv.toLowerCase() !== baseWordLower);
                    if (newCustom.length < prevLen) customChanged = true;
                }
            } else {
                if (currentState) {
                    if (!newCustom.some(v => v.sv.toLowerCase() === baseWordLower)) {
                        let globalEn = (global_dict as any)[baseWordLower] || "";
                        if (globalEn) {
                            newCustom.push({
                                sv: svWord,
                                en: globalEn,
                                stage, article, course_id: courseId, timestamp: Date.now()
                            });
                            customChanged = true;
                        } else {
                            newQueue.push({
                                sv: svWord,
                                stage, article, course_id: courseId,
                                context_sv: sent.sv,
                                context_en: sent.en || ""
                            });
                        }
                    }
                } else {
                    const prevLen = newCustom.length;
                    newCustom = newCustom.filter(v => v.sv.toLowerCase() !== baseWordLower);
                    if (newCustom.length < prevLen) customChanged = true;
                }
            }
        });

        if (excludedChanged) localStorage.setItem('excludedVocab', JSON.stringify(newExcluded));
        if (customChanged) localStorage.setItem('customVocab', JSON.stringify(newCustom));
        
        setCustomVocab(newCustom);
        setExcludedVocab(newExcluded);

        if (newQueue.length > 0) {
            setQueue(newQueue);
            setQueueIndex(0);
        } else {
            if (excludedChanged || customChanged) {
                window.dispatchEvent(new Event('vocabUpdated'));
            }
            onSaveComplete();
        }
    };

    const handleQueueSubmit = () => {
        if (!userTranslation.trim()) return;
        const currentItem = queue[queueIndex];
        
        const newCustom = [...customVocab];
        newCustom.push({
            sv: currentItem.sv,
            en: userTranslation,
            stage: currentItem.stage,
            article: currentItem.article,
            course_id: currentItem.course_id,
            timestamp: Date.now()
        });
        localStorage.setItem('customVocab', JSON.stringify(newCustom));
        setCustomVocab(newCustom);
        setUserTranslation("");

        if (queueIndex + 1 < queue.length) {
            setQueueIndex(queueIndex + 1);
        } else {
            setQueue([]);
            window.dispatchEvent(new Event('vocabUpdated'));
            onSaveComplete();
        }
    };

    return (
        <div style={{ position: 'relative' }}>
            <div style={{ margin: 0, fontSize: '20px', lineHeight: '1.6', color: 'var(--text-h)' }}>
                {nodes}
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '12px' }}>
                {hasChanges && <button className="btn-primary" style={{ padding: '6px 12px', fontSize: '14px' }} onClick={handleSave}>Save</button>}
                <button className="btn-primary" style={{ padding: '6px 12px', fontSize: '14px', background: 'transparent', color: 'var(--text)', border: '1px solid var(--border)' }} onClick={onCancel}>Cancel</button>
            </div>

            {queue.length > 0 && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
                    background: 'rgba(0,0,0,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
                }}>
                    <div className="glass-panel" style={{ padding: '24px', width: '400px', maxWidth: '90vw', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <h3 style={{ margin: 0, color: 'white', textAlign: 'center' }}>Translate "{queue[queueIndex].sv}"</h3>
                        <p style={{ margin: 0, color: '#9ca3af', fontStyle: 'italic' }}>"{queue[queueIndex].context_sv}"</p>
                        <p style={{ margin: 0, color: '#9ca3af' }}>{queue[queueIndex].context_en}</p>
                        
                        <input 
                            autoFocus
                            type="text" 
                            placeholder="Enter English translation..."
                            value={userTranslation}
                            onChange={e => setUserTranslation(e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter') handleQueueSubmit(); }}
                            style={{ 
                                width: '100%', padding: '12px', fontSize: '16px', 
                                borderRadius: '8px', border: '1px solid var(--border)', 
                                background: 'rgba(255,255,255,0.1)', color: 'white', outline: 'none' 
                            }}
                        />
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ color: '#9ca3af', fontSize: '14px' }}>{queueIndex + 1} of {queue.length}</span>
                            <button className="btn-primary" onClick={handleQueueSubmit} disabled={!userTranslation.trim()}>Next</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
