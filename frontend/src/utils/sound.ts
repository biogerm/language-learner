import { getMp3PublicUrl } from '../services/r2';

const missingAudioCache = new Set<string>();
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

    setTimeout(() => {
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = 'sv-SE';
      utterance.rate = 0.9;
      utterance.pitch = 1.0;

      const svVoice = getSwedishVoice();
      if (svVoice) {
        utterance.voice = svVoice;
      }

      (window as any)._activeTTS = utterance;
      utterance.onend = () => { (window as any)._activeTTS = null; };
      utterance.onerror = (e) => {
        console.warn('Swedish TTS error:', e);
        (window as any)._activeTTS = null;
      };

      window.speechSynthesis.speak(utterance);
    }, 25);
  } catch (err) {
    console.warn('Failed to speak Swedish TTS:', err);
  }
};

/**
 * Play the exact audio for a word or phrase.
 * Probes exact raw filename (preserving case/punctuation like "Hör av dig snart!.mp3"),
 * lowercase, clean, and snake_case candidates before falling back to Swedish TTS.
 */
export const playExactWordAudio = (word: string) => {
  if (!word) return;
  const rawTrimmed = word.trim();
  const cleanWord = rawTrimmed.replace(/[.,!?"':;()]/g, '').trim().toLowerCase();
  if (!rawTrimmed) return;

  // Stop previous audio
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
  }

  // If already known to lack MP3, trigger TTS synchronously during user gesture
  if (missingAudioCache.has(rawTrimmed) && missingAudioCache.has(cleanWord)) {
    playSwedishTTS(word);
    return;
  }

  const rawKey = encodeURIComponent(rawTrimmed);
  const rawLowerKey = encodeURIComponent(rawTrimmed.toLowerCase());
  const cleanKey = encodeURIComponent(cleanWord);
  const snakeKey = encodeURIComponent(rawTrimmed.toLowerCase().replace(/\s+/g, '_'));
  const cleanSnakeKey = encodeURIComponent(cleanWord.replace(/\s+/g, '_'));

  const candidateUrls = Array.from(new Set([
    getMp3PublicUrl(`words_audio/${rawKey}.mp3`),
    getMp3PublicUrl(`words_audio/${rawLowerKey}.mp3`),
    getMp3PublicUrl(`words_audio/${cleanKey}.mp3`),
    getMp3PublicUrl(`words_audio/${snakeKey}.mp3`),
    getMp3PublicUrl(`words_audio/${cleanSnakeKey}.mp3`)
  ]));

  let currentIndex = 0;

  const tryNext = () => {
    if (currentIndex >= candidateUrls.length) {
      missingAudioCache.add(rawTrimmed);
      missingAudioCache.add(cleanWord);
      playSwedishTTS(word);
      return;
    }

    const url = candidateUrls[currentIndex++];
    const audio = new Audio(url);
    activeAudio = audio;
    let settled = false;

    const onFail = () => {
      if (settled) return;
      settled = true;
      tryNext();
    };

    audio.onerror = () => onFail();
    audio.play().catch((err) => {
      if (err.name !== 'AbortError') {
        onFail();
      }
    });
  };

  tryNext();
};
