# Language Learner Web App

This is the frontend component of the Language Learner Cloud (LLC) project, a modern React application built with Vite.

## Tech Stack
- **Framework**: React 19 + Vite
- **Routing**: React Router DOM
- **Local Storage**: Dexie (IndexedDB wrapper)
- **Cloud Database**: Supabase (PostgreSQL)
- **Spaced Repetition**: `ts-fsrs`

## Architecture Highlights

### Dual-Layer Storage
The app is designed to be **Offline-First**. 
1. **Dexie.js** acts as the primary data source for the UI. It provides instant load times and offline capabilities.
2. **Supabase** acts as the cloud synchronization layer, ensuring that user progress (like FSRS logs, custom words, and mastery levels) is safely backed up and synced across devices.

### Learning Logic (FSRS)
We use the **Free Spaced Repetition Scheduler (FSRS)** algorithm to manage the learning queue. 
- Words are classified into three types: `Target` (core vocabulary), `Secondary` (contextual vocabulary), and `Custom` (user-added words).
- When a user studies an article, the system queues these words for dictation and flashcard review, automatically calculating the optimal next review date based on the user's performance.

### Independent Module Versioning
The core learning experiences are split into independent modules:
- **Narration**
- **Dictation**
- **Flashcard**

Each of these modules is versioned independently. When updates are made to the logic or UI of a specific module, only its version badge (and the `moduleVersions` in `package.json`) is bumped.

## Development Scripts

```bash
npm run dev      # Start local development server
npm run build    # Build for production
npm run lint     # Run oxlint
npm run preview  # Preview the production build locally
```

### Testing
End-to-End (E2E) and automated tests (Playwright/Puppeteer) are located in the `e2e/` directory.

```bash
# Example: Run E2E tests (if configured in package.json)
npx playwright test
```
