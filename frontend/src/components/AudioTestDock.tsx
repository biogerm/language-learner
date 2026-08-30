import { useState, useEffect } from 'react';
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
  const [customWord, setCustomWord] = useState('trotta');
  const [statusLog, setStatusLog] = useState<string>('Ready. Click a test button below to listen.');
  const [availableVoices, setAvailableVoices] = useState<string[]>([]);
  const [isExpanded, setIsExpanded] = useState(true);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const updateVoices = () => {
        const voices = window.speechSynthesis.getVoices();
        const sv = voices
          .filter(v => v.lang.toLowerCase().includes('sv') || v.name.toLowerCase().includes('alva') || v.name.toLowerCase().includes('swedish'))
          .map(v => `${v.name} (${v.lang})`);
        setAvailableVoices(sv);
      };
      updateVoices();
      window.speechSynthesis.onvoiceschanged = updateVoices;
    }
  }, []);

  const handleEngineChange = (newEngine: TtsEngine) => {
    setEngine(newEngine);
    setPreferredTtsEngine(newEngine);
    setStatusLog(`Switched global TTS Engine to: ${newEngine.toUpperCase()}`);
  };

  const testApple = async (word: string) => {
    setStatusLog(`Testing Apple Native Web Speech for "${word}"...`);
    const res = await playAppleWebSpeech(word);
    if (res.ok) {
      setStatusLog(`🔊 Apple Web Speech: Played "${word}" via [${res.voice || 'sv-SE'}]`);
    } else {
      setStatusLog(`❌ Apple Web Speech Error: ${res.error || 'Failed'}`);
    }
  };

  const testGoogle = async (word: string) => {
    setStatusLog(`Testing Google Cloud Stream for "${word}"...`);
    const res = await playGoogleTTSStream(word);
    if (res.ok) {
      setStatusLog(`🔊 Google Cloud Stream: Played "${word}" (200 OK)`);
    } else {
      setStatusLog(`❌ Google Cloud Stream Error: ${res.error || 'Failed'}`);
    }
  };

  const testStudio = async (word: string) => {
    setStatusLog(`Testing Studio R2 MP3 for "${word}"...`);
    const res = await playStudioR2(word);
    if (res.ok) {
      setStatusLog(`🎵 Studio R2 MP3: Played "${word}.mp3" (200 OK)`);
    } else {
      setStatusLog(`❌ Studio R2 Error: ${res.error || '404'}`);
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
          <strong style={{ fontSize: '1rem', fontWeight: 600, color: '#e2e8f0' }}>Audio Engine Cross-Browser Test Bench</strong>
          <span style={{
            fontSize: '0.75rem',
            padding: '2px 8px',
            borderRadius: '9999px',
            background: 'rgba(59, 130, 246, 0.2)',
            color: '#60a5fa',
            border: '1px solid rgba(59, 130, 246, 0.4)'
          }}>
            Multi-Engine
          </span>
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
            <span style={{ fontSize: '0.85rem', color: '#94a3b8', marginRight: '4px' }}>Active Engine:</span>
            <button
              onClick={() => handleEngineChange('apple')}
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                fontWeight: engine === 'apple' ? 600 : 400,
                background: engine === 'apple' ? '#6366f1' : 'rgba(255, 255, 255, 0.06)',
                color: '#fff',
                border: engine === 'apple' ? '1px solid #818cf8' : '1px solid rgba(255, 255, 255, 0.1)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              🍏 Apple System (Alva / Web Speech)
            </button>

            <button
              onClick={() => handleEngineChange('google')}
              style={{
                padding: '6px 12px',
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
              🌐 Google Cloud Stream (/api/tts)
            </button>

            <button
              onClick={() => handleEngineChange('auto')}
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                fontWeight: engine === 'auto' ? 600 : 400,
                background: engine === 'auto' ? '#10b981' : 'rgba(255, 255, 255, 0.06)',
                color: '#fff',
                border: engine === 'auto' ? '1px solid #34d399' : '1px solid rgba(255, 255, 255, 0.1)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              ⚡ Auto (Stream + Fallback)
            </button>
          </div>

          {/* Quick Word Comparison Grid */}
          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '8px' }}>Compare Preset Words Across Engines:</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
              {/* trotta */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '10px 14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.95rem', color: '#f8fafc', marginBottom: '6px' }}>"trotta" (No Studio MP3)</div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button onClick={() => testApple('trotta')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#4338ca', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🍏 Apple Alva
                  </button>
                  <button onClick={() => testGoogle('trotta')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#0284c7', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🌐 Google Stream
                  </button>
                </div>
              </div>

              {/* trötta */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '10px 14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.95rem', color: '#f8fafc', marginBottom: '6px' }}>"trötta" (No Studio MP3)</div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button onClick={() => testApple('trötta')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#4338ca', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🍏 Apple Alva
                  </button>
                  <button onClick={() => testGoogle('trötta')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#0284c7', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🌐 Google Stream
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
                  <button onClick={() => testApple('Hör av dig snart!')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#4338ca', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🍏 Apple Alva
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
                  <button onClick={() => testGoogle('konditional')} style={{ flex: 1, padding: '5px 8px', borderRadius: '6px', fontSize: '0.75rem', background: '#0284c7', color: '#fff', border: 'none', cursor: 'pointer' }}>
                    🌐 Google Stream
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
              onClick={() => testApple(customWord)}
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
              🍏 Play Apple
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
              🌐 Play Google
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
              🎵 Try Studio
            </button>
          </div>

          {/* Diagnostic Console Log */}
          <div style={{
            background: 'rgba(0, 0, 0, 0.6)',
            borderRadius: '8px',
            padding: '10px 14px',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            fontSize: '0.85rem',
            marginBottom: '1rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', marginBottom: '4px', fontSize: '0.75rem' }}>
              <span>Live Diagnostic Output</span>
              <span>Swedish System Voices Detected: {availableVoices.length > 0 ? availableVoices.join(', ') : 'None (Browser default)'}</span>
            </div>
            <div style={{ color: '#38bdf8', fontFamily: 'monospace' }}>
              {statusLog}
            </div>
          </div>

          {/* Browser & Pronunciation Tips */}
          <div style={{
            padding: '10px 14px',
            borderRadius: '8px',
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            fontSize: '0.8rem',
            color: '#94a3b8',
            lineHeight: 1.5
          }}>
            <div style={{ fontWeight: 600, color: '#cbd5e1', marginBottom: '4px' }}>💡 Audio Engine Tips:</div>
            <div>• <strong>Why Apple Alva was silent in Chrome:</strong> Chrome sandbox blocks macOS system voices if they are not installed locally. To enable Alva in Chrome: <em>macOS System Settings → Accessibility → Spoken Content → System Voice → Download "Alva"</em>. (Arc and Safari have native macOS voice entitlements).</div>
            <div>• <strong>Swedish Pronunciation:</strong> Be sure to test with authentic Swedish characters like <strong>"trötta"</strong> (with <em>ö</em>). Testing non-Swedish spelling like <em>"trotta"</em> causes TTS to read it with English phonemes.</div>
          </div>
        </>
      )}
    </div>
  );
}
