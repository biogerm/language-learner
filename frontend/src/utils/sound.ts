import { getMp3PublicUrl } from '../services/r2';

export type TtsEngine = 'auto' | 'apple' | 'google';

// Cache of words confirmed to have NO studio MP3 on R2
const missingAudioCache = new Set<string>();
let activeAudio: HTMLAudioElement | null = null;

export const getPreferredTtsEngine = (): TtsEngine => {
  if (typeof window === 'undefined') return 'auto';
  return (localStorage.getItem('preferred_tts_engine') as TtsEngine) || 'auto';
};

export const setPreferredTtsEngine = (engine: TtsEngine) => {
  if (typeof window === 'undefined') return;
  localStorage.setItem('preferred_tts_engine', engine);
};

let cachedVoices: SpeechSynthesisVoice[] = [];
let voiceLoadingPromise: Promise<SpeechSynthesisVoice[]> | null = null;

export const loadSwedishVoices = (): Promise<SpeechSynthesisVoice[]> => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return Promise.resolve([]);
  }

  const current = window.speechSynthesis.getVoices();
  if (current && current.length > 0) {
    cachedVoices = current;
    return Promise.resolve(current);
  }

  if (voiceLoadingPromise) return voiceLoadingPromise;

  voiceLoadingPromise = new Promise((resolve) => {
    const handleVoices = () => {
      const v = window.speechSynthesis.getVoices();
      if (v && v.length > 0) {
        cachedVoices = v;
        window.speechSynthesis.removeEventListener('voiceschanged', handleVoices);
        resolve(v);
      }
    };

    window.speechSynthesis.addEventListener('voiceschanged', handleVoices);
    window.speechSynthesis.onvoiceschanged = handleVoices;

    // Timeout fallback in case voiceschanged never triggers
    setTimeout(() => {
      cachedVoices = window.speechSynthesis.getVoices() || [];
      resolve(cachedVoices);
    }, 1500);
  });

  return voiceLoadingPromise;
};

// Start loading voices immediately
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  loadSwedishVoices();
}

export const getBestSwedishVoice = async (): Promise<SpeechSynthesisVoice | undefined> => {
  const voices = await loadSwedishVoices();
  // Priority: Alva (Premium) > Alva (Enhanced) > Alva > Oskar (Premium) > Oskar > any sv voice
  return (
    voices.find(v => v.name.includes('Alva (Premium)')) ||
    voices.find(v => v.name.includes('Alva (Enhanced)')) ||
    voices.find(v => v.name.toLowerCase().includes('alva') && (v.lang.toLowerCase().includes('sv') || v.lang.toLowerCase().includes('se'))) ||
    voices.find(v => v.name.includes('Oskar (Premium)')) ||
    voices.find(v => v.name.includes('Oskar')) ||
    voices.find(v => v.lang.toLowerCase().startsWith('sv') || v.lang.toLowerCase().includes('se'))
  );
};

/**
 * Play via Apple / OS Native Web Speech API (Alva / Oskar in sv-SE)
 * Engineered with full Chrome/Chromium & Safari/Arc compatibility:
 * 1. Asynchronously awaits and binds the exact Alva voice object
 * 2. Retains utterance reference on window to prevent Chromium V8 GC truncation
 * 3. Safely resumes audio context
 */
export const playAppleWebSpeech = async (word: string): Promise<{ ok: boolean; voice?: string; error?: string }> => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return { ok: false, error: 'Web Speech API not supported in this browser' };
  }
  const cleanText = (word || '').replace(/[!?"'.,:;()]/g, ' ').trim();
  if (!cleanText) return { ok: false, error: 'Empty text' };

  try {
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }

    const svVoice = await getBestSwedishVoice();

    return new Promise((resolve) => {
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = 'sv-SE';
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      if (svVoice) {
        utterance.voice = svVoice;
      }

      // CRITICAL FOR CHROME: Store active utterance on window so V8 Garbage Collector does not destroy it mid-speech!
      (window as any).__activeAppleUtterance = utterance;

      let settled = false;
      utterance.onstart = () => {
        if (!settled) {
          settled = true;
          resolve({ ok: true, voice: svVoice ? svVoice.name : 'System Swedish' });
        }
      };

      utterance.onend = () => {
        (window as any).__activeAppleUtterance = null;
        if (!settled) {
          settled = true;
          resolve({ ok: true, voice: svVoice ? svVoice.name : 'System Swedish' });
        }
      };

      utterance.onerror = (e) => {
        (window as any).__activeAppleUtterance = null;
        if (!settled) {
          settled = true;
          resolve({ ok: false, error: e.error || 'SpeechSynthesis error' });
        }
      };

      window.speechSynthesis.speak(utterance);

      // Safety timeout
      setTimeout(() => {
        if (!settled) {
          settled = true;
          resolve({ ok: true, voice: svVoice ? svVoice.name : 'System Swedish' });
        }
      }, 1000);
    });
  } catch (err: any) {
    return { ok: false, error: err.message || 'Unknown error' };
  }
};

/**
 * Play via Google Cloud TTS Audio Stream (/api/tts)
 */
export const playGoogleTTSStream = (word: string): Promise<{ ok: boolean; error?: string }> => {
  return new Promise((resolve) => {
    const cleanText = (word || '').replace(/[!?"'.,:;()]/g, ' ').trim();
    if (!cleanText) return resolve({ ok: false, error: 'Empty text' });

    if (activeAudio) {
      activeAudio.pause();
      activeAudio.currentTime = 0;
    }

    const ttsUrl = `/api/tts?text=${encodeURIComponent(cleanText)}`;
    const audio = new Audio(ttsUrl);
    activeAudio = audio;

    let settled = false;
    audio.onplay = () => {
      if (!settled) {
        settled = true;
        resolve({ ok: true });
      }
    };
    audio.onerror = () => {
      if (!settled) {
        settled = true;
        resolve({ ok: false, error: 'Failed to load TTS audio stream' });
      }
    };

    audio.play().catch((e) => {
      if (!settled) {
        settled = true;
        resolve({ ok: false, error: e.message });
      }
    });
  });
};

/**
 * Play Studio R2 MP3
 */
export const playStudioR2 = (word: string): Promise<{ ok: boolean; error?: string }> => {
  return new Promise((resolve) => {
    const trimmed = (word || '').trim();
    if (!trimmed) return resolve({ ok: false, error: 'Empty word' });

    if (activeAudio) {
      activeAudio.pause();
      activeAudio.currentTime = 0;
    }

    const mp3Url = getMp3PublicUrl(`words_audio/${encodeURIComponent(trimmed)}.mp3`);
    const audio = new Audio(mp3Url);
    activeAudio = audio;

    let settled = false;
    audio.onplay = () => {
      if (!settled) {
        settled = true;
        resolve({ ok: true });
      }
    };
    audio.onerror = () => {
      if (!settled) {
        settled = true;
        resolve({ ok: false, error: '404: Studio MP3 not found in R2' });
      }
    };

    audio.play().catch((err) => {
      if (!settled) {
        settled = true;
        resolve({ ok: false, error: err.message });
      }
    });
  });
};

export const playSwedishTTS = (word: string) => {
  const engine = getPreferredTtsEngine();
  if (engine === 'google') {
    playGoogleTTSStream(word).then(res => {
      if (!res.ok) playAppleWebSpeech(word);
    });
  } else {
    // Default & 'apple': Prioritize Apple System Voice (Alva / Alva Premium)
    playAppleWebSpeech(word).then(res => {
      if (!res.ok) playGoogleTTSStream(word);
    });
  }
};

/**
 * Pre-probes whether the exact MP3 file exists in R2 in the background.
 */
export const preProbeWordAudio = (word: string) => {
  if (!word) return;
  const trimmed = word.trim();
  if (missingAudioCache.has(trimmed)) return;

  const url = getMp3PublicUrl(`words_audio/${encodeURIComponent(trimmed)}.mp3`);
  fetch(url, { method: 'HEAD' })
    .then(res => {
      if (!res.ok) {
        missingAudioCache.add(trimmed);
      }
    })
    .catch(() => {
      missingAudioCache.add(trimmed);
    });
};

/**
 * Play the exact audio for a word or phrase.
 * 1. ALWAYS tries studio MP3 from R2 first (e.g. konditional, Hör av dig snart!, slut, etc.)
 * 2. If known to have no MP3 (or on 404 error), plays TTS according to preferred engine.
 */
export const playExactWordAudio = (word: string) => {
  if (!word) return;
  const trimmed = word.trim();
  if (!trimmed) return;

  // Stop previous audio
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
  }

  // If already confirmed to lack MP3, play TTS directly
  if (missingAudioCache.has(trimmed)) {
    playSwedishTTS(word);
    return;
  }

  // Attempt studio MP3 from R2
  const mp3Url = getMp3PublicUrl(`words_audio/${encodeURIComponent(trimmed)}.mp3`);
  const audio = new Audio(mp3Url);
  activeAudio = audio;

  let hasFallenBack = false;
  const fallback = () => {
    if (hasFallenBack) return;
    hasFallenBack = true;
    missingAudioCache.add(trimmed);
    playSwedishTTS(word);
  };

  audio.onerror = () => fallback();
  audio.play().catch((err) => {
    if (err.name !== 'AbortError') {
      fallback();
    }
  });
};
