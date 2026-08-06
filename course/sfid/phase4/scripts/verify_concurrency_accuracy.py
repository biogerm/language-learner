import whisper
import concurrent.futures
import warnings

warnings.filterwarnings("ignore")

MODELS_DIR = "../phase4/models"
TEST_SENTENCE_AUDIO = "../phase4/test_sentence.mp3"

model = whisper.load_model("large", download_root=MODELS_DIR)

def transcribe(i):
    res = model.transcribe(TEST_SENTENCE_AUDIO, language="sv")
    return res["text"].strip()

print("Verifying accuracy of 10 concurrent threads on large model...")
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(transcribe, i) for i in range(10)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

for idx, text in enumerate(results):
    print(f"Thread {idx+1}: {text}")

