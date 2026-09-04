import { getMp3PublicUrl } from '../services/r2';

// Cache of words confirmed to have NO studio MP3 on R2
const missingAudioCache = new Set<string>();
// Cache of URLs already preloaded via fetch into browser HTTP cache
const preloadedUrls = new Set<string>();

// Global singleton audio instance — avoids exhausting iOS/WebKit CoreAudio hardware channels
let sharedAudio: HTMLAudioElement | null = null;

const getSharedAudio = (): HTMLAudioElement => {
  if (!sharedAudio && typeof window !== 'undefined') {
    sharedAudio = new Audio();
  }
  return sharedAudio!;
};

/**
 * Safely stops active audio and completely releases the underlying WebKit AVPlayer/CoreAudio pipeline.
 */
export const stopAudio = () => {
  if (sharedAudio) {
    sharedAudio.onerror = null;
    sharedAudio.onplay = null;
    sharedAudio.pause();
    sharedAudio.removeAttribute('src');
    sharedAudio.load(); // Forces WebKit to tear down the AVPlayer hardware decoder
  }
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel(); // Clears any stuck utterance queue on iOS
    } catch {}
  }
};

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
    // Cancel any stuck utterances in iOS WebKit speech queue before speaking
    window.speechSynthesis.cancel();
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

    stopAudio();

    const safeVoice = voice.includes('Standard') || voice === 'Alva' ? 'Alva' : 'Alva (Premium)';
    const ttsUrl = `/api/apple-tts?text=${encodeURIComponent(cleanText)}&voice=${encodeURIComponent(safeVoice)}`;
    const audio = getSharedAudio();

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

    audio.src = ttsUrl;
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

    stopAudio();

    const ttsUrl = `/api/tts?text=${encodeURIComponent(cleanText)}`;
    const audio = getSharedAudio();

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

    audio.src = ttsUrl;
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

    stopAudio();

    const mp3Url = getMp3PublicUrl(`words_audio/${encodeURIComponent(trimmed)}.mp3`);
    const audio = getSharedAudio();

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

    audio.src = mp3Url;
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
 * Pre-probes / preloads word audio into browser HTTP cache without allocating
 * any underlying WebKit CoreAudio hardware channels or leaking Audio elements.
 */
export const preProbeWordAudio = async (word: string) => {
  if (!word) return;
  const trimmed = word.trim();
  if (!trimmed || missingAudioCache.has(trimmed)) return;

  const primaryUrl = getMp3PublicUrl(`words_audio/${encodeURIComponent(trimmed)}.mp3`);
  if (preloadedUrls.has(primaryUrl)) return;
  preloadedUrls.add(primaryUrl);

  try {
    // Warm the browser's HTTP disk/memory cache cleanly
    const res = await fetch(primaryUrl, { method: 'GET' });
    if (res.ok) {
      return;
    }
    if (res.status === 404) {
      // Also probe capitalized variant
      const capitalized = trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
      if (capitalized !== trimmed) {
        const fallbackUrl = getMp3PublicUrl(`words_audio/${encodeURIComponent(capitalized)}.mp3`);
        if (!preloadedUrls.has(fallbackUrl)) {
          preloadedUrls.add(fallbackUrl);
          const fbRes = await fetch(fallbackUrl, { method: 'GET' });
          if (fbRes.ok) return;
        }
      }
      missingAudioCache.add(trimmed);
    }
  } catch {}
};

/**
 * Play the exact audio for a word or phrase using the shared singleton audio player.
 * 1. ALWAYS tries studio MP3 from R2 first.
 * 2. If that 404s, tries the capitalized variant (e.g. "jag…" -> "Jag…") in case
 *    the R2 file uses a capital first letter.
 * 3. Only falls back to TTS if both attempts fail.
 */
export const playExactWordAudio = (word: string) => {
  if (!word) return;
  const trimmed = word.trim();
  if (!trimmed) return;

  stopAudio();

  // If already confirmed to lack MP3, play TTS directly
  if (missingAudioCache.has(trimmed)) {
    playSwedishTTS(word);
    return;
  }

  const audio = getSharedAudio();
  const primaryUrl = getMp3PublicUrl(`words_audio/${encodeURIComponent(trimmed)}.mp3`);
  const capitalized = trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
  const hasCaseVariant = capitalized !== trimmed;
  const fallbackUrl = hasCaseVariant
    ? getMp3PublicUrl(`words_audio/${encodeURIComponent(capitalized)}.mp3`)
    : null;

  let currentAttempt: 'primary' | 'fallback' | 'done' = 'primary';

  const onError = () => {
    if (currentAttempt === 'primary') {
      if (fallbackUrl) {
        currentAttempt = 'fallback';
        audio.pause();
        audio.removeAttribute('src');
        audio.load();
        audio.src = fallbackUrl;
        const p = audio.play();
        if (p !== undefined) {
          p.catch((err) => {
            if (err.name === 'AbortError') return;
            if (err.name !== 'NotAllowedError') {
              currentAttempt = 'done';
              missingAudioCache.add(trimmed);
              playSwedishTTS(word);
            }
          });
        }
      } else {
        currentAttempt = 'done';
        missingAudioCache.add(trimmed);
        playSwedishTTS(word);
      }
    } else if (currentAttempt === 'fallback') {
      currentAttempt = 'done';
      missingAudioCache.add(trimmed);
      playSwedishTTS(word);
    }
  };

  audio.onplay = () => {
    audio.onerror = null;
  };
  audio.onerror = onError;
  audio.src = primaryUrl;

  const p = audio.play();
  if (p !== undefined) {
    p.catch((err) => {
      if (err.name === 'AbortError') return;
      if (err.name !== 'NotAllowedError') {
        onError();
      }
    });
  }
};

