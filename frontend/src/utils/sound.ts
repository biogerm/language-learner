import { getMp3PublicUrl } from '../services/r2';
import r2AudioList from '../data/r2_audio_index.json';

const availableAudioSet = new Set<string>(r2AudioList);
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
  } catch (err) {
    console.warn('Failed to speak Swedish TTS:', err);
  }
};

/**
 * Play the exact audio for a word or phrase.
 * If known to exist in R2 audio repository, plays the studio MP3 recording.
 * If not in R2 repository, immediately and synchronously plays Swedish TTS within the user gesture!
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

  // Find matching audio filename in availableAudioSet:
  // 1. Raw exact (e.g. "Hör av dig snart!")
  // 2. Raw lowercase (e.g. "hör av dig snart!")
  // 3. Clean word (e.g. "hör av dig snart" / "trotta")
  // 4. Snake_case (e.g. "hör_av_dig_snart!" / "hör_av_dig_snart")
  const candidates = [
    rawTrimmed,
    rawTrimmed.toLowerCase(),
    cleanWord,
    rawTrimmed.toLowerCase().replace(/\s+/g, '_'),
    cleanWord.replace(/\s+/g, '_')
  ];

  let matchedFilename: string | null = null;
  for (const c of candidates) {
    if (availableAudioSet.has(c)) {
      matchedFilename = c;
      break;
    }
  }

  if (matchedFilename) {
    const encoded = encodeURIComponent(matchedFilename);
    const url = getMp3PublicUrl(`words_audio/${encoded}.mp3`);
    const audio = new Audio(url);
    activeAudio = audio;
    audio.play().catch((err) => {
      if (err.name !== 'AbortError') {
        playSwedishTTS(word);
      }
    });
  } else {
    // Synchronously trigger Swedish TTS within user gesture (100% reliable)
    playSwedishTTS(word);
  }
};
