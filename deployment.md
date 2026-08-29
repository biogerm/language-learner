# Deployment Guide & Architecture Reference

This document describes the deployment architecture, configuration requirements, known environment workarounds, and step-by-step procedures for deploying the **Language Learner** web application.

---

## 1. System Topology & Architecture

| Component | Service / Location | Details / Domain |
| :--- | :--- | :--- |
| **Web Frontend** | Cloudflare Pages | Project: `language-learner-se`<br>Domain: `https://app.languagelearner.se` |
| **Landing Page** | Cloudflare Pages | Project: `language-learner-landing`<br>Domain: `https://www.languagelearner.se` |
| **Asset Storage (R2)** | Cloudflare R2 | Storage for Course JSON & Audio MP3s<br>Domain: `https://cdn.languagelearner.se` |
| **Edge Proxy (API)** | Cloudflare Pages Functions | Route: `/api/r2/*`<br>Implementation: `functions/api/r2/[[catchall]].ts` |
| **Backend & Auth** | Supabase | Authentication & user progress sync (FSRS, dictionary) |

---

## 2. Key Architecture Findings & Mechanisms

### 2.1 Cloudflare Pages Functions as Edge Proxy (`/api/r2/*`)
- **Problem**: When the frontend runs on `app.languagelearner.se`, requesting assets directly from `cdn.languagelearner.se` triggers cross-origin (CORS) security restrictions in web browsers. Furthermore, static `_redirects` rules cannot proxy to external endpoints with HTTP 200 rewrites in Cloudflare Pages (causing SPA HTML fallbacks).
- **Solution**: We employ a Cloudflare Pages Edge Function located at `frontend/functions/api/r2/[[catchall]].ts`. It intercepts `/api/r2/*` requests on the same origin, fetches the target file from `https://cdn.languagelearner.se`, and streams the response back with standard CORS headers (`Access-Control-Allow-Origin: *`).
- **Local Dev vs Prod**:
  - In local development (`npm run dev`), the custom `vite-plugin-r2.ts` plugin mocks and serves `/api/r2/*` directly from S3-compatible R2 credentials.
  - In production (`app.languagelearner.se`), the Cloudflare Pages Function seamlessly serves `/api/r2/*`.

### 2.2 Corporate Proxy / Zscaler SSL Interception Workaround
- **Problem**: In corporate environments running Zscaler or enterprise SSL inspection proxies, Node.js and Wrangler CLI fail during OAuth token refresh and API deployment calls due to certificate mismatch (`UNABLE_TO_GET_ISSUER_CERT_LOCALLY` or `fetch failed`).
- **Solution**: Disable Node TLS rejection when executing Wrangler commands locally:
  ```bash
  export NODE_TLS_REJECT_UNAUTHORIZED=0
  ```
- **Token Cache**: Wrangler stores authenticated session tokens under `~/.wrangler/config/default.toml`. When TLS verification is bypassed, Wrangler can communicate with the Cloudflare API and refresh the OAuth token automatically.

### 2.3 Resilient Course & Vocabulary Hydration Strategy
- **Dictionary Validity Check**: `DataContext.tsx` validates that the cached dictionary in IndexedDB (`db.course_data`) contains non-empty entries. If corrupted or empty, it automatically triggers a fresh remote fetch.
- **Article-Level Sentence Fallback**: If a course lacks a standalone `vocab.json` file, `DataContext.tsx` automatically extracts target vocabulary (`target_words`) directly from the article's sentence nodes, guaranteeing that Dictation and Flashcard modules always load words.
- **Stage & Article Auto-Alignment**: `Layout.tsx` verifies that the active `selectedStage` and `selectedArticleId` exist in the current course's structure, auto-selecting the first valid stage and article to prevent empty UI dropdowns.

---

## 3. Manual Deployment Procedure

To deploy the frontend to Cloudflare Pages from a local terminal:

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Compile TypeScript and build the production bundle
npm run build

# 3. Deploy assets and Edge Functions to Cloudflare Pages
env NODE_TLS_REJECT_UNAUTHORIZED=0 npx wrangler pages deploy dist --project-name language-learner-se
```

---

## 4. CI/CD Deployment Pipeline Analysis & Recommendation

### Should We Establish an Automated Deployment Pipeline?
**Recommendation: YES (Strongly Recommended).**

### Why a CI/CD Pipeline is Beneficial:
1. **Eliminates Local Zscaler / Proxy Issues**:
   - GitHub Actions runners execute in a clean cloud network with valid root certificates, completely eliminating local TLS certificate mismatch errors and manual `NODE_TLS_REJECT_UNAUTHORIZED=0` workarounds.
2. **Eliminates Expiring Local OAuth Tokens**:
   - Instead of relying on local `~/.wrangler/config/default.toml` OAuth tokens (which expire), GitHub Actions uses a permanent `CLOUDFLARE_API_TOKEN` stored securely in GitHub Secrets.
3. **Automated Quality Gates**:
   - Every push/PR can automatically run `npm run lint` and `npm run build` before deploying to staging/production, preventing broken builds from reaching live users.
4. **Instant Multi-Environment Previews**:
   - Pull requests automatically receive isolated preview URLs (`<hash>.language-learner-se.pages.dev`) for testing before merging to `main`.

### Recommended CI/CD Implementation Plan:
- **Option A (Simplest)**: **Cloudflare Pages Native Git Integration**
  - Connect the GitHub repository directly in Cloudflare Pages Dashboard.
  - Set Build Command: `cd frontend && npm run build`
  - Set Output Directory: `frontend/dist`
  - Set Root Directory: `frontend`
  - Set Environment Variables: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_R2_PUBLIC_URL`
- **Option B (Maximum Control)**: **GitHub Actions Workflow**
  - Use `.github/workflows/deploy.yml` with `cloudflare/wrangler-action` or `cloudflare/pages-action` triggered on pushes to `main`.
