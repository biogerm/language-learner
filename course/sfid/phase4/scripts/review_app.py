from flask import Flask, render_template_string, jsonify, request, send_from_directory
import json
import os

app = Flask(__name__)

PHASE4_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(PHASE4_DIR, "output", "audio_manifest.json")
PHASE2_DIR = os.path.join(os.path.dirname(PHASE4_DIR), "phase2", "articles")
MASTER_DICT_PATH = os.path.join(os.path.dirname(PHASE4_DIR), "phase1", "master_dictionary.json")

# In-memory storage
manifest_data = {}
target_texts = {}

def load_data():
    global manifest_data, target_texts
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
        
    # Load texts for sentences
    import glob
    for filepath in glob.glob(os.path.join(PHASE2_DIR, "article_*.json")):
        with open(filepath, "r", encoding="utf-8") as f:
            article = json.load(f)
            if isinstance(article, dict):
                for item in article.get("sentences", []):
                    target_texts[item["sentence_id"]] = item["sv"]
                    
    # Load texts for words
    with open(MASTER_DICT_PATH, "r", encoding="utf-8") as f:
        master = json.load(f)
        for base_form in master.get("words", {}).keys():
            target_texts[base_form] = base_form

@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SFI D Audio Review</title>
        <style>
            body { font-family: -apple-system, sans-serif; background: #f5f5f7; color: #1d1d1f; max-width: 800px; margin: 0 auto; padding: 40px; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; }
            h1 { font-size: 24px; color: #0071e3; }
            .text-display { font-size: 32px; font-weight: bold; margin: 30px 0; }
            .controls button { font-size: 18px; padding: 12px 24px; margin: 10px; border: none; border-radius: 8px; cursor: pointer; color: white; font-weight: 600; }
            .btn-pass { background: #34c759; }
            .btn-reject { background: #ff3b30; }
            .stats { margin-top: 30px; color: #86868b; font-size: 14px; }
            .keyboard-hints { margin-top: 20px; font-size: 12px; color: #86868b; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Audio Review</h1>
            <div id="stats" class="stats">Loading...</div>
            <div id="textDisplay" class="text-display">Loading text...</div>
            <audio id="audioPlayer" controls autoplay style="width: 100%; margin: 20px 0;"></audio>
            <div class="controls">
                <button class="btn-reject" onclick="mark('failed')">Reject (R)</button>
                <button class="btn-pass" onclick="mark('verified')">Pass (P)</button>
            </div>
            <div class="keyboard-hints">Keyboard: [Space] Play/Pause | [P] Pass | [R] Reject</div>
        </div>

        <script>
            let currentItem = null;
            let flaggedItems = [];
            
            function fetchFlagged() {
                fetch("/api/flagged")
                    .then(r => r.json())
                    .then(data => {
                        flaggedItems = data.items;
                        document.getElementById('stats').innerText = flaggedItems.length + " items remaining";
                        nextItem();
                    });
            }
            
            function nextItem() {
                if (flaggedItems.length === 0) {
                    document.getElementById('textDisplay').innerText = "All done! 🎉";
                    document.getElementById('audioPlayer').style.display = 'none';
                    return;
                }
                currentItem = flaggedItems.shift();
                document.getElementById('stats').innerText = flaggedItems.length + " items remaining";
                document.getElementById('textDisplay').innerText = currentItem.text;
                document.getElementById('audioPlayer').src = "/audio/" + currentItem.file;
                document.getElementById('audioPlayer').play();
            }
            
            function mark(status) {
                if(!currentItem) return;
                fetch("/api/mark", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({id: currentItem.id, type: currentItem.type, status: status})
                }).then(() => nextItem());
            }
            
            document.addEventListener('keydown', (e) => {
                if (e.key.toLowerCase() === 'p') mark('verified');
                if (e.key.toLowerCase() === 'r') mark('failed');
            });
            
            fetchFlagged();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/audio/<path:filename>")
def serve_audio(filename):
    return send_from_directory(os.path.join(PHASE4_DIR, "output"), filename)

@app.route("/api/flagged")
def get_flagged():
    load_data()
    items = []
    for k, v in manifest_data["sentences"].items():
        if v["status"] == "flagged":
            items.append({"id": k, "type": "sentences", "file": v["file"], "text": target_texts.get(k, k)})
    for k, v in manifest_data["words"].items():
        if v["status"] == "flagged":
            items.append({"id": k, "type": "words", "file": v["file"], "text": target_texts.get(k, k)})
    return jsonify({"items": items})

@app.route("/api/mark", methods=["POST"])
def mark_item():
    data = request.json
    item_type = data["type"]
    item_id = data["id"]
    new_status = data["status"]
    
    if item_type in manifest_data and item_id in manifest_data[item_type]:
        manifest_data[item_type][item_id]["status"] = new_status
        # Save immediately
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=2)
            
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(port=5050)
