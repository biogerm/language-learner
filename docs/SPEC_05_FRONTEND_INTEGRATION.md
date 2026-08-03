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

The generated articles from Phase 2 must be assembled into a single JavaScript object mirroring the **Course -> Step -> Article** hierarchy.

**Output Specification (`data.js`):**
```javascript
// Auto-generated. DO NOT EDIT.
window.APP_DATA = {
  "course_id": "sfid",
  "course_title": "SFI D",
  "steps": [
    {
      "step_id": "step_01",
      "step_title": "Daily Life and Health",
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

## 3. Printable HTML Generation

To satisfy the requirement of providing printable physical study materials, the pipeline must generate a standalone HTML file containing all articles formatted for A4 printing.

### 3.1 Layout & Formatting Requirements

*   **Print Target**: A4 paper (`size: A4`).
*   **Page Breaks**: Every article MUST start on a new physical page using CSS `page-break-before: always;`.
*   **Typography**: Use highly legible fonts for print (e.g., Arial, Helvetica, sans-serif) at 12pt minimum.
*   **Visual Highlights**: Target words must be styled using the `position_start` and `position_end` indices from the JSON to wrap the word in a `<strong>` or `<mark>` tag.
    *   *Example*: `Min granne är en riktig <strong>soffpotatis</strong> som aldrig tränar.`
*   **Translation Handling**: The English translation (`en`) should be printed immediately below the Swedish sentence (`sv`) in a smaller, lighter font, or organized in a side-by-side table format.
*   **Metadata Header**: The top of the first page should include the Course Title, Level (SFI D / B1), and Generation Date.

### 3.2 HTML Output Path
*   **File Path**: `print/sfid_b1_articles.html`

### 3.3 CSS Print Example
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

## 4. Execution Steps

1.  Read `master_dict.json`.
2.  Format into Key-Value pairs and wrap in `window.globalDictionary = ...`.
3.  Write to `frontend/js/global_dict.js`.
4.  Read all Article JSONs in the `chapters/` directory.
5.  Combine them into the nested `Course -> Step -> Article` structure.
6.  Wrap in `window.APP_DATA = ...`.
7.  Write to `frontend/js/data.js`.
8.  Pass the Article JSONs to an HTML templating engine (e.g., Jinja2 or custom string interpolation) and write `print/sfid_b1_articles.html`.
