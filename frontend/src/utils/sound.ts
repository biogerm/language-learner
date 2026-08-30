import { getMp3PublicUrl } from '../services/r2';

// Cache of words confirmed to have NO studio MP3 on R2
const missingAudioCache = new Set<string>();
let activeAudio: HTMLAudioElement | null = null;

export const playSwedishTTS = (word: string) => {
  const cleanText = (word || '').replace(/[!?"'.,:;()]/g, ' ').trim();
  if (!cleanText) return;

  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
  }

  // 1. Primary: Real Swedish Audio Stream via HTML5 Audio
  const ttsUrl = `/api/tts?text=${encodeURIComponent(cleanText)}`;
  const audio = new Audio(ttsUrl);
  activeAudio = audio;
  
  audio.play().catch(() => {
    // 2. Secondary fallback: Web Speech API
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
        }
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'sv-SE';
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
      } catch (e) {
        console.warn('SpeechSynthesis fallback failed:', e);
      }
    }
  });
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
 * 2. If known to have no MP3 (or on 404 error), plays clear Swedish TTS audio stream.
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
