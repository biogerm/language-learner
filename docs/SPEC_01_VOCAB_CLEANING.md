# Phase 1: Vocabulary Extraction, Cleaning & Dictionary Generation

## 1. Overview

This phase (Phase 1) is the foundational step of the data pipeline. Its goal is to ensure that every Swedish vocabulary word extracted for the curriculum has a correct, complete English translation. 

Because subsequent phases (like Article Generation) rely heavily on the accuracy of the dictionary to generate contextual sentences, **this phase must strictly precede Phase 2**. 

Original vocabulary files extracted from PDFs (JSON format) often contain dirty data due to formatting artifacts (e.g., soft-hyphen truncation, grammatical information overriding translations, split phrasal verbs). This pipeline will receive the raw input, apply automated cleaning rules and AI-assisted repair, and output a pristine, verified Master Dictionary.

> [!NOTE]
> The integrity of the dictionary data is critical. The frontend uses a flat JavaScript object `globalDictionary` (`{ "word": "translation" }`). The "Extract Vocab" mode allows users to select words in articles, and the system automatically looks them up via `globalDictionary[word.toLowerCase()]` to save to their personal vocabulary list.

## 2. Input Specification

### 2.1 Input Flexibility
The pipeline is designed to be highly flexible regarding input sources. The input could be:
1.  **Translated JSON**: A dictionary mapping Swedish words to English translations (e.g., extracted from a textbook PDF).
2.  **Raw Wordlist**: A simple text list of Swedish words without translations.
3.  **Raw Article Text**: A block of Swedish text from which the pipeline must first extract the core vocabulary.

> [!TIP]
> **For the current project**, the input is specifically the **Translated JSON** format, sourced from the textbook vocabulary lists.

### 2.2 Primary Inputs (Current Project)
*   `b1_ordlista.json`: B1 level vocabulary list (approx. 3,433 entries, ~30 defective entries)
*   `RivstartB1B2_Ordlista_engelska.pdf` and `rivstart_B1_B2_TB__ordkort_1.pdf`: The original textbook and flashcard PDF files. Used as the ground-truth reference for repairing defective entries.
*   `ok_b1_ordlista.json`: B1 level supplementary vocabulary (46 clean entries)
*   `b1_extra.json`: B1 extra vocabulary (233 entries, source and translation share the same form)

### 2.3 Parameters (Inherited)
These parameters are defined here in Phase 1 and **MUST be inherited** by all subsequent phases (Phase 2 to 5):
*   `source_level` (String): The target processing level. **Default: `"B1"`**. (Note: For this project, the level is strictly B1, corresponding to SFI D).
*   `native_language` (String): The target translation language. **Default: `"english"`**.
*   `include_extras` (Boolean): Whether to include words from the `extra.json` files. **Default: `false`**.

## 3. Data Cleaning Rules

The input JSON must be traversed and repaired according to the following specific rules. 

> [!IMPORTANT]
> **Ground Truth Rule**: The errors described below are artifacts of the PDF extraction process. To fix them, the system MUST NOT rely on the AI to "guess" or hallucinate the repair. Instead, the script must use a PDF parsing library (e.g., `pdfplumber` or `PyMuPDF`) to actively search the original PDF files (`RivstartB1B2_Ordlista_engelska.pdf` or `rivstart_B1_B2_TB__ordkort_1.pdf`) for the corrupted fragment, locate its exact position on the page, extract the surrounding text block directly from the PDF, and use that original ground-truth context to correct the error.

The repair process must maintain an Audit Trail.

### 3.1 Soft-Hyphen Truncation Fix
*   **Condition**: The JSON value string contains a soft hyphen `\u00ad`.
*   **Logic**: Search for the truncated key or value in the original PDF. Extract the full, unbroken line. Use this line to determine the complete English translation and remove the soft hyphen.
*   **Example**:
    *   Input: `"människa": "human being, per\u00ad"`
    *   Action: Find "human being, per" in the PDF, retrieve full line "människa human being, person".
    *   Output: `"människa": "human being, person"`

### 3.2 Grammar Info Replacement Fix
*   **Condition**: The JSON value string starts with `(-` or `(+` (these are Swedish conjugation patterns, not English translations).
*   **Logic**: This happens when the PDF parser grabbed the grammatical suffix instead of the translation. Search the original PDF for the key, extract the surrounding lines to find the actual English translation that follows the grammar info.
*   **Example**:
    *   Input: `"sammanfatta": "(-r, -de, -t)"`
    *   Action: Find "sammanfatta" in the PDF, read the adjacent text containing the English translation.
    *   Output: `"sammanfatta": "summarize"`

### 3.3 Phrasal Verb Split Fix
*   **Condition**: The JSON value is solely a Swedish particle or preposition (e.g., `på`, `av`, `ut`, `upp`).
*   **Logic**: This happens when a phrasal verb is split across lines in the PDF. Search the original PDF for the key adjacent to the preposition. Merge them into a new key, extract the actual English translation from the surrounding text, and delete the original split entries.
*   **Example**:
    *   Input: `"stöta": "på"`
    *   Action: Locate "stöta på" in the PDF, retrieve the adjacent English translation.
    *   Output: `"stöta på": "run into, encounter"`

### 3.4 Line-Wrap Orphan Cleanup
*   **Condition**: The JSON key consists only of English characters (no Swedish special characters like `å, ä, ö`) **AND** is very short (usually `< 5` characters). These are typically PDF line-break artifacts.
*   **Logic**: Search the PDF to confirm these are orphaned fragments of a previous line's English translation. Permanently delete these entries as keys, as their valid content has been merged in steps 3.1-3.3.
*   **Example**:
    *   Detected: `"ne": "well known in the arts"`, `"ty": "flower"`, `"me": "my jacket?"`
    *   Action: Removed from the dataset.

## 4. Translation Completion

After executing all cleaning rules, a comprehensive check must be performed to ensure every valid word has a legitimate English translation.
*   **Logic**:
    1.  Collect all words where the value is an empty string (`""`), `null`, or was deemed invalid in the previous step.
    2.  Use the AI for **Batch Translation**. Send words to the AI in batches of 50 to prevent hitting API token limits.
    3.  Force the AI to return results in JSON format: `{ "word": "translation" }`.
    4.  Validate the response to ensure all requested words received non-empty translations.

## 5. Output Specification

Upon completion, the system must output the Master Dictionary JSON (`master_dictionary.json`). This file is the fundamental persistent data source containing structured metadata and vocabulary details.

```json
{
  "metadata": {
    "level": "B1",
    "source": "rivstart_b1",
    "total_words": 3433,
    "generated_at": "2025-01-01T00:00:00Z"
  },
  "words": {
    "soffpotatis": {
      "en": "couch potato",
      "word_class": "noun",
      "gender": "en"
    },
    "träna": {
      "en": "exercise, work out",
      "word_class": "verb",
      "gender": null
    }
  }
}
```
> [!TIP]
> If `word_class` and `gender` cannot be fully determined by rules or AI in this phase, they can be set to `null` and refined in later phases. However, the `en` (translation) field MUST contain a non-empty string.

## 6. Validation Rules

Perform data validation before finalizing the output. If any violations occur, the script must throw an exception and halt.

*   **Key Rules**: Must contain at least one letter (supports `å, ä, ö`). For multi-word phrases, spaces are allowed, but unresolved PDF fragments are not.
*   **Value Rules**:
    *   Must be a non-empty string.
    *   **MUST NOT** contain the soft hyphen `\u00ad`.
    *   **MUST NOT** start with `(-` or `(+`.
*   **Uniqueness**: No duplicate keys allowed in the dictionary (duplicates must be merged or deduped).
*   **Encoding**: All files must be saved in **UTF-8**.

## 7. Interfaces with Other Phases

The output generated here (`master_dictionary.json`) is the central hub for the entire application data pipeline. It directly feeds into:

*   **Phase 2 (Article Generation)**: Provides the verified target vocabulary list that the AI must use to generate reading materials.
*   **Phase 3 (Database Export)**: Provides the base forms and translations for SQLite insertion.
*   **Phase 4 (Audio TTS)**: Provides the exact word list for generating Edge TTS audio files.
*   **Phase 5 (Frontend Integration)**: Transformed into `global_dict.js` to support the UI's text translation extraction feature.

## 8. Prompt Templates

Use the following Prompt templates to drive the LLM for repair and translation tasks.

### 8.1 AI Defect Repair Prompt
```text
You are a data extraction assistant. We have some corrupted entries from a Swedish vocabulary dictionary extracted from a PDF. 

Instead of guessing, I will provide you with the corrupted JSON entry, AND the raw text block extracted from the original PDF surrounding this entry.
Your task is to use the raw PDF text to find the correct, full Swedish word/phrase and its English translation.

Input Corrupted JSON:
{
  "människa": "human being, per\u00ad"
}

Raw PDF Text Context:
"...
djur animal
människa human being, person
sammanfatta (-r, -de, -t) summarize
..."

Provide ONLY the repaired JSON as your response:
{
  "människa": "human being, person"
}
```

### 8.2 AI Batch Translation Prompt
```text
You are an expert Swedish to English translator. Please translate the following list of Swedish vocabulary words into English. Provide concise translations suitable for a language learner's dictionary.

If a word has multiple common meanings, provide a short comma-separated list.
Input (List of Swedish words):
["soffpotatis", "träna", "att", "tro"]

Respond ONLY with a valid JSON object where the key is the Swedish word and the value is the English translation:
{
  "soffpotatis": "couch potato",
  "träna": "exercise, work out",
  "att": "to",
  "tro": "believe, think"
}
```

## 9. Error Handling

*   **AI Retry Mechanism**: If the AI returns unstructured format (non-JSON), times out, or leaves translations blank (e.g., `""` or `null`), the system must **retry up to 3 times** before throwing an error.
*   **Audit Trail**:
    *   Create a `dictionary_cleaning.log` file.
    *   All entries modified by rules `3.1` through `3.4` must append the original and modified data to the log.
    *   Any word that remains untranslated after 3 retries must be marked as `[ERROR_UNTRANSLATED]` in the log for manual intervention.
