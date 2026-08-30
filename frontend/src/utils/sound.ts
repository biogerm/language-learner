import { getMp3PublicUrl } from '../services/r2';

// In-memory cache: word -> verified MP3 URL string or false (TTS only)
const audioProbeCache = new Map<string, string | false>();
let activeAudio: HTMLAudioElement | null = null;
let cachedVoices: SpeechSynthesisVoice[] = [];

// Pre-load voices on module import
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  const loadVoices = () => {
    try {
      const v = window.speechSynthesis.getVoices();
      if (v && v.length > 0) {
        cachedVoices = v;
      }
    } catch {}
  };
  loadVoices();
  window.speechSynthesis.onvoiceschanged = loadVoices;
}

export const getSwedishVoice = (): SpeechSynthesisVoice | undefined => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return undefined;
  const voices = cachedVoices.length ? cachedVoices : window.speechSynthesis.getVoices();
  return (
    voices.find(v => v.lang && (v.lang.toLowerCase().startsWith('sv') || v.lang.toLowerCase().includes('se'))) ||
    voices.find(v => v.name && v.name.toLowerCase().includes('swedish'))
  );
};

export const playSwedishTTS = (word: string) => {
  const cleanText = (word || '').replace(/[!?"'.,:;()]/g, ' ').trim();
  if (!cleanText) return;

  // Stop previous audio
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
  }

  // 1. Primary: Real Swedish Audio Stream via HTML5 Audio
  // 100% audible on all Mac speakers, independent of local macOS voice downloads!
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
 * Call this when a new word card loads or enters the queue.
 */
export const preProbeWordAudio = (word: string) => {
  if (!word) return;
  const trimmed = word.trim();
  if (audioProbeCache.has(trimmed)) return;

  const url = getMp3PublicUrl(`words_audio/${encodeURIComponent(trimmed)}.mp3`);
  fetch(url, { method: 'HEAD' })
    .then(res => {
      audioProbeCache.set(trimmed, res.ok ? url : false);
    })
    .catch(() => {
      audioProbeCache.set(trimmed, false);
    });
};

/**
 * Play the exact audio for a word or phrase.
 * If exact MP3 exists on R2, plays the studio MP3.
 * If not, immediately speaks Swedish TTS synchronously within the user gesture.
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

  const cached = audioProbeCache.get(trimmed);
  if (cached === false) {
    playSwedishTTS(word);
    return;
  }
  if (typeof cached === 'string') {
    const audio = new Audio(cached);
    activeAudio = audio;
    audio.play().catch(() => playSwedishTTS(word));
    return;
  }

  // If probe is still in-flight or not cached yet, play Swedish TTS synchronously
  // to ensure browser User Activation is NEVER lost!
  playSwedishTTS(word);
  preProbeWordAudio(word);
};
