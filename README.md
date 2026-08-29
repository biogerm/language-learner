# Language Learner Cloud (LLC)

An AI-powered language learning platform currently configured for Swedish (CEFR B1 / SFI D level).

This project features a comprehensive ecosystem that takes raw vocabulary data, processes it into structured learning materials using AI, and serves it through a modern web application with offline-first capabilities and spaced repetition.

## Architecture Overview

The platform consists of three main components:

### 1. Data Pipeline (`/scripts` & `/docs`)
A robust 5-phase Python pipeline that transforms raw vocabulary into a structured, dual-language database and generates audio assets.
- **Vocabulary Extraction**: Cleans raw data and ensures translation accuracy using AI.
- **Article Generation**: AI generates CEFR B1 standard Swedish articles incorporating target vocabulary.
- **Database Export**: Exports to a SQLite database (`b1_vocab.db`) for backend/mobile consumption.
- **Audio TTS**: Generates Edge TTS audio for words and sentences with closed-loop Whisper ASR verification.
- **Frontend Assembly**: Packages final JSON data for the web application.
> See the `/docs` folder for detailed technical specifications (Spec 01 - 05).

### 2. Web Application (`/frontend`)
A modern React SPA (Single Page Application) built with Vite.
- **Offline-First Storage**: Uses Dexie (IndexedDB) for local data persistence.
- **Cloud Synchronization**: Uses Supabase for syncing user progress and data across devices.
- **Spaced Repetition (FSRS)**: Implements the Free Spaced Repetition Scheduler for optimal learning efficiency.
- **Learning Modes**: Features Narration, Dictation, and Flashcard learning modes.

### 3. Landing Page (`/landing-page`)
The marketing and entry point for the application.

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.10+ (for running the data pipeline)

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Deployment & CI/CD
For production deployment instructions and architecture details, see the [Deployment Guide](deployment.md).

## Security & Privacy Note
This repository does NOT contain any API keys, sensitive environment variables (`.env`), or proprietary raw PDF data. If you are setting this up locally, you will need to provide your own API keys for AI services (OpenAI/Gemini) and Supabase.
