# MARLS Execution Plan

> Sole control document. No essential instruction may exist only in chat or another planning/verification file.

## 0. Reader Map

| Section | Mandatory Readers | Use |
|---|---|---|
| 1 Parameters & Approval | All agents; requester approves | Understand the product, constraints, state, and authority |
| 2 Agent Registry | All read; each agent follows its row | Establish real identities, ownership, inputs, and outputs |
| 3 Requirements & Validation | All read; executors/verifiers act on assigned rows | Define what must pass in every applicable loop |
| 4 Loop Plan | All agents | Keep every loop on the same complete product |
| 5 Controller Steps | Controller and current actor | Control sequence and gates |
| 6 Runtime Ledger | Controller writes; all agents confirm | Record coverage, evidence, and decisions |

## 1. Parameters & Approval

- Plan ID / Version: MARLS-Legacy-Fix-V3 / v3
- Request originator: User
- Request and approved assumptions: The previous MARLS loops (v2) partially failed during E2E verification due to dev server crashes. We must execute the exact 10+ user feedback points (excluding Nivåtest renaming 1.1-1.4 per latest request).
- Goal / final product / format: 100% parity with legacy `app.js` functionality regarding Edit Mode, FSRS routing, and Highlighting.
- Inputs and source locations: 
  - `frontend/src/pages/Narration.tsx`, `Flashcard.tsx`, `Dictation.tsx`
  - `frontend/src/components/Layout.tsx`
  - `frontend/src/utils/parser.ts`
- Constraints / exclusions: Use only React/TypeScript/Vite. Database operations must use Supabase/Dexie. **Do NOT modify Nivåtest references**.
- Success criteria: All specified bugs verified fixed by the `/browser` subagent in an end-to-end test.
- Controller: Main thread
- Loop count / active loop / active step: 3 / Loop 3 / Step 1
- Fit Gate / concurrency controls: PASS
- Multi-agent status: ACTIVE
- Plan Approval: PENDING_USER_APPROVAL
- Approved Plan ID / Version / evidence: [Pending Approval]
- Execution Gate: BLOCKED

## 2. Agent Registry

| Domain | Agent Role | Agent ID | Responsibilities | Inputs / Dependencies | Complete Product Output | Req / Check IDs | Required Sections |
|---|---|---|---|---|---|---|---|
| UI & Layout | React Specialist | [Pending] | Fix Layout, Narration Edit mode, Highlighting logic, and Study/Review routing | `Layout.tsx`, `Narration.tsx`, `Flashcard.tsx`, `Dictation.tsx`, `parser.ts` | Complete React UI Codebase | R-01 to R-03 | 1, 3, 4-6 |
| QA | E2E QA Verifier | [Pending] | Run browser tests locally | Vite Dev Server, Browser | E2E Test Report | V-E2E-01 | 1, 3, 4-6 |

## 3. Requirements & Validation

### 3.1 Detailed Implementation Procedure

#### I-01 — Refactor Study vs Review Routing (React Specialist)
1. **Inputs:** `Layout.tsx`, `Flashcard.tsx`, `Dictation.tsx`.
2. **Actions:** 
   - Remove the confusing dual-dropdowns in `Layout.tsx`.
   - Implement a clear top-level mode toggle: **Study Mode** vs **Review Mode**.
   - In Study Mode, navigating to Flashcard or Dictation strictly uses the currently selected Article (with Stage/Article selection visible).
   - In Review Mode, navigating to Flashcard or Dictation uses the global FSRS due cards queue.
3. **Output:** Clean routing and state isolation for Study vs Review.

#### I-02 — Rebuild Inline Edit Mode (React Specialist)
1. **Inputs:** `Narration.tsx`.
2. **Actions:**
   - Ensure Edit button (✏️) is present on each individual sentence.
   - When Edit is clicked, display explicit "Save" and "Cancel" buttons.
   - Allow user to click any word in the sentence to toggle its state (`target` -> `secondary` -> `none`).
3. **Output:** Inline Edit mode in Narration.

#### I-03 — Restore Legacy Highlighting Logic (React Specialist)
1. **Inputs:** `Narration.tsx`, `parser.ts`.
2. **Actions:**
   - In normal Reading Mode (not editing), render the sentence strictly using the legacy `parseSentence` logic which utilizes backend-provided `position_start` and `position_end`.
   - This ensures multi-word phrases (e.g., "tack på förhand") are highlighted as a single cohesive span, fixing the disparity with the legacy version.
3. **Output:** Legacy-compliant highlighting.

### 3.2 Detailed Validation Procedure

#### V-E2E-01 — Comprehensive Full Browser Pass
1. **Linked Req:** All
2. **Setup:** Controller runs `npm run dev` and passes port to `/browser` subagent.
3. **Actions:** 
   - Open browser, login.
   - Verify top-level navigation allows switching between Study and Review explicitly.
   - Go to Narration. Verify legacy multi-word highlighting is correct.
   - Click Edit on a sentence. Verify Save/Cancel buttons appear. Click a word to toggle its highlight. Click Save. 
   - Switch to Flashcards in Study Mode. Verify Stage/Article dropdown exists and FSRS rating buttons do NOT appear.
   - Switch to Flashcards in Review Mode. Verify FSRS rating buttons DO appear.
4. **Evidence:** Browser console logs, DOM state checks.
5. **Threshold:** 100% of these actions succeed without error.
6. **Executor:** `/browser` E2E QA Verifier.

### 3.3 Requirements & Validation Matrix

| Req ID | Type | Requirement | Implementation Step IDs | Check ID | Effect / Scenario | Method & Required Evidence | Pass Criteria | Executor | Verifier | Loops | Per-Loop Result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | F | Study/Review isolation (3.2) | I-01 | V-E2E-01 | UX clearly separates FSRS from local article study | Browser validation | 100% Match | React Sp. | `/browser` | 1-3 | NOT TESTED |
| R-02 | F | Inline Edit Mode (2.2, 2.3) | I-02 | V-E2E-01 | User edits vocab inline w/ Save/Cancel | Browser clicks edit, save, cancel | Works | React Sp. | `/browser` | 1-3 | NOT TESTED |
| R-03 | F | Legacy Highlighting (2.4) | I-03 | V-E2E-01 | Multi-word phrases highlight correctly | Visual/DOM verification | Works | React Sp. | `/browser` | 1-3 | NOT TESTED |

## 4. Loop Plan

| Loop | Same Complete Product Target | Agents | Required Check IDs | Red-Team Focus | Completion Gate |
|---|---|---|---|---|---|
| 1 | Complete React UI Codebase | React Sp., `/browser` | V-E2E-01 | Resolving foundational regressions (FAILED/ABORTED) | All Must pass; 100% checks covered |
| 2 | Complete React UI Codebase | React Sp., `/browser` | V-E2E-01 | UI implementation of fixes (PARTIAL/ABORTED) | All Must pass; all agents confirm coverage |
| 3 | Complete React UI Codebase | React Sp., `/browser` | V-E2E-01 | Final UI polish & strict legacy parity (ACTIVE) | All Must pass; all agents confirm coverage |

## 5. Controller Steps

| Step | Starts After | Reader / Actor | Required Action and Plan Update | Complete When |
|---|---|---|---|---|
| 1 | Requester approves exact version | Controller | Read full plan; open gate; invoke agents; record IDs | Multi-agent ACTIVE |
| 2 | Step 1 / prior loop gate | All agents | Read assigned plan sections and acknowledge version, scope, output, checks | All acknowledged |
| 3 | Step 2 | Domain agents | Produce, red-team, and fully rewrite complete outputs | Outputs returned |
| 4 | Step 3 | Executors / verifiers | Run every assigned check on rewritten outputs; return fresh evidence | Assigned coverage 100% |
| 5 | Step 4 | Controller / all agents | Update ledger; circulate global coverage; correct and re-validate gaps | All IDs covered and confirmed |
| 6 | Step 5 | Controller | Close loop and activate next loop or aggregate final product | Gate decision recorded |

## 6. Runtime Ledger

| Loop | Agent ID | Plan Version | Product Status | Assigned / Returned Check IDs | Coverage / Evidence | Global Confirmation | Controller Gate |
|---|---|---|---|---|---|---|---|
| 1 | React Sp. & `/browser` | v1 | ABORTED (Dev Server Crashed) | V-E2E-01 | 0% | GAPS | CLOSED |
| 2 | React Sp. & `/browser` | v2 | ABORTED (Sidetracked by bugs) | V-E2E-01 | 0% | GAPS | CLOSED |
| 3 | [Pending] | v3 | NOT_STARTED | V-E2E-01 | 0% | PENDING | BLOCKED |
