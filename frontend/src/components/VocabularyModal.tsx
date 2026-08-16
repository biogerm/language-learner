import { db } from '../db/dexie';

export default function VocabularyModal({ courseId, word, en, onClose }: { courseId: string, word: string, en: string, onClose: () => void }) {
  const handleAdd = async () => {
    const existing = await db.fsrs_progress.get(word);
    if (!existing) {
      await db.fsrs_progress.put({
        word_id: word,
        course_id: courseId,
        state: 0,
        due: new Date(),
        stability: 0,
        difficulty: 0,
        elapsed_days: 0,
        scheduled_days: 0,
        reps: 0,
        lapses: 0,
        last_review: new Date(),
        synced: false
      });
      window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Added ${word} to queue` }));
    }
    onClose();
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
      background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
    }}>
      <div className="glass-panel" style={{ padding: '24px', width: '300px', maxWidth: '90vw', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <h3 style={{ margin: 0 }}>{word}</h3>
        <p style={{ margin: 0 }}>{en}</p>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn-primary" onClick={handleAdd} style={{ padding: '8px 16px' }}>Add to Queue</button>
          <button className="btn-primary" style={{ padding: '8px 16px', background: 'transparent', color: 'var(--text)', border: '1px solid var(--border)' }} onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
