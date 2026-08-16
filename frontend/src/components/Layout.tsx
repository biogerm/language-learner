import { Outlet, useNavigate, useLocation, useParams } from 'react-router-dom';

import { FSRSToast } from './FSRSToast';
import { useEffect, useState } from 'react';
import { syncOfflineProgress } from '../utils/fsrs';

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { courseId } = useParams();

  useEffect(() => {
    const handleOnline = () => {
      console.log('App is online. Attempting to sync offline progress.');
      syncOfflineProgress().catch(console.error);
    };
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, []);

  const [appMode, setAppMode] = useState(localStorage.getItem('appMode') || 'study');

  useEffect(() => {
    const handleModeChange = () => setAppMode(localStorage.getItem('appMode') || 'study');
    window.addEventListener('appModeChanged', handleModeChange);
    return () => window.removeEventListener('appModeChanged', handleModeChange);
  }, []);

  const handleModeSwitch = (path: string) => {
    if (courseId) {
      navigate(`/${path}/${courseId}`);
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header className="glass-panel" style={{ 
        margin: '16px', padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        position: 'sticky', top: '16px', zIndex: 100 
      }}>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <h2 style={{ margin: 0, cursor: 'pointer', transition: 'color 0.2s ease' }} 
              onClick={() => navigate('/dashboard')}
              onMouseOver={(e) => e.currentTarget.style.color = 'var(--accent)'}
              onMouseOut={(e) => e.currentTarget.style.color = 'var(--text-h)'}>
            Language Learner
          </h2>
          {courseId && (
            <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
              <div style={{ display: 'flex', background: 'var(--glass-bg)', padding: '4px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                <button 
                  className="hover-scale"
                  onClick={() => {
                    localStorage.setItem('appMode', 'study');
                    window.dispatchEvent(new Event('appModeChanged'));
                    if (!location.pathname.includes('narration') && !location.pathname.includes('dictation') && !location.pathname.includes('flashcard')) {
                      handleModeSwitch('narration');
                    }
                  }}
                  style={{ background: appMode === 'study' ? 'var(--accent)' : 'transparent', color: appMode === 'study' ? 'white' : 'var(--text-h)', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: appMode === 'study' ? 'bold' : 'normal' }}>
                  📚 Study
                </button>
                <button 
                  className="hover-scale"
                  onClick={() => {
                    localStorage.setItem('appMode', 'review');
                    window.dispatchEvent(new Event('appModeChanged'));
                    if (location.pathname.includes('narration')) {
                      handleModeSwitch('flashcard');
                    }
                  }}
                  style={{ background: appMode === 'review' ? 'var(--accent)' : 'transparent', color: appMode === 'review' ? 'white' : 'var(--text-h)', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: appMode === 'review' ? 'bold' : 'normal' }}>
                  📅 Review
                </button>
              </div>

              <div style={{ display: 'flex', background: 'var(--glass-bg)', padding: '4px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                {appMode === 'study' && (
                  <button 
                    className="hover-scale"
                    onClick={() => handleModeSwitch('narration')}
                    style={{ background: location.pathname.includes('narration') ? 'var(--accent)' : 'transparent', color: location.pathname.includes('narration') ? 'white' : 'var(--text-h)', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: location.pathname.includes('narration') ? 'bold' : 'normal' }}>
                    📖 Narration
                  </button>
                )}
                <button 
                  className="hover-scale"
                  onClick={() => handleModeSwitch('dictation')}
                  style={{ background: location.pathname.includes('dictation') ? 'var(--accent)' : 'transparent', color: location.pathname.includes('dictation') ? 'white' : 'var(--text-h)', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: location.pathname.includes('dictation') ? 'bold' : 'normal' }}>
                  🎧 Dictation
                </button>
                <button 
                  className="hover-scale"
                  onClick={() => handleModeSwitch('flashcard')}
                  style={{ background: location.pathname.includes('flashcard') ? 'var(--accent)' : 'transparent', color: location.pathname.includes('flashcard') ? 'white' : 'var(--text-h)', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: location.pathname.includes('flashcard') ? 'bold' : 'normal' }}>
                  📝 Flashcard
                </button>
              </div>
            </div>
          )}
          <button 
            onClick={() => { localStorage.clear(); window.location.href = '/login'; }} 
            style={{ 
              background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-mute)', 
              padding: '6px 12px', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', marginLeft: 'auto' 
            }}
            className="hover-scale"
          >
            Sign Out
          </button>
        </div>
      </header>
      
      <main style={{ flex: 1, padding: '0 16px 16px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div key={appMode} className="reveal-animation" style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
          <Outlet />
        </div>
      </main>
      
      <FSRSToast />
      
      <footer style={{ textAlign: 'center', padding: '16px', color: 'var(--text-mute)', fontSize: '14px' }}>
        Language Learner v1.0.0
      </footer>
    </div>
  );
}
