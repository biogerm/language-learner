import whisper
import time
import os
import concurrent.futures
import warnings

warnings.filterwarnings("ignore")

MODELS_DIR = "../phase4/models"
TEST_SENTENCE_AUDIO = "../phase4/test_sentence.mp3"
TEST_WORDS_AUDIO = ["../phase4/test_word_{}.mp3".format(i) for i in range(10)]

SENTENCES = [TEST_SENTENCE_AUDIO] * 10
WORDS = TEST_WORDS_AUDIO

global_model = None

def init_worker(model_name):
    global global_model
    import warnings
    warnings.filterwarnings("ignore")
    global_model = whisper.load_model(model_name, download_root=MODELS_DIR)

def process_audio(audio_path):
    global_model.transcribe(audio_path, language="sv")
    return True

def run_benchmark(model_name):
    print(f"\n======================================")
    print(f"Multiprocessing Benchmark: {model_name} (2 Processes)")
    print(f"======================================")
    
    # Initialize the ProcessPool. Max workers is 2.
    with concurrent.futures.ProcessPoolExecutor(max_workers=2, initializer=init_worker, initargs=(model_name,)) as executor:
        print(f"[{model_name}] Spawning 2 processes and loading 2 model copies into RAM (please wait)...")
        
        # Warmup and force initialization across all 2 workers
        list(executor.map(process_audio, [TEST_SENTENCE_AUDIO]*2))
        print(f"[{model_name}] Initialization complete! Starting real benchmark.")
        
        # 10 Sentences benchmark
        start_sent = time.time()
        list(executor.map(process_audio, SENTENCES))
        t_sent = time.time() - start_sent
        print(f"[{model_name}] 10 Sentences processed in: {t_sent:.2f}s")
        
        # 10 Words benchmark
        start_words = time.time()
        list(executor.map(process_audio, WORDS))
        t_words = time.time() - start_words
        print(f"[{model_name}] 10 Words processed in: {t_words:.2f}s")

    return t_sent, t_words

if __name__ == '__main__':
    ms, mw = run_benchmark("medium")
    ls, lw = run_benchmark("large")
    
    print("\n--- ESTIMATED TOTAL TIME FOR ENTIRE CORPUS (1659 Sentences + 3307 Words) ---")
    medium_total_mins = ((1659 / 10 * ms) + (3307 / 10 * mw)) / 60
    large_total_mins = ((1659 / 10 * ls) + (3307 / 10 * lw)) / 60
    
    print(f"[medium] Estimated total time (2 processes): {medium_total_mins:.2f} minutes")
    print(f"[large] Estimated total time (2 processes): {large_total_mins:.2f} minutes")
