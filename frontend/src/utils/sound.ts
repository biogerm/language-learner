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
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
  const cleanText = (word || '').replace(/[!?"'.,:;()]/g, ' ').trim();
  if (!cleanText) return;

  try {
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }
    if (window.speechSynthesis.speaking || window.speechSynthesis.pending) {
      window.speechSynthesis.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'sv-SE';
    utterance.rate = 0.9;
    utterance.pitch = 1.0;

    (window as any)._activeTTS = utterance;
    utterance.onend = () => { (window as any)._activeTTS = null; };
    utterance.onerror = (e) => {
      console.warn('Swedish TTS error:', e);
      (window as any)._activeTTS = null;
    };

    window.speechSynthesis.speak(utterance);
  } catch (err) {
    console.warn('Failed to speak Swedish TTS:', err);
  }
};

/**
 * Pre-probes whether a word has a valid MP3 file in R2 in the background.
 * Call this when a new word card loads or enters the queue.
 */
export const preProbeWordAudio = (word: string) => {
  if (!word) return;
  const trimmed = word.trim();
  if (audioProbeCache.has(trimmed)) return;

  const rawKey = encodeURIComponent(trimmed);
  const rawLowerKey = encodeURIComponent(trimmed.toLowerCase());
  const cleanWord = trimmed.replace(/[.,!?"':;()]/g, '').trim().toLowerCase();
  const cleanKey = encodeURIComponent(cleanWord);
  const snakeKey = encodeURIComponent(trimmed.toLowerCase().replace(/\s+/g, '_'));
  const cleanSnakeKey = encodeURIComponent(cleanWord.replace(/\s+/g, '_'));

  const candidateUrls = Array.from(new Set([
    getMp3PublicUrl(`words_audio/${rawKey}.mp3`),
    getMp3PublicUrl(`words_audio/${rawLowerKey}.mp3`),
    getMp3PublicUrl(`words_audio/${cleanKey}.mp3`),
    getMp3PublicUrl(`words_audio/${snakeKey}.mp3`),
    getMp3PublicUrl(`words_audio/${cleanSnakeKey}.mp3`)
  ]));

  // Probe all candidates concurrently in parallel
  Promise.all(candidateUrls.map(url =>
    fetch(url, { method: 'HEAD' })
      .then(res => res.ok ? url : null)
      .catch(() => null)
  )).then(results => {
    const matched = results.find((r): r is string => !!r);
    audioProbeCache.set(trimmed, matched || false);
  });
};

/**
 * Play the exact audio for a word or phrase.
 * If pre-probed as available, plays the verified studio MP3.
 * If pre-probed as missing or in-flight, immediately speaks Swedish TTS synchronously within user gesture.
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
