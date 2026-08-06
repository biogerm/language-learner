import whisper
import time
import os
import asyncio
import edge_tts

MODELS_DIR = "../phase4/models"
os.makedirs(MODELS_DIR, exist_ok=True)

# Test Data
LONG_SENTENCE = "Även om det regnade kraftigt hela förmiddagen, bestämde vi oss för att ta en lång promenad i skogen och plocka svamp inför kvällens middag."
WORDS = ["soffpotatis", "träna", "att", "tro", "fåtölj", "bok", "kväll", "skog", "middag", "svamp"]

TEST_SENTENCE_AUDIO = "../phase4/test_sentence.mp3"
TEST_WORDS_AUDIO = ["../phase4/test_word_{}.mp3".format(i) for i in range(len(WORDS))]

async def generate_test_audio():
    print("Generating test audio...")
    comm = edge_tts.Communicate(LONG_SENTENCE, "sv-SE-SofieNeural", rate="-20%")
    await comm.save(TEST_SENTENCE_AUDIO)
    for i, word in enumerate(WORDS):
        comm = edge_tts.Communicate(word, "sv-SE-MattiasNeural", rate="-20%")
        await comm.save(TEST_WORDS_AUDIO[i])
    print("Audio generated.")

def benchmark_model(model_name):
    print(f"\n--- Benchmarking Model: {model_name} ---")
    start_load = time.time()
    model = whisper.load_model(model_name, download_root=MODELS_DIR)
    load_time = time.time() - start_load
    print(f"[{model_name}] Loaded in {load_time:.2f}s.")
    
    # Sentence Inference
    start_sent = time.time()
    res_sent = model.transcribe(TEST_SENTENCE_AUDIO, language="sv")
    sent_time = time.time() - start_sent
    print(f"[{model_name}] Sentence time: {sent_time:.2f}s, Text: {res_sent['text'].strip()}")
    
    # Words Inference
    start_words = time.time()
    for audio in TEST_WORDS_AUDIO:
        _ = model.transcribe(audio, language="sv")
    words_time = time.time() - start_words
    print(f"[{model_name}] 10 Words time: {words_time:.2f}s")
    
    avg_word_time = words_time / len(WORDS)
    return sent_time, avg_word_time

async def main():
    if not os.path.exists(TEST_SENTENCE_AUDIO):
        await generate_test_audio()
        
    models = ["small", "medium", "large"]
    results = {}
    for m in models:
        st, wt = benchmark_model(m)
        results[m] = {"sent": st, "word": wt}
        
    print("\n--- ESTIMATED TOTAL TIME ---")
    TOTAL_SENTENCES = 1659
    TOTAL_WORDS = 3307
    
    for m in models:
        total_time = (TOTAL_SENTENCES * results[m]["sent"]) + (TOTAL_WORDS * results[m]["word"])
        total_mins = total_time / 60
        print(f"[{m}] Estimated total inference time: {total_mins:.2f} minutes")

if __name__ == "__main__":
    asyncio.run(main())
