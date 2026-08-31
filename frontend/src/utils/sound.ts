import { getMp3PublicUrl } from '../services/r2';

// Cache of words confirmed to have NO studio MP3 on R2
const missingAudioCache = new Set<string>();
let activeAudio: HTMLAudioElement | null = null;

const isApplePlatform = typeof navigator !== 'undefined' && (
  /iPhone|iPad|iPod/i.test(navigator.userAgent) ||
  (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1) ||
  /^((?!chrome|android).)*safari/i.test(navigator.userAgent)
);

/**
 * Play via Apple Web Speech API (Native WebKit in iOS / Safari)
 */
export const playAppleNativeWebSpeech = (word: string): boolean => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return false;
  const cleanText = (word || '').replace(/[!?"'.,:;()]/g, ' ').trim();
  if (!cleanText) return false;

  try {
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'sv-SE';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    (window as any).__activeSpeechUtterance = utterance;
    window.speechSynthesis.speak(utterance);
    return true;
  } catch {
    return false;
  }
};

/**
 * Play via Apple Native macOS Voice (Alva / Alva Premium).
 * Uses high-fidelity native audio stream directly from macOS system speech engine,
 * or direct WebKit synthesis on iOS / Safari.
 */
export const playAppleWebSpeech = (word: string, voice = 'Alva (Premium)'): Promise<{ ok: boolean; voice?: string; error?: string }> => {
  return new Promise((resolve) => {
    const cleanText = (word || '').replace(/[!?"'.,:;()]/g, ' ').trim();
    if (!cleanText) return resolve({ ok: false, error: 'Empty text' });

    // On iOS (iPhone/iPad) or native Safari, use direct WebKit speech synthesis for 0ms latency & 100% native Apple audio
    if (isApplePlatform && typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const ok = playAppleNativeWebSpeech(cleanText);
      if (ok) {
        return resolve({ ok: true, voice: 'Apple iOS / Safari Swedish' });
      }
    }

    if (activeAudio) {
      activeAudio.pause();
      activeAudio.currentTime = 0;
    }

    const safeVoice = voice.includes('Standard') || voice === 'Alva' ? 'Alva' : 'Alva (Premium)';
    const ttsUrl = `/api/apple-tts?text=${encodeURIComponent(cleanText)}&voice=${encodeURIComponent(safeVoice)}`;
    const audio = new Audio(ttsUrl);
    activeAudio = audio;

    let settled = false;
    audio.onplay = () => {
      if (!settled) {
        settled = true;
        resolve({ ok: true, voice: safeVoice });
      }
    };
    audio.onerror = () => {
      // If /api/apple-tts fails (e.g. deployed on cloud Linux), fallback to Google stream
      if (!settled) {
        settled = true;
        playGoogleTTSStream(cleanText).then(resolve);
      }
    };

    audio.play().catch(() => {
      if (!settled) {
        settled = true;
        playGoogleTTSStream(cleanText).then(resolve);
      }
    });
  });
};

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
        const spoken = playAppleNativeWebSpeech(cleanText);
        resolve({ ok: spoken, error: spoken ? undefined : 'Failed to load TTS' });
      }
    };

    audio.play().catch(() => {
      if (!settled) {
        settled = true;
        const spoken = playAppleNativeWebSpeech(cleanText);
        resolve({ ok: spoken });
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
  // Try Google TTS stream first, then fallback to Web Speech API
  playGoogleTTSStream(word).then((res) => {
    if (!res.ok) {
      playAppleNativeWebSpeech(word);
    }
  });
};

/**
 * Pre-probes / preloads word audio.
 * Note: Never use fetch(HEAD) to cross-origin CDN without CORS headers,
 * as it caused false-positive errors marking all words as missing audio.
 */
export const preProbeWordAudio = (word: string) => {
  if (!word) return;
  const trimmed = word.trim();
  if (missingAudioCache.has(trimmed)) return;

  try {
    const url = getMp3PublicUrl(`words_audio/${encodeURIComponent(trimmed)}.mp3`);
    const preloadAudio = new Audio();
    preloadAudio.preload = 'auto';
    preloadAudio.src = url;
  } catch {}
};

/**
 * Play the exact audio for a word or phrase.
 * 1. ALWAYS tries studio MP3 from R2 first (e.g. konditional, Hör av dig snart!, slut, etc.)
 * 2. If known to have no MP3 (via audio.onerror), falls back to native Apple / cloud TTS.
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

  // Attempt studio MP3 from R2 via HTML5 Audio element
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

  audio.onerror = () => {
    fallback();
  };

  const playPromise = audio.play();
  if (playPromise !== undefined) {
    playPromise.catch((err) => {
      if (err.name === 'AbortError') return;
      if (err.name !== 'NotAllowedError') {
        fallback();
      }
    });
  }
};
