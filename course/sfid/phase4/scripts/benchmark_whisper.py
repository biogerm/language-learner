import whisper
import time
import os
import edge_tts
import asyncio

MODELS_DIR = "../phase4/models"
os.makedirs(MODELS_DIR, exist_ok=True)

# A sample Swedish sentence from our corpus
TEST_SENTENCE = "Jag brukar sitta i en fåtölj och läsa böcker på kvällarna."
TEST_AUDIO = "../phase4/test_benchmark.mp3"

async def generate_test_audio():
    print(f"Generating test audio for: {TEST_SENTENCE}")
    communicate = edge_tts.Communicate(TEST_SENTENCE, "sv-SE-SofieNeural", rate="-20%")
    await communicate.save(TEST_AUDIO)
    print("Test audio generated.")

def benchmark_model(model_name):
    print(f"\n--- Benchmarking Model: {model_name} ---")
    print(f"Downloading/Loading {model_name} into {MODELS_DIR} (This may take a while for large)...")
    
    start_load = time.time()
    model = whisper.load_model(model_name, download_root=MODELS_DIR)
    load_time = time.time() - start_load
    print(f"[{model_name}] Model loaded in {load_time:.2f} seconds.")
    
    print(f"[{model_name}] Running inference on test audio...")
    start_infer = time.time()
    result = model.transcribe(TEST_AUDIO, language="sv")
    infer_time = time.time() - start_infer
    
    text = result["text"].strip()
    print(f"[{model_name}] Inference time: {infer_time:.2f} seconds")
    print(f"[{model_name}] Recognized text: '{text}'")
    return infer_time, text

async def main():
    if not os.path.exists(TEST_AUDIO):
        await generate_test_audio()
        
    benchmark_model("small")
    benchmark_model("large")
    
    print("\n--- Benchmark Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
