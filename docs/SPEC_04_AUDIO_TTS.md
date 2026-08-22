# Phase 4: Audio TTS Generation & Verification

## 1. Overview
The core objective of Phase 4 is to generate MP3 pronunciation audio for all generated sentences and individual words, and to rigorously verify their quality.

To meet the needs of SFI learners, the audio is generated using the Microsoft Edge TTS API, with the speech rate reduced by 20% to accommodate a learning pace. 
Furthermore, this phase incorporates an Automatic Speech Recognition (ASR) loopback verification using OpenAI Whisper. This ensures pronunciation accuracy and prevents the pipeline from outputting corrupted files caused by network timeouts or silent generation bugs.

## 2. Input Specification

- **Input from Phase 2**: The article JSON files containing all sentences. Each sentence must have an `id` and an `sv` (Swedish text) field.
- **Input from Phase 1**: The `master_dict.json` containing all individual words (using the `base_form` key).
- **Parameters**:
  - `voices`: TTS voice pool (Default: `["sv-SE-SofieNeural", "sv-SE-MattiasNeural"]`, alternating male/female)
  - `rate`: Speech rate adjustment (Default: `-20%`)
  - `output_format`: Audio format (Default: `mp3`)
  - `max_concurrent`: Maximum concurrent requests (Default: 10)
  - `retry_count`: Retries for failed requests (Default: 5)
  - `min_file_size_bytes`: Minimum valid MP3 file size (Default: 1024 bytes)
  - `whisper_model`: Whisper model for verification (Default: `base`)
  - `verification_threshold`: Minimum similarity score for TTS verification (Default: 0.85)

## 3. TTS Generation Pipeline

### 3.1 Task Splitting
- **Sentence Audio Task**: Extract all unique sentences from the Phase 2 JSON files.
- **Word Audio Task**: Extract all unique `base_form` entries from the Phase 1 dictionary.
- **Deduplicate**: Words and sentences appearing multiple times across chapters are generated only once and shared.
- **Voice Alternation (Male/Female)**: When generating sentence or word audio, the script MUST alternate between the voices in the voice pool (e.g., Sentence 1 uses Female, Sentence 2 uses Male, Sentence 3 uses Female; same for Words). This is crucial to prevent auditory fatigue and help learners adapt to different accents and genders.

### 3.2 Concurrency & Rate Limit Evasion
To achieve high-concurrency generation while avoiding Edge TTS API rate limits, implement the following robust generation loop. The script MUST use a strategy combining ThreadPools, explicit file size checks, and cooldown sleeps:

1. **Thread Pool**: Use Python's `concurrent.futures.ThreadPoolExecutor` with `max_workers=10`. This strikes the exact balance between speed and single-IP rate limits.
2. **Robust Retry Loop**: Wrap each TTS API subprocess call in a `for attempt in range(10):` loop.
3. **Double Quality Validation**: Edge TTS may silently fail and generate empty 0KB files upon hitting a rate limit. Always verify that the output MP3 file exists AND its size is strictly `> 1024 bytes`.
4. **Cooldown Sleep**: If an exception is caught or the file size validation fails, execute `time.sleep(1)` before the next loop iteration. This creates a natural "traffic desynchronization", allowing the rate limit to cool down.

**Implementation Reference**:
```python
def generate_tts(text, mp3_path, voice):
    cmd = f'edge-tts --voice {voice} --rate=-20% --text "{text}" --write-media {mp3_path}'
    max_retries = 10
    for attempt in range(max_retries):
        try:
            # Execute command silently
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Crucial: Check if file actually exists AND is larger than 1KB (not empty/corrupted)
            if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1024:
                return True
        except Exception:
            pass
        # Natural traffic desynchronization cooldown on failure
        time.sleep(1)
    return False
```

### 3.3 File Naming Conventions
- Sentence Audio: `sentences_audio/{sentence_id}.mp3` (e.g., `sentences_audio/art01_s001.mp3`)
- Word Audio: `words_audio/{base_form}.mp3` (e.g., `words_audio/soffpotatis.mp3`)
- All filenames must be **lowercase**, with spaces replaced by underscores `_`.
- Special Swedish characters (å, ä, ö) should be retained in the filename; do not downgrade to ASCII.

### 3.4 Quality Checks
Perform basic checks after every generation:
1. **File Existence**: Confirm the file is saved to the correct path.
2. **File Size**: Check if the file size is `>= min_file_size_bytes` (1KB) to prevent empty or corrupted files.
3. **Audio Duration (Optional)**: Reject audio files shorter than 0.3 seconds.
- Files failing these checks automatically trigger a retry (up to `retry_count`).
- If retries are exhausted, log the error and skip to the next task.

## 4. Speech Recognition (ASR) Verification
Introduce an ASR mechanism to perform closed-loop validation on the generated audio, ensuring the TTS engine actually pronounced the intended text.

### 4.1 Verification Flow
1. Load the generated MP3 file.
2. Feed it into Whisper (or Azure Speech-to-Text) to extract the transcript.
3. **Normalize**: Convert both the original text and the generated transcript to lowercase, and strip all punctuation and extra whitespace.
4. Calculate **Levenshtein distance (Character-level)** or **Word Error Rate (WER)**.
5. Calculate the similarity score: `similarity score = 1 - (edit_distance / max_length)`.

### 4.2 Decision Rules
- **PASS**: If `similarity >= verification_threshold` (default 0.85).
- **FAIL**: If `similarity < verification_threshold`, mark as failed and trigger a regeneration retry.
- **FLAG**: If the similarity remains below the threshold after 3 regeneration cycles, flag the audio for manual review.

### 4.3 Special Handling
- **Single Word Audio**: For standalone words, enforce an **Exact Match** after normalization instead of using edit distance.
- **Numbers**: If a sentence contains numbers, normalize the numbers to their spelled-out text equivalents before comparing.
- **Proper Nouns**: Exclude proper nouns from the comparison text if they are known to be consistently misrecognized by Whisper.

## 5. Output Specification

### 5.1 Audio Files
- **Directories**: `audio/{course_id}/sentences/` and `audio/{course_id}/words/`.
- **Format**: MP3, Mono, 24kHz Sample Rate.

### 5.2 Audio Manifest JSON
At the end of the run, an `audio_manifest.json` must be generated for frontend and backend state tracking.
```json
{
  "metadata": {
    "course_id": "sfid",
    "total_sentences": 1750,
    "total_words": 3433,
    "generated_at": "2025-01-01T00:00:00Z",
    "voices": ["sv-SE-SofieNeural", "sv-SE-MattiasNeural"],
    "rate": "-20%"
  },
  "sentences": {
    "art01_s001": {
      "file": "sentences_audio/art01_s001.mp3",
      "duration_ms": 3200,
      "verification_score": 0.95,
      "status": "verified"
    }
  },
  "words": {
    "soffpotatis": {
      "file": "words_audio/soffpotatis.mp3",
      "duration_ms": 1100,
      "verification_score": 1.0,
      "status": "verified"
    }
  }
}
```

## 6. Validation Rules
1. Every `sentence` referenced in the Phase 2 JSONs must have a corresponding MP3 in `sentences_audio/`.
2. Every `base_form` referenced in the Master Dictionary must have a corresponding MP3 in `words_audio/`.
3. All audio files must pass the `min_file_size_bytes` check.
4. At least **95%** of the audio files must pass the ASR verification.
5. The remaining <= 5% of unverified files must be explicitly recorded with a "flagged" status in the manifest for manual inspection.

## 7. Scripts & Snippets

> [!NOTE]
> This phase is entirely API/Script driven. No LLM reasoning prompts are required.

**Edge TTS CLI Reference:**
```bash
# Word Audio
edge-tts --text "soffpotatis" --voice "sv-SE-MattiasNeural" --rate="-20%" --write-media "words_audio/soffpotatis.mp3"

# Sentence Audio
edge-tts --text "Det är en fin dag idag." --voice "sv-SE-SofieNeural" --rate="-20%" --write-media "sentences_audio/art01_s001.mp3"
```

**Whisper Verification Snippet (Python):**
```python
import whisper
import Levenshtein

def verify_audio(file_path, original_text, threshold=0.85):
    model = whisper.load_model("base")
    # Force Swedish language
    result = model.transcribe(file_path, language="sv")
    
    transcript = result["text"].lower().strip()
    target_text = original_text.lower().strip()
    
    # Simple cleanup
    transcript = "".join([c for c in transcript if c.isalnum() or c.isspace()])
    target_text = "".join([c for c in target_text if c.isalnum() or c.isspace()])
    
    distance = Levenshtein.distance(target_text, transcript)
    max_len = max(len(target_text), len(transcript))
    
    if max_len == 0:
        return 0.0
        
    similarity = 1 - (distance / max_len)
    return similarity
```

## 8. Error Handling

- **Network timeout**: The Edge TTS API may stop responding. Use an exponential backoff strategy for retries.
- **Rate limiting**: If a 429 error occurs, suspend execution (cooldown) for a few seconds and reduce the concurrency pool before resuming.
- **Corrupted audio**: If the file size is too small or cannot be read by an audio library, delete it immediately and retry generation.
- **Whisper unavailable**: If the local Whisper model fails to load or runs out of memory (OOM), log a Warning, skip the ASR verification phase, but continue saving the generated MP3s to ensure the pipeline doesn't crash completely.
