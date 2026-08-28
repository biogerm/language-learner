import { useEffect, useState, useRef } from 'react';

export function FSRSToast() {
  const [syncMsg, setSyncMsg] = useState('');
  const [toastMsg, setToastMsg] = useState('');
  const [toastVisible, setToastVisible] = useState(false);
  const toastTimeoutRef = useRef<number | null>(null);
  const syncTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    const handleSync = (e: CustomEvent) => {
      setSyncMsg(e.detail || 'Synced to Cloud');
      if (syncTimeoutRef.current) clearTimeout(syncTimeoutRef.current);
      syncTimeoutRef.current = window.setTimeout(() => setSyncMsg(''), 3000);
    };

    const handleToast = (e: CustomEvent) => {
      const msg = typeof e.detail === 'string' ? e.detail : (e.detail?.toastMsg || `${e.detail?.ratingName || 'Good'} | ${e.detail?.dayStr || '1 day'}`);
      if (!msg) return;

      setToastMsg(msg);
      setToastVisible(true);

      if (toastTimeoutRef.current) clearTimeout(toastTimeoutRef.current);
      toastTimeoutRef.current = window.setTimeout(() => {
        setToastVisible(false);
        setTimeout(() => setToastMsg(''), 300);
      }, 2500);
    };

    window.addEventListener('fsrs-sync', handleSync as EventListener);
    window.addEventListener('fsrs-toast', handleToast as EventListener);

    return () => {
      window.removeEventListener('fsrs-sync', handleSync as EventListener);
      window.removeEventListener('fsrs-toast', handleToast as EventListener);
      if (toastTimeoutRef.current) clearTimeout(toastTimeoutRef.current);
      if (syncTimeoutRef.current) clearTimeout(syncTimeoutRef.current);
    };
  }, []);

  return (
    <>
      {/* Floating Center FSRS Rating Toast (replicating L) */}
      {toastMsg && (
        <div 
          id="fsrs-toast"
          className="fsrs-toast"
          style={{
            position: 'fixed',
            top: '25%',
            left: 0,
            right: 0,
            marginLeft: 'auto',
            marginRight: 'auto',
            width: 'fit-content',
            textAlign: 'center',
            background: 'linear-gradient(135deg, rgba(30, 27, 75, 0.95), rgba(49, 46, 129, 0.95))',
            border: '2px solid rgba(167, 139, 250, 0.9)',
            color: '#ffffff',
            padding: '12px 32px',
            borderRadius: '30px',
            fontSize: '1.3rem',
            fontWeight: 800,
            letterSpacing: '0.5px',
            boxShadow: '0 12px 40px rgba(139, 92, 246, 0.6), inset 0 0 16px rgba(192, 132, 252, 0.3)',
            backdropFilter: 'blur(24px)',
            WebkitBackdropFilter: 'blur(24px)',
            zIndex: 10000,
            pointerEvents: 'none',
            opacity: toastVisible ? 1 : 0,
            transform: toastVisible ? 'translateY(0) scale(1)' : 'translateY(12px) scale(0.95)',
            transition: 'opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1), transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)'
          }}
        >
          {toastMsg}
        </div>
      )}

      {/* Cloud Sync Status Badge (Bottom Right) */}
      {syncMsg && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          background: 'var(--accent, #6366f1)',
          color: 'white',
          padding: '10px 20px',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
          zIndex: 9999,
          fontWeight: 600,
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          ☁️ {syncMsg}
        </div>
      )}
    </>
  );
}
