# Phase 5: Frontend Data Assembly & HTML Printing

## 1. Overview

This final phase prepares the generated data for consumption by the end-user facing systems: the web application and physical printouts.

The pipeline takes the outputs from Phase 1 (Master Dictionary) and Phase 2 (Article JSONs) to generate static JavaScript data files that the frontend application loads. It also takes the generated articles and compiles them into a printable HTML file formatted specifically for A4 paper.

```mermaid
graph TD
    A[Phase 1: master_dict.json] --> C[Frontend Assembler]
    B[Phase 2: Structured Articles] --> C
    C --> D[data.js (Articles)]
    C --> E[global_dict.js (Vocab)]
    B --> F[HTML Print Generator]
    F --> G[sfid_b1_articles.html]
```

## 2. Frontend Data Interfaces

The frontend application requires the data to be injected as global JavaScript variables. This allows the static frontend to operate without a backend server.

### 2.1 Dictionary Interface (`global_dict.js`)

The `master_dict.json` must be flattened into a simple key-value store. This powers the "Extract Vocab" feature in the frontend (specifically `app.js` lines 200-464), which looks up words highlighted by the user and displays their translations.

**Output Specification (`global_dict.js`):**
```javascript
// Auto-generated from master_dict.json. DO NOT EDIT.
window.globalDictionary = {
    "soffpotatis": "couch potato",
    "träna": "exercise, work out",
    "granne": "neighbor"
};
```

### 2.2 Article Data Interface (`data.js`)

The generated articles from Phase 2 must be assembled into a single JavaScript object mirroring the **Course -> Stage -> Article** hierarchy.

**Output Specification (`data.js`):**
```javascript
// Auto-generated. DO NOT EDIT.
window.APP_DATA = {
  "course_id": "sfid",
  "course_title": "SFI D",
  "stages": [
    {
      "stage_id": "stage_01",
      "stage_title": "Daily Life and Health",
      "articles": [
        {
          "article_id": "art_01",
          "article_title": "En dag på gymmet",
          "target_word_count": 25,
          "sentences": [
            {
              "sentence_id": "art01_s001",
              "sv": "Min granne är en riktig soffpotatis som aldrig tränar.",
              "en": "My neighbor is a real couch potato who never exercises.",
              "target_words": [
                {
                  "word_in_sentence": "soffpotatis",
                  "base_form": "soffpotatis",
                  "position_start": 25,
                  "position_end": 36
                },
                {
                  "word_in_sentence": "tränar",
                  "base_form": "träna",
                  "position_start": 48,
                  "position_end": 54
                }
              ]
            }
          ]
        }
      ]
    }
  ]
};
```

### 2.3 Dictation Data Interface (`dictation_data.js`)

Phase 5 must extract all `target_words` with their context from the Phase 2 Article JSONs to generate the dataset for the frontend's "Dictation" and "Flashcard" modes.
To allow the frontend to display both the contextual meaning and the standard dictionary definition, this interface **must** cross-reference the master dictionary during generation:

**Assembly Logic:**
1. Iterate over all sentences in the articles and extract all `target_words`.
2. Extract the Swedish base form (`base_form`) and the contextual translation (`contextual_en` mapped to `en`).
3. Use the `base_form` to look up the standard global translation in `master_dict.json`.
4. Inject this global translation as a new field named `dictionary_en`.
5. When rendering in the frontend App, `dictionary_en` should be displayed in parentheses next to the original explanation.

**Output Specification (`dictation_data.js`):**
```javascript
// Auto-generated from articles and master_dict.json. DO NOT EDIT.
window.DICTATION_WORDS = [
  {
    "sv": "gå",
    "en": "went",
    "dictionary_en": "go, walk",
    "context_sv": "Han gick hem.",
    "stage": "Daily Life and Health",
    "article": "En dag på gymmet",
    "course_id": "sfid"
  }
];
```

## 3. Web App UI & FSRS Logic

The frontend web application must process the generated `data.js` to provide an interactive reading experience and integrate with the Spaced Repetition System (FSRS).

### 3.1 Learning Queue & Word Storage Architecture

To ensure high-quality spaced repetition and correct data lifecycle management, the system must implement **two separate data stores** and a strict entry protocol.

#### Store A: Staging Queue (Temporary)
A lightweight data store used as an **in-progress learning queue**. Words are placed here when they enter the "Initial Learning Queue" and are removed once the word has been mastered (passed the double threshold). This store handles **Target Words** and **Secondary Words** — words that are already indexed in the master dictionary.

*   **Target Words**: Automatically enter Store A alongside the article load. No user action required.
*   **Secondary Words / Dictionary Lookup**: During reading, if the user taps the 📖 button, selects a word, and clicks "Save", it enters Store A. At this point, the system MUST assemble the word's record by combining:
    *   `contextual_en` (from the sentence's JSON) — the in-context meaning
    *   The global translation from `global_dict.js` — the base dictionary meaning
    *   Combined format: `[Contextual Translation] ([Master Dictionary Global Translation])` (e.g., `couch potato (someone who lies on the sofa, inactive)`)

**Record Schema for Store A** (must mirror the master dictionary structure to allow full index-based retrieval during review):

| Field | Source | Notes |
|---|---|---|
| `base_form` | sentence JSON | Primary key / lookup index |
| `word_type` | `word_metadata.json` | verb, noun, adjective, etc. |
| `en_translation` | Combined (contextual + global) | As assembled above |
| `sv_context` | sentence JSON (`sv` field) | The full Swedish example sentence |
| `sentence_audio_filename` | sentence JSON | Filename only, no path |
| `contextual_en` | sentence JSON | Precise in-context translation |
| `source` | article metadata | Which article the word came from |

**Double Threshold (Removal Rule)**: A word is removed from Store A once it passes both:
- ✅ **Dictation Mode**: 100% correct
- ✅ **Translation Mode**: 100% correct

Because Target and Secondary words already exist in the master dictionary, they do **not** need to be persisted after mastery — removing them from Store A is sufficient.

---

#### Store B: Permanent Custom Vocabulary (Persistent)
A permanent, long-lived data store for **user-defined custom words** — words that do not appear in the article data but the user still wants to learn. This store is **never pruned after mastery**; it functions as the user's personal vocabulary library (analogous to an FSRS deck).

*   **Trigger**: The user can manually add a word at any time (e.g., from an external source, a physical book, or a conversation).
*   **User Input Required**: The user must manually enter the English translation, as the system cannot infer it from the article data.
*   **System Auto-Saves**: The system should attempt to auto-populate as many fields as possible (e.g., looking up `word_type` and inflections from the SQLite database if the word exists there). Fields that cannot be resolved (e.g., `sv_context`, `sentence_audio_filename`) are left empty.

**Record Schema for Store B**:

| Field | Source | Notes |
|---|---|---|
| `base_form` | User input | Primary key |
| `en_translation` | User input (mandatory) | Manually entered by user |
| `word_type` | Auto-resolved from DB | If found in SQLite, else empty |
| `sv_context` | Auto-resolved from DB | If found in SQLite, else empty |
| `sentence_audio_filename` | Auto-resolved from DB | If found in SQLite, else empty |
| `notes` | User input (optional) | Free-text personal notes |

**Double Threshold (Retention Rule)**: Even after a Store B word passes the double-threshold validation, it is **retained permanently**. The user's custom vocabulary is a personal asset and must not be deleted.

### 3.2 Bilingual Highlighting (Dual-Sided Rendering)
In the reading mode UI layer (e.g., `renderSentences`), implement seamless bilingual alignment highlighting to map the Swedish text to the English translation:
*   **Target Words (Core Vocabulary)**:
    *   **Swedish Side (sv)**: Match the `word_in_sentence` string and render prominently (e.g., **bold + gold** color).
    *   **English Side (en)**: Match the extracted `contextual_en` string and render with the exact same styling (**bold + gold**).
*   **Secondary Words (Auxiliary Vocabulary)**:
    *   **Swedish Side (sv)**: Match the `word_in_sentence` string and render with secondary styling (e.g., blue dashed underline).
    *   **English Side (en)**: Match the `contextual_en` string and render with the corresponding secondary styling (blue dashed underline).

This dual-sided rendering ensures that when a student reads, their eyes can immediately map the contextual meaning between the two languages.

## 4. Printable HTML Generation

To satisfy the requirement of providing printable physical study materials, the pipeline must generate a standalone HTML file containing all articles formatted for A4 printing.

### 4.1 Layout & Formatting Requirements

*   **Print Target**: A4 paper (`size: A4`).
*   **Page Breaks**: Every article MUST start on a new physical page using CSS `page-break-before: always;`.
*   **Typography**: Use highly legible fonts for print (e.g., Arial, Helvetica, sans-serif) at 12pt minimum.
*   **Visual Highlights**: Target words must be styled using the `position_start` and `position_end` indices from the JSON to wrap the word in a `<strong>` or `<mark>` tag.
    *   *Example*: `Min granne är en riktig <strong>soffpotatis</strong> som aldrig tränar.`
*   **Translation Handling**: The English translation (`en`) should be printed immediately below the Swedish sentence (`sv`) in a smaller, lighter font, or organized in a side-by-side table format.
*   **Metadata Header**: The top of the first page should include the Course Title, Level (SFI D / B1), and Generation Date.

### 4.2 HTML Output Path
*   **File Path**: `print/sfid_b1_articles.html`

### 4.3 CSS Print Example
The generator script must inject the following CSS block into the generated HTML:
```html
<style>
    @media print {
        @page { size: A4; margin: 20mm; }
        body { font-family: Arial, sans-serif; font-size: 12pt; line-height: 1.5; }
        .article { page-break-before: always; }
        .article:first-child { page-break-before: avoid; }
        .sentence-sv { font-weight: normal; margin-bottom: 2px; }
        .target-word { font-weight: bold; text-decoration: underline; }
        .sentence-en { font-size: 10pt; color: #555; margin-bottom: 15px; font-style: italic; }
    }
</style>
```

## 5. Execution Steps

1.  Read `master_dict.json`.
2.  Format into Key-Value pairs and wrap in `window.globalDictionary = ...`.
3.  Write to the external application directory `<web_app_dir>/js/global_dict.js`.
4.  Read all Article JSONs in the `chapters/` directory.
5.  Combine them into the nested `Course -> Stage -> Article` structure.
6.  Wrap in `window.APP_DATA = ...`.
7.  Write to the external application directory `<web_app_dir>/js/data.js`.
8.  Extract `target_words` from articles and cross-reference with `master_dict.json` to generate an array of vocabulary objects with a `dictionary_en` field.
9.  Wrap in `window.DICTATION_WORDS = ...` and write to `<web_app_dir>/js/dictation_data.js`.
10. Pass the Article JSONs to an HTML templating engine (e.g., Jinja2 or custom string interpolation) and write `print/sfid_b1_articles.html`.
