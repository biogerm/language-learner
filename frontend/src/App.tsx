import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useEffect } from 'react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Narration from './pages/Narration';
import Dictation from './pages/Dictation';
import Flashcard from './pages/Flashcard';
import Layout from './components/Layout';
import './index.css';

import { ErrorBoundary } from './components/ErrorBoundary';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { DataProvider } from './contexts/DataContext';
import { bindAudioUnlock, isAudioDebug } from './utils/sound';

// On-screen audio debug overlay (?audiodebug=1) — shows every audio decision
// on iPad where there is no way to read the console.
function AudioDebugOverlay() {
  if (!isAudioDebug()) return null;
  const logs: string[] = [];
  window.addEventListener('audio-debug', ((e: CustomEvent) => {
    logs.unshift(`[${new Date().toLocaleTimeString()}] ${e.detail}`);
    if (logs.length > 8) logs.pop();
    const el = document.getElementById('audio-debug-overlay');
    if (el) el.textContent = logs.join('\n');
  }) as EventListener);
  return (
    <pre
      id="audio-debug-overlay"
      style={{
        position: 'fixed', bottom: 8, left: 8, zIndex: 99999,
        background: 'rgba(0,0,0,0.85)', color: '#0f0', fontSize: 10,
        padding: 6, maxWidth: '60vw', maxHeight: '30vh', overflow: 'hidden',
        whiteSpace: 'pre-wrap', pointerEvents: 'none', margin: 0
      }}
    />
  );
}

function ProtectedRoute() {
  const { session, loading } = useAuth();

  // iOS Safari: unlock the audio element on first user gesture (touch/key/click)
  useEffect(() => {
    bindAudioUnlock();
  }, []);

  if (loading) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>Loading...</div>;
  }
  
  if (!session) {
    return <Navigate to="/login" replace />;
  }
  
  return <Outlet />;
}

function App() {
  return (
    <ErrorBoundary>
      <AudioDebugOverlay />
      <AuthProvider>
        <DataProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              
              <Route element={<ProtectedRoute />}>
                <Route element={<Layout />}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/narration/:courseId" element={<Narration />} />
                  <Route path="/dictation/:courseId" element={<Dictation />} />
                  <Route path="/flashcard/:courseId" element={<Flashcard />} />
                  <Route path="/course/:courseId/review" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                </Route>
              </Route>
            </Routes>
          </Router>
        </DataProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
