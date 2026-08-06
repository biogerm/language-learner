import whisper
import time
import os
import concurrent.futures
import warnings

warnings.filterwarnings("ignore")

MODELS_DIR = "../phase4/models"
MODEL_NAME = "large"

TEST_SENTENCE_AUDIO = "../phase4/test_sentence.mp3"
TEST_WORDS_AUDIO = ["../phase4/test_word_{}.mp3".format(i) for i in range(10)]

print(f"\n======================================")
print(f"Starting Concurrency Benchmark: {MODEL_NAME}")
print(f"======================================")

start_load = time.time()
model = whisper.load_model(MODEL_NAME, download_root=MODELS_DIR)
print(f"Model loaded in {time.time() - start_load:.2f}s.")

def transcribe_sentence(i):
    model.transcribe(TEST_SENTENCE_AUDIO, language="sv")

def transcribe_words(i):
    for audio in TEST_WORDS_AUDIO:
        model.transcribe(audio, language="sv")

print(f"-> 10 threads simultaneously transcribing 1 long sentence...")
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(transcribe_sentence, i) for i in range(10)]
    concurrent.futures.wait(futures)
t_sent = time.time() - start_time
print(f"[Result] 10 threads (sentence) finished in: {t_sent:.2f}s")
print(f"         Average time per sentence across all threads: {t_sent/10:.2f}s")

print(f"-> 10 threads simultaneously transcribing 10 words...")
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(transcribe_words, i) for i in range(10)]
    concurrent.futures.wait(futures)
t_words = time.time() - start_time
print(f"[Result] 10 threads (10 words) finished in: {t_words:.2f}s")
print(f"         Average time per 10 words across all threads: {t_words/10:.2f}s")

