import { useEffect, useState } from 'react';

export function FSRSToast() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleSync = (e: CustomEvent) => {
      setMessage(e.detail || 'Synced to Cloud');
      setTimeout(() => setMessage(''), 3000);
    };
    window.addEventListener('fsrs-sync', handleSync as EventListener);
    return () => window.removeEventListener('fsrs-sync', handleSync as EventListener);
  }, []);

  if (!message) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      background: 'var(--accent)',
      color: 'white',
      padding: '12px 24px',
      borderRadius: '8px',
      boxShadow: 'var(--glass-shadow)',
      zIndex: 9999,
      fontWeight: 600
    }}>
      ☁️ {message}
    </div>
  );
}
