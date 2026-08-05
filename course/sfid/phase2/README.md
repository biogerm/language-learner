# Phase 2: Article Generation & Bilingual Translation

## Directory Structure
- `/articles/`: Contains the 57 original, untranslated JSON articles exactly as they were initially generated. This directory is kept pristine and unmodified.
- `/articles_translated/`: Contains the 57 JSON articles with English translations injected. The structure and metadata exactly mirror the original files.
- `/scripts/`: Python scripts used for generation, translation validation, and data cleaning.
- `/archive/`: Contains intermediate outputs and monolithic legacy JSON files.

## Note on Article Titles
In the original generation process, the article generator agent output the placeholder `"Läsförståelse"` for the `article_title` of every single article. Therefore, both the `/articles/` and `/articles_translated/` folders accurately reflect this original state. No synthetic or generated titles have been applied.
