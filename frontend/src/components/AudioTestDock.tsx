import { useState } from 'react';
import {
  getPreferredTtsEngine,
  setPreferredTtsEngine,
  playAppleWebSpeech,
  playGoogleTTSStream,
  playStudioR2,
  type TtsEngine
} from '../utils/sound';

export default function AudioTestDock() {
  const [engine, setEngine] = useState<TtsEngine>(getPreferredTtsEngine());
  const [customWord, setCustomWord] = useState('trötta');
  const [statusLog, setStatusLog] = useState<string>('Ready. Click a test button below.');
  const [isExpanded, setIsExpanded] = useState(true);

  const handleEngineChange = (newEngine: TtsEngine) => {
    setEngine(newEngine);
    setPreferredTtsEngine(newEngine);
    setStatusLog(`Active Engine set to: ${newEngine === 'apple' ? '🍏 Apple Alva (Premium)' : '🌐 Google Stream'}`);
  };

  const testAlvaPremium = async (word: string) => {
    setStatusLog(`Playing "${word}" via 🍏 Apple Alva (Premium)...`);
    const res = await playAppleWebSpeech(word, 'Alva (Premium)');
    if (res.ok) {
      setStatusLog(`🔊 Played "${word}" via 🍏 Apple Alva (Premium)`);
    } else {
      setStatusLog(`❌ Error: ${res.error || 'Failed'}`);
    }
  };

  const testAlvaStandard = async (word: string) => {
    setStatusLog(`Playing "${word}" via 🍏 Apple Alva (Standard)...`);
    const res = await playAppleWebSpeech(word, 'Alva');
    if (res.ok) {
      setStatusLog(`🔊 Played "${word}" via 🍏 Apple Alva (Standard)`);
    } else {
      setStatusLog(`❌ Error: ${res.error || 'Failed'}`);
    }
  };

  const testGoogle = async (word: string) => {
    setStatusLog(`Playing "${word}" via 🌐 Google Stream...`);
    const res = await playGoogleTTSStream(word);
    if (res.ok) {
      setStatusLog(`🔊 Played "${word}" via 🌐 Google Stream`);
    } else {
      setStatusLog(`❌ Error: ${res.error || 'Failed'}`);
    }
  };

  const testStudio = async (word: string) => {
    setStatusLog(`Playing "${word}" via 🎵 Studio MP3...`);
    const res = await playStudioR2(word);
    if (res.ok) {
      setStatusLog(`🎵 Played "${word}.mp3" (Studio Recording)`);
    } else {
      setStatusLog(`❌ 404: No studio MP3 found for "${word}"`);
    }
  };

  return (
    <div style={{
      marginTop: '2.5rem',
      marginBottom: '2rem',
      padding: '1.25rem 1.5rem',
      borderRadius: '16px',
      background: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(148, 163, 184, 0.2)',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
      color: '#f8fafc',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: isExpanded ? '1rem' : '0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '1.25rem' }}>🎧</span>
          <strong style={{ fontSize: '1rem', fontWeight: 600, color: '#e2e8f0' }}>Swedish Audio Engine Dock</strong>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            fontSize: '0.875rem'
          }}
        >
          {isExpanded ? 'Collapse ▲' : 'Expand ▼'}
        </button>
      </div>

      {isExpanded && (
        <>
          {/* Active Engine Selector */}
          <div style={{ marginBottom: '1.25rem', display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.85rem', color: '#94a3b8', marginRight: '4px' }}>App Default Engine:</span>
            <button
              onClick={() => handleEngineChange('apple')}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                fontWeight: engine === 'apple' || engine === 'auto' ? 600 : 400,
                background: engine === 'apple' || engine === 'auto' ? '#6366f1' : 'rgba(255, 255, 255, 0.06)',
                color: '#fff',
                border: engine === 'apple' || engine === 'auto' ? '1px solid #818cf8' : '1px solid rgba(255, 255, 255, 0.1)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              🍏 Apple Alva (Native macOS)
            </button>

            <button
              onClick={() => handleEngineChange('google')}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                fontWeight: engine === 'google' ? 600 : 400,
                background: engine === 'google' ? '#0ea5e9' : 'rgba(255, 255, 255, 0.06)',
                color: '#fff',
                border: engine === 'google' ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.1)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              🌐 Google Stream
            </button>
          </div>

          {/* Quick Word Comparison Grid */}
          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '8px' }}>Direct Word Comparison:</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
              {/* trötta */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '10px 14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.95rem', color: '#f8fafc', marginBottom: '6px' }}>"trötta"</div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button onClick={() => testAlvaPremium('trötta')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#6366f1', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🍏 Alva Premium
                  </button>
                  <button onClick={() => testAlvaStandard('trötta')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#4338ca', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🍏 Alva Standard
                  </button>
                  <button onClick={() => testGoogle('trötta')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#0284c7', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🌐 Google
                  </button>
                </div>
              </div>

              {/* konditional */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '10px 14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.95rem', color: '#f8fafc', marginBottom: '6px' }}>"konditional"</div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button onClick={() => testStudio('konditional')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#059669', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🎵 Studio MP3
                  </button>
                  <button onClick={() => testAlvaPremium('konditional')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#6366f1', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🍏 Alva Premium
                  </button>
                  <button onClick={() => testGoogle('konditional')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#0284c7', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🌐 Google
                  </button>
                </div>
              </div>

              {/* Hör av dig snart! */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '10px 14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.95rem', color: '#f8fafc', marginBottom: '6px' }}>"Hör av dig snart!"</div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button onClick={() => testStudio('Hör av dig snart!')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#059669', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🎵 Studio MP3
                  </button>
                  <button onClick={() => testAlvaPremium('Hör av dig snart!')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#6366f1', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🍏 Alva Premium
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Custom Word Input */}
          <div style={{ marginBottom: '1.25rem', display: 'flex', gap: '8px', alignItems: 'center' }}>
            <input
              type="text"
              value={customWord}
              onChange={(e) => setCustomWord(e.target.value)}
              placeholder="Type any Swedish word/phrase to test..."
              style={{
                flex: 1,
                padding: '8px 14px',
                borderRadius: '8px',
                background: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid rgba(148, 163, 184, 0.3)',
                color: '#fff',
                fontSize: '0.9rem',
                outline: 'none'
              }}
            />
            <button
              onClick={() => testAlvaPremium(customWord)}
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                background: '#6366f1',
                color: '#fff',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: 500
              }}
            >
              🍏 Alva Premium
            </button>
            <button
              onClick={() => testAlvaStandard(customWord)}
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                background: '#4338ca',
                color: '#fff',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: 500
              }}
            >
              🍏 Alva Standard
            </button>
            <button
              onClick={() => testGoogle(customWord)}
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                background: '#0ea5e9',
                color: '#fff',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: 500
              }}
            >
              🌐 Google
            </button>
            <button
              onClick={() => testStudio(customWord)}
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                background: '#10b981',
                color: '#fff',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: 500
              }}
            >
              🎵 Studio
            </button>
          </div>

          {/* Diagnostic Console Log */}
          <div style={{
            background: 'rgba(0, 0, 0, 0.6)',
            borderRadius: '8px',
            padding: '10px 14px',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            fontSize: '0.85rem'
          }}>
            <div style={{ color: '#94a3b8', marginBottom: '4px', fontSize: '0.75rem' }}>Live Diagnostic Status:</div>
            <div style={{ color: '#38bdf8', fontFamily: 'monospace' }}>
              {statusLog}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
