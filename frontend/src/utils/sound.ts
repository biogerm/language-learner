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
 * If the exact MP3 does not exist (404), directly speak the exact word via Swedish TTS.
 * Never play a different base word in Dictation / Flashcard!
 */
export const playExactWordAudio = (word: string) => {
  if (!word) return;
  const cleanWord = word.replace(/[.,!?"':;()]/g, '').trim().toLowerCase();
  if (!cleanWord) return;

  // Stop previous audio
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
  }

  // If already known to lack MP3, trigger TTS synchronously during user gesture
  if (missingAudioCache.has(cleanWord)) {
    playSwedishTTS(word);
    return;
  }

  const encodedFilename = encodeURIComponent(cleanWord);
  const url = getMp3PublicUrl(`words_audio/${encodedFilename}.mp3`);
  const audio = new Audio(url);
  activeAudio = audio;
  let hasFallenBack = false;

  const fallbackToTTS = () => {
    if (hasFallenBack) return;
    hasFallenBack = true;
    missingAudioCache.add(cleanWord);
    playSwedishTTS(word);
  };

  audio.onerror = () => {
    fallbackToTTS();
  };

  audio.play().catch((err) => {
    if (err.name !== 'AbortError') {
      fallbackToTTS();
    }
  });
};
