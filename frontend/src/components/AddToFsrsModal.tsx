import { useState, useEffect } from 'react';
import { db } from '../db/dexie';
import { global_dict } from '../data/global_dict';
import { useData } from '../contexts/DataContext';

interface AddToFsrsModalProps {
  courseId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function AddToFsrsModal({ courseId, isOpen, onClose }: AddToFsrsModalProps) {
  const [word, setWord] = useState('');
  const [translation, setTranslation] = useState('');
  const [step, setStep] = useState(1); // 1: input word, 2: confirm/add translation, 3: success
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const { courseData } = useData();
  const [result, setResult] = useState<{ found_in: 'course' | 'global' | 'custom' | 'existing'; en: string; sentence?: string; sentence_en?: string; due?: string } | null>(null);
  const [addedCount, setAddedCount] = useState(0);

  // Reset state whenever the modal closes so reopening always starts at step 1
  useEffect(() => {
    if (!isOpen) {
      setStep(1);
      setWord('');
      setTranslation('');
      setMessage('');
      setResult(null);
      setLoading(false);
    }
  }, [isOpen]);

  // Check if word exists in course data (with example sentence)
  // Primary source: Dexie course_data.dictionary[] (rich entries with base_form, sentence_id, en_translation)
  // Fallback: in-memory courseData (stages schema or legacy object schema)
  const findInCourseData = async (inputWord: string) => {
    const lowerInput = inputWord.toLowerCase();
    // 1) Dexie dictionary — authoritative, has base_form + translations + sentence ids
    try {
      const rows = await db.course_data.toArray();
      for (const cd of rows) {
        if (Array.isArray(cd.dictionary)) {
          const hit = cd.dictionary.find((d: any) => d.base_form?.toLowerCase() === lowerInput);
          if (hit) {
            // resolve example sentence sv/en from articles if possible
            let sv = '', en = '';
            const stages = (cd.articles as any)?.stages;
            if (Array.isArray(stages)) {
              outer: for (const stage of stages) {
                for (const article of stage.articles || []) {
                  for (const sentence of article.sentences || []) {
                    if (sentence.sentence_id === hit.sentence_id) {
                      sv = sentence.sv; en = sentence.en;
                      break outer;
                    }
                  }
                }
              }
            }
            return {
              word: hit.base_form,
              en: hit.en_translation || hit.contextual_en || '',
              sentence: sv,
              sentence_en: en,
              hasExample: Boolean(sv)
            };
          }
        }
      }
    } catch { /* Dexie unavailable — fall through to memory lookup */ }
    // 2) In-memory stages schema
    const stages = courseData?.articles?.stages || (courseData as any)?.stages;
    if (stages) {
      for (const stage of stages) {
        for (const article of stage.articles || []) {
          for (const sentence of article.sentences || []) {
            for (const tw of sentence.target_words || []) {
              if (tw.base_form?.toLowerCase() === lowerInput) {
                return {
                  word: tw.base_form,
                  en: tw.en_translation || tw.contextual_en || '',
                  sentence: sentence.sv,
                  sentence_en: sentence.en,
                  hasExample: true
                };
              }
            }
            for (const sw of sentence.secondary_words || []) {
              if (sw.base_form?.toLowerCase() === lowerInput) {
                return {
                  word: sw.base_form,
                  en: sw.en_translation || sw.contextual_en || '',
                  sentence: sentence.sv,
                  sentence_en: sentence.en,
                  hasExample: true
                };
              }
            }
          }
        }
      }
    }
    // 3) Legacy schema: courseData["Stage X"]["Uppgift Y"] = [{id, sv, en}, ...]
    // Match word inside the Swedish sentence text; example = that sentence.
    const cdAny = courseData as any;
    if (cdAny && !cdAny.stages && !cdAny.articles?.stages) {
      for (const stageKey of Object.keys(cdAny)) {
        const stageObj = cdAny[stageKey];
        if (!stageObj || typeof stageObj !== 'object') continue;
        for (const articleKey of Object.keys(stageObj)) {
          const sentences = stageObj[articleKey];
          if (!Array.isArray(sentences)) continue;
          for (const sentence of sentences) {
            if (!sentence?.sv) continue;
            const re = new RegExp(`\\b${inputWord.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\w*\\b`, 'i');
            const m = sentence.sv.match(re);
            if (m) {
              const strip = (s: string) => s.replace(/<[^>]+>/g, '');
              const wordEn = (global_dict as any)[(m[0] || '').toLowerCase()] || strip(sentence.en || '');
              return {
                word: m[0],
                en: wordEn,
                sentence: strip(sentence.sv),
                sentence_en: strip(sentence.en || ''),
                hasExample: true
              };
            }
          }
        }
      }
    }
    return null;
  };

  const handleAdd = async () => {
    setLoading(true);
    setMessage('');
    try {
      // Step 1: Check course data
      const courseWord = await findInCourseData(word);
      let finalWord = word;

      if (courseWord) {
        // Use the word from course data
        finalWord = courseWord.word;
        setResult({
          found_in: 'course',
          en: courseWord.en,
          sentence: courseWord.sentence,
          sentence_en: courseWord.sentence_en
        });
        // We don't need to save anything extra because the course data already has it.
        // Just add to FSRS.
      } else {
        // Step 2: Check global dictionary
        const lowerWord = word.toLowerCase();
        const globalEn = (global_dict as any)[lowerWord];
        if (globalEn) {
          setResult({ found_in: 'global', en: globalEn });
          // No need to save to custom dictionary because it's in global_dict (without example)
          // But note: the global_dict doesn't have example sentences, so we just add the word.
        } else {
          // Step 3: Not found anywhere, ask for translation
          if (!translation) {
            // Move to step 2 UI to collect the translation from the user
            setStep(2);
            setMessage('');
            setLoading(false);
            return;
          }
          setResult({ found_in: 'custom', en: translation });
          // Save to custom dictionary
          await db.custom_dictionary.add({
            base_form: word,
            word_in_sentence: word, // Since we don't have a sentence, we use the word itself
            en_translation: translation,
            article_id: '', // Not tied to an article
            stage_id: '', // Not tied to a stage
            course_id: courseId,
            sentence: '', // No example sentence
            sentence_en: '',
            synced: false
          } as any);
        }
      }

      // Add to FSRS progress
      // state=2 (Review) so the word enters the review flow immediately — no waiting.
      // CRITICAL: normalize word_id to lowercase. Every other path (submitGatePass,
      // queueBuilder, sync) keys fsrs by lowercase. If a user typed "Förmån" and we
      // stored it verbatim, answering correctly would update the lowercase row while
      // the capitalized row stays due forever -> word repeats infinitely in review.
      finalWord = finalWord.trim().toLowerCase();
      const existing =
        (await db.fsrs_progress.get(finalWord)) ??
        (await db.fsrs_progress.where('word_id').equalsIgnoreCase(finalWord).first());
      let dueStr = '';
      if (!existing) {
        const now = new Date();
        await db.fsrs_progress.put({
          word_id: finalWord,
          course_id: courseId,
          state: 2,
          due: now,
          stability: 0.5,
          difficulty: 5,
          elapsed_days: 0,
          scheduled_days: 0,
          reps: 0,
          lapses: 0,
          last_review: now,
          lastGatePassDate: now.toISOString(),
          synced: false
        });
        dueStr = 'now';
        // Trigger sync event + queue refresh so the new word appears in the live review session
        window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Added ${finalWord} to queue` }));
        window.dispatchEvent(new CustomEvent('learning-queue-updated'));
      } else {
        dueStr = new Date(existing.due).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
        setResult(r => (r ? { ...r, found_in: 'existing', due: dueStr } : r));
      }

      setStep(3);
      setMessage(`Added "${finalWord}" to review queue`);
      if (result?.found_in !== 'existing') setAddedCount(c => c + 1);
    } catch (err) {
      console.error('Failed to add word to FSRS:', err);
      setMessage('Failed to add word. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const sourceMeta: Record<string, { icon: string; label: string; note: string; color: string }> = {
    course:   { icon: '📖', label: 'Found in course',        note: 'This word comes with an example sentence from your course.', color: '#34d399' },
    global:   { icon: '📚', label: 'Found in dictionary',    note: 'General dictionary word — no course example sentence available.', color: '#60a5fa' },
    custom:   { icon: '✏️', label: 'Custom word',            note: 'Not in any dictionary — saved to your custom word list with your translation.', color: '#fbbf24' },
    existing: { icon: '🔁', label: 'Already in review',      note: 'This word is already in your FSRS queue — nothing changed.', color: '#a78bfa' }
  };
  const meta = result ? sourceMeta[result.found_in] : null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'flex-start', justifyContent: 'center', zIndex: 1000,
      paddingTop: '120px', animation: 'fadeIn 0.15s ease', overflowY: 'auto'
    }}>
      <div className="glass-panel" style={{
        padding: '28px', width: '420px', maxWidth: '92vw', display: 'flex', flexDirection: 'column', gap: '14px',
        borderRadius: '16px', boxShadow: '0 20px 60px rgba(0,0,0,0.5)', animation: 'slideUp 0.2s ease',
        marginBottom: '40px'
      }}>
        {step === 1 && (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '22px' }}>➕</span>
              <h3 style={{ margin: 0, fontSize: '17px' }}>Add Word to Review</h3>
              {addedCount > 0 && (
                <span style={{ marginLeft: 'auto', fontSize: '12px', color: '#34d399', fontWeight: 600 }}>
                  ✓ {addedCount} added this session
                </span>
              )}
            </div>
            <p style={{ margin: 0, fontSize: '13px', opacity: 0.75, lineHeight: 1.5 }}>
              Type a Swedish word — we'll check the course, the dictionary, or ask you for a translation.
            </p>
            <input
              type="text"
              placeholder="Swedish word"
              value={word}
              onChange={(e) => setWord(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleAdd(); }}
              autoFocus
              style={{ width: '100%', padding: '14px 16px', fontSize: '17px', borderRadius: '10px', border: '1px solid var(--border)', background: 'rgba(255,255,255,0.1)', color: 'white', outline: 'none', boxSizing: 'border-box' }}
            />
            <button className="btn-primary" onClick={handleAdd} disabled={loading || !word.trim()} style={{ padding: '12px 16px', width: '100%', borderRadius: '10px', fontSize: '15px', fontWeight: 600 }}>
              {loading ? 'Looking up…' : 'Add to Review'}
            </button>
          </>
        )}
        {step === 2 && (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '22px' }}>✏️</span>
              <h3 style={{ margin: 0, fontSize: '17px' }}>{word}</h3>
            </div>
            <p style={{ margin: 0, fontSize: '13px', opacity: 0.75, lineHeight: 1.5 }}>
              We couldn't find "<strong>{word}</strong>" in the course or the dictionary. What does it mean in English?
            </p>
            <input
              type="text"
              placeholder="English translation"
              value={translation}
              onChange={(e) => setTranslation(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleAdd(); }}
              autoFocus
              style={{ width: '100%', padding: '14px 16px', fontSize: '17px', borderRadius: '10px', border: '1px solid var(--border)', background: 'rgba(255,255,255,0.1)', color: 'white', outline: 'none', boxSizing: 'border-box' }}
            />
            <button className="btn-primary" onClick={handleAdd} disabled={loading || !translation.trim()} style={{ padding: '12px 16px', width: '100%', borderRadius: '10px', fontSize: '15px', fontWeight: 600 }}>
              {loading ? 'Saving…' : 'Save & Add to Review'}
            </button>
          </>
        )}
        {step === 3 && meta && (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '26px' }}>{meta.icon}</span>
              <div>
                <h3 style={{ margin: 0, fontSize: '16px' }}>
                  {result!.found_in === 'existing' ? `"${word}" is already in review` : `"${word}" added to review`}
                </h3>
                <span style={{ fontSize: '12px', color: meta.color, fontWeight: 600 }}>{meta.label}</span>
              </div>
            </div>
            <div style={{
              padding: '12px 14px', borderRadius: '10px', background: 'rgba(255,255,255,0.06)',
              border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: '6px'
            }}>
              <p style={{ margin: 0, fontSize: '13px', opacity: 0.8, lineHeight: 1.5 }}>{meta.note}</p>
              <div style={{ fontSize: '14px', lineHeight: 1.6 }}>
                <span style={{ opacity: 0.6, fontSize: '12px' }}>EN</span>{' '}
                <strong>{result!.en}</strong>
              </div>
              {result!.sentence && (
                <div style={{ fontSize: '13px', lineHeight: 1.6, borderTop: '1px solid var(--border)', paddingTop: '8px' }}>
                  <span style={{ opacity: 0.6 }}>{result!.sentence}</span>
                  {result!.sentence_en && <div style={{ opacity: 0.55, fontStyle: 'italic', fontSize: '12px', marginTop: '2px' }}>{result!.sentence_en}</div>}
                </div>
              )}
            </div>
            <div style={{ fontSize: '12.5px', opacity: 0.7, display: 'flex', alignItems: 'center', gap: '6px' }}>
              🗓️ {result!.found_in === 'existing'
                ? <>Already due — next review <strong style={{ opacity: 1 }}>{result!.due}</strong></>
                : <>In your review queue <strong style={{ opacity: 1 }}>right now</strong> — it will appear in this session's Review flow</>}
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                className="btn-primary"
                onClick={() => {
                  // Continue adding: reset to step 1, keep the modal open
                  setStep(1);
                  setWord('');
                  setTranslation('');
                  setMessage('');
                  setResult(null);
                }}
                style={{ padding: '12px 16px', flex: 1, borderRadius: '10px', fontSize: '14px', fontWeight: 600 }}>
                + Add another
              </button>
              <button
                onClick={onClose}
                style={{ padding: '12px 16px', borderRadius: '10px', fontSize: '14px', fontWeight: 600, background: 'transparent', color: 'var(--text-mute, rgba(255,255,255,0.7))', border: '1px solid var(--border)', cursor: 'pointer' }}>
                Done
              </button>
            </div>
          </>
        )}
        {message && step !== 3 && (
          <p style={{ color: '#ef4444', fontSize: '0.85rem', margin: 0 }}>{message}</p>
        )}
        {step !== 3 && (
          <button onClick={onClose} style={{ padding: '6px 12px', fontSize: '13px', background: 'transparent', color: 'var(--text-mute, rgba(255,255,255,0.6))', border: 'none', cursor: 'pointer', alignSelf: 'center' }}>
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}