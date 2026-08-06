import os
import json
import glob
import subprocess
import time
import argparse
import concurrent.futures
from pathlib import Path
import shlex
import warnings
import Levenshtein

# Suppress warnings from PyTorch/Whisper
warnings.filterwarnings("ignore")

# Configuration
PHASE2_DIR = "../phase2/articles"
MASTER_DICT = "../phase1/master_dictionary.json"
OUTPUT_DIR = "../output"
SENTENCES_DIR = os.path.join(OUTPUT_DIR, "sentences_audio")
WORDS_DIR = os.path.join(OUTPUT_DIR, "words_audio")
MANIFEST_PATH = os.path.join(OUTPUT_DIR, "audio_manifest.json")
MODELS_DIR = "../models"

VOICES = ["sv-SE-SofieNeural", "sv-SE-MattiasNeural"]
RATE = "-20%"
MIN_FILE_SIZE = 1024
TTS_MAX_WORKERS = 10
ASR_MAX_WORKERS = 3
WHISPER_MODEL_NAME = "medium"
VERIFICATION_THRESHOLD = 0.85

global_whisper_model = None

def init_worker(model_name):
    """Initializer for Whisper ProcessPoolExecutor"""
    global global_whisper_model
    import whisper
    import warnings
    warnings.filterwarnings("ignore")
    global_whisper_model = whisper.load_model(model_name, download_root=MODELS_DIR)

def ensure_dirs():
    os.makedirs(SENTENCES_DIR, exist_ok=True)
    os.makedirs(WORDS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

def load_data():
    sentences = {}
    words = {}
    
    # Load sentences
    phase2_files = glob.glob(os.path.join(PHASE2_DIR, "article_*.json"))
    for file_path in phase2_files:
        with open(file_path, "r", encoding="utf-8") as f:
            article = json.load(f)
            if isinstance(article, dict):
                for item in article.get("sentences", []):
                    s_id = item["sentence_id"]
                    sv_text = item["sv"]
                    sentences[s_id] = sv_text

    # Load words
    if os.path.exists(MASTER_DICT):
        with open(MASTER_DICT, "r", encoding="utf-8") as f:
            master = json.load(f)
            for base_form in master.get("words", {}).keys():
                words[base_form] = base_form
                
    return sentences, words

def generate_tts_task(task_type, item_id, text, index):
    """Generate audio using Edge-TTS with retry loop"""
    voice = VOICES[index % len(VOICES)]
    
    if task_type == "sentence":
        filename = f"{item_id}.mp3"
        out_dir = SENTENCES_DIR
    else:
        # Sanitize filename
        safe_base = item_id.replace("/", "_")
        filename = f"{safe_base}.mp3"
        out_dir = WORDS_DIR
        
    mp3_path = os.path.join(out_dir, filename)
    
    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) >= MIN_FILE_SIZE:
        return {"id": item_id, "path": mp3_path, "text": text, "voice": voice, "status": "generated"}

    safe_text = shlex.quote(text)
    cmd = f'python3 -m edge_tts --voice {voice} --rate={RATE} --text {safe_text} --write-media "{mp3_path}"'
    
    for attempt in range(10):
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(mp3_path) and os.path.getsize(mp3_path) >= MIN_FILE_SIZE:
                return {"id": item_id, "path": mp3_path, "text": text, "voice": voice, "status": "generated"}
        except Exception:
            pass
        # Cooldown
        time.sleep(1)
        
    return {"id": item_id, "path": mp3_path, "text": text, "voice": voice, "status": "failed"}

def verify_audio_task(task):
    """Verify audio using Whisper model in ProcessPool"""
    if task["status"] != "generated":
        task["verification_score"] = 0.0
        return task
        
    global global_whisper_model
    try:
        result = global_whisper_model.transcribe(task["path"], language="sv")
        transcript = result["text"].lower().strip()
        target_text = task["text"].lower().strip()
        
        # Cleanup
        transcript = "".join([c for c in transcript if c.isalnum() or c.isspace()])
        target_text = "".join([c for c in target_text if c.isalnum() or c.isspace()])
        
        if task.get("type") == "word":
            similarity = 1.0 if target_text == transcript else 0.0
        else:
            distance = Levenshtein.distance(target_text, transcript)
            max_len = max(len(target_text), len(transcript))
            similarity = 1.0 - (distance / max_len) if max_len > 0 else 0.0
            
        task["verification_score"] = similarity
        if similarity >= VERIFICATION_THRESHOLD:
            task["status"] = "verified"
        else:
            task["status"] = "flagged"
            
    except Exception as e:
        task["verification_score"] = 0.0
        task["status"] = "flagged"
        
    return task

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-mode", action="store_true", help="Run on a small subset")
    args = parser.parse_args()

    ensure_dirs()
    print("Loading data...")
    sentences, words = load_data()
    
    if args.test_mode:
        print("TEST MODE: Limiting to 10 sentences and 10 words.")
        sentences = dict(list(sentences.items())[:10])
        words = dict(list(words.items())[:10])
        
    print(f"Total Sentences: {len(sentences)}, Total Words: {len(words)}")
    
    # ---------------------------------------------------------
    # STAGE 1: TTS Generation (High Concurrency ThreadPool)
    # ---------------------------------------------------------
    print("\n--- STAGE 1: Edge TTS Generation ---")
    tts_tasks = []
    
    # Prepare inputs
    s_items = list(sentences.items())
    for i, (s_id, text) in enumerate(s_items):
        tts_tasks.append(("sentence", s_id, text, i))
        
    w_items = list(words.items())
    for i, (w_id, text) in enumerate(w_items):
        tts_tasks.append(("word", w_id, text, i))
        
    generated_results = []
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=TTS_MAX_WORKERS) as executor:
        futures = [executor.submit(generate_tts_task, t_type, id_, text, idx) 
                   for t_type, id_, text, idx in tts_tasks]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            # Inject type
            res["type"] = "sentence" if res["id"] in sentences else "word"
            generated_results.append(res)
            if (i+1) % 50 == 0:
                print(f"TTS Generated: {i+1}/{len(tts_tasks)}")
                
    print(f"Stage 1 completed in {time.time() - start_time:.2f}s")
    
    # ---------------------------------------------------------
    # STAGE 2: ASR Verification (ProcessPool)
    # ---------------------------------------------------------
    print("\n--- STAGE 2: Whisper ASR Verification ---")
    verified_results = []
    start_time = time.time()
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=ASR_MAX_WORKERS, initializer=init_worker, initargs=(WHISPER_MODEL_NAME,)) as executor:
        print(f"Spawning {ASR_MAX_WORKERS} Whisper processes (loading models)...")
        futures = [executor.submit(verify_audio_task, task) for task in generated_results]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            verified_results.append(res)
            if (i+1) % 20 == 0:
                print(f"ASR Verified: {i+1}/{len(generated_results)}")
                
    print(f"Stage 2 completed in {time.time() - start_time:.2f}s")
    
    # ---------------------------------------------------------
    # Generate Manifest
    # ---------------------------------------------------------
    manifest = {
        "metadata": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "voices": VOICES,
            "rate": RATE,
            "total_sentence_files": sum(1 for r in verified_results if r["type"] == "sentence"),
            "total_word_files": sum(1 for r in verified_results if r["type"] == "word")
        },
        "sentences": {},
        "words": {}
    }
    
    for res in verified_results:
        entry = {
            "file": res["path"].replace("../output/", ""),
            "verification_score": res["verification_score"],
            "status": res["status"]
        }
        if res["type"] == "sentence":
            manifest["sentences"][res["id"]] = entry
        else:
            manifest["words"][res["id"]] = entry
            
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        
    print(f"\nManifest saved to {MANIFEST_PATH}")
    
    # Print summary
    failed = sum(1 for r in verified_results if r["status"] == "flagged")
    print(f"\nPipeline Summary: Total={len(verified_results)}, Verified={len(verified_results)-failed}, Flagged={failed}")

if __name__ == "__main__":
    main()
