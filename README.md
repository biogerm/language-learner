# SFI D Language Learner Data Pipeline

This repository contains the data pipeline for generating Swedish language learning materials (CEFR B1 / SFI D level) from raw vocabulary lists.

## Architecture

The data pipeline consists of 5 phases, orchestrated to transform raw vocabulary into a structured, dual-language database and audio assets for frontend consumption.

1. **Phase 1: Vocabulary Extraction & Cleaning** - Cleans raw JSON data extracted from PDFs, fixes encoding issues, and uses AI to ensure all translations are accurate.
2. **Phase 2: Structured Article Generation** - Uses AI to generate CEFR B1 standard Swedish articles that incorporate 100% of the target vocabulary in a 3-layer architecture (`Course` -> `Step` -> `Article`).
3. **Phase 3: Database Export (SQLite)** - Joins vocabulary and context sentences, exporting to a SQLite database (`b1_vocab.db`) for backend and mobile consumption.
4. **Phase 4: Audio TTS** - Generates Edge TTS audio for words and sentences, with closed-loop Whisper ASR verification.
5. **Phase 5: Frontend Assembly & HTML Print** - Packages the final JSON data for the web application and generates A4 printable HTML materials.

## Directory Structure
- `/course/sfid/data/` - Raw input vocabulary data (JSON/TXT).
- `/scripts/` - Python pipeline scripts.
- `/docs/` - Detailed technical specifications for each phase of the pipeline.
