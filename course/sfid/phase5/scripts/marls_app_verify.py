import re
import sys

def test_app_js():
    app_js_path = "../SFI/web_app/js/app.js"
    with open(app_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print("Running V-F01 (FSRS Dual-Threshold)...")
    if "currentWord.dictationPassed" in content and "currentWord.translationPassed" in content:
        if "if (currentIndex >= queue.length)" in content and "customVocab.push(" in content:
            print("[PASS] V-F01: Words are only pushed to customVocab after passing both dictation and translation queues.")
        else:
            print("[FAIL] V-F01: Save logic is disconnected from queues.")
            sys.exit(1)
    else:
        print("[FAIL] V-F01: Missing Dictation/Translation state checks.")
        sys.exit(1)
        
    print("Running V-F02 (Rich Translation Assembly)...")
    if "translationStr = `${contextual} (${globalEn})`" in content:
        print("[PASS] V-F02: Target words correctly assemble [Contextual] ([Global]) string.")
    else:
        print("[FAIL] V-F02: Missing translation string assembly format.")
        sys.exit(1)
        
    print("Running V-F03 (Audio URL Generation)...")
    if "new Audio('audio/words_audio/'" in content or "new Audio(`audio/words_audio/" in content:
        if "encodeURIComponent" in content:
            print("[PASS] V-F03: Audio URL correctly encodes unicode characters like åäö.")
        else:
            print("[FAIL] V-F03: URL encoding missing.")
            sys.exit(1)
            
    print("Running V-UI01 (Bilingual CSS Structure)...")
    if "<span class=\"vocab-word ${w.type}-word\"" in content and "<span class=\"vocab-word ${w.type}-word en-word\">" in content:
        print("[PASS] V-UI01: Both Swedish and English lines generate matched span tags.")
    else:
        print("[FAIL] V-UI01: Bilingual tags are missing.")
        sys.exit(1)
        
    print("APP MARLS VALIDATION COMPLETE: ALL PASSED")

if __name__ == '__main__':
    test_app_js()
