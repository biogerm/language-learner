import { FSRS, type Card, Rating, createEmptyCard } from 'ts-fsrs';
import { db } from '../db/dexie';
import { supabase } from '../services/supabase';

const fsrs = new FSRS({});

export async function syncOfflineProgress() {
    if (!navigator.onLine) {
        window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: 'Offline. Waiting to sync...' }));
        return;
    }

    try {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session?.user) return;
        const userId = session.user.id;

        // 1. PULL: Fetch all remote records from Supabase
        const { data: remoteRecords, error: pullError } = await supabase
            .from('fsrs_progress')
            .select('*')
            .eq('user_id', userId);

        if (pullError) {
            console.error('Supabase pull error:', pullError);
            return;
        }

        const remoteMap = new Map((remoteRecords || []).map(r => [r.word_id, r]));
        const localRecords = await db.fsrs_progress.toArray();
        const localMap = new Map(localRecords.map(r => [r.word_id, r]));

        // 2. RECONCILE: Apply remote state & purge deleted cards
        await db.transaction('rw', db.fsrs_progress, async () => {
            // Delete local cards that were previously synced but removed from server
            for (const local of localRecords) {
                if (local.synced && !remoteMap.has(local.word_id)) {
                    await db.fsrs_progress.delete(local.word_id);
                }
            }

            // Update or insert remote cards into Dexie
            for (const remote of remoteRecords || []) {
                const local = localMap.get(remote.word_id);
                const remoteUpdated = remote.updated_at ? new Date(remote.updated_at).getTime() : 0;
                const localUpdated = local?.updated_at ? new Date(local.updated_at).getTime() : 0;

                if (!local || (local.synced && remoteUpdated >= localUpdated)) {
                    await db.fsrs_progress.put({
                        word_id: remote.word_id,
                        course_id: remote.course_id,
                        state: remote.state,
                        due: new Date(remote.due),
                        stability: remote.stability,
                        difficulty: remote.difficulty,
                        elapsed_days: remote.elapsed_days,
                        scheduled_days: remote.scheduled_days,
                        reps: remote.reps,
                        lapses: remote.lapses,
                        last_review: remote.last_review ? new Date(remote.last_review) : new Date(),
                        todayDictationPassed: remote.today_dictation_passed ?? false,
                        todayFlashcardPassed: remote.today_flashcard_passed ?? false,
                        max_wrongs: remote.max_wrongs ?? 0,
                        max_time: remote.max_time ?? 0,
                        gave_up: remote.gave_up ?? false,
                        reveal_count: remote.reveal_count ?? 0,
                        lastGatePassDate: remote.last_gate_pass_date || null,
                        synced: true,
                        updated_at: remote.updated_at
                    });
                }
            }
        });

        // 3. PUSH: Send any un-synced local changes to Supabase
        const unsynced = await db.fsrs_progress
            .filter(record => !record.synced && !record.sync_error)
            .toArray();

        if (unsynced.length > 0) {
            const payload = unsynced.map(record => ({
                user_id: userId,
                course_id: record.course_id || 'sfid',
                word_id: record.word_id,
                state: record.state,
                due: record.due.toISOString(),
                stability: record.stability || 0,
                difficulty: record.difficulty || 0,
                elapsed_days: record.elapsed_days || 0,
                scheduled_days: record.scheduled_days || 0,
                reps: record.reps || 0,
                lapses: record.lapses || 0,
                last_review: record.last_review ? record.last_review.toISOString() : new Date().toISOString(),
                today_dictation_passed: record.todayDictationPassed ?? false,
                today_flashcard_passed: record.todayFlashcardPassed ?? false,
                max_wrongs: record.max_wrongs || 0,
                max_time: record.max_time || 0,
                gave_up: record.gave_up || false,
                reveal_count: record.reveal_count || 0,
                last_gate_pass_date: record.lastGatePassDate || null,
                updated_at: record.updated_at || new Date().toISOString()
            }));

            const { error: pushError } = await supabase
                .from('fsrs_progress')
                .upsert(payload, { onConflict: 'user_id, course_id, word_id' });

            if (pushError) {
                console.error('Supabase sync push error:', pushError);
            } else {
                await Promise.all(unsynced.map(record => 
                    db.fsrs_progress.update(record.word_id, { synced: true, sync_error: undefined })
                ));
            }
        }

        window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: 'FSRS synchronized' }));
    } catch (err: any) {
        console.error('Error during progress sync:', err);
        window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Sync error: ${err.message}` }));
    }
}

export function calculateFSRSRating(max_wrongs: number, max_time: number, gave_up: boolean, reveal_count: number): Rating {
    const isGaveUp = gave_up === true;
    const wrongs = Number(max_wrongs) || 0;
    const time = Number(max_time) || 0;
    const reveals = Number(reveal_count) || (isGaveUp ? 1 : 0);

    // 1. Again (5 mins interval / reset to relearning)
    // - Both gates gave up / revealed (reveals >= 2): neither hearing nor reading was recalled
    // - Single reveal combined with high error count (reveals >= 1 && wrongs >= 4)
    // - Extreme trial-and-error struggle without reveal (wrongs >= 6)
    // - Severe timeout with multiple errors (time > 60 && wrongs >= 4)
    if (reveals >= 2 || (reveals >= 1 && wrongs >= 4) || wrongs >= 6 || (time > 60 && wrongs >= 4)) {
        return Rating.Again;
    }

    // 2. Hard (1 day interval)
    // - Single-gate reveal (reveals === 1): one gate was looked up, but the other was solved independently!
    //   Capped strictly at Hard (guaranteed impossible to get Good or Easy).
    // - Multiple errors without reveal (3 <= wrongs <= 5)
    // - Noticeable hesitation/errors without reveal (wrongs >= 2 && time > 30)
    if (reveals === 1 || wrongs >= 3 || (wrongs >= 2 && time > 30)) {
        return Rating.Hard;
    }

    // 3. Good (2~3 days interval)
    // - Strictly NO reveals allowed (reveals === 0)
    // - Minor errors (wrongs === 1 || wrongs === 2)
    // - Or 0-1 error but took longer than 15s (time > 15)
    if (reveals === 0) {
        if (wrongs === 2 && time <= 30) return Rating.Good;
        if (wrongs <= 1 && time > 15) return Rating.Good;
    }

    // 4. Easy (3~4 days interval)
    // - Strictly NO reveals allowed (reveals === 0)
    // - Flawless or near-flawless (wrongs <= 1) and quick (time <= 15s)
    if (reveals === 0 && wrongs <= 1 && time <= 15) {
        return Rating.Easy;
    }

    return Rating.Hard;
}

export async function submitGatePass(
    courseId: string, 
    wordId: string, 
    gate: 'dictation' | 'flashcard', 
    wrongs: number, 
    timeSec: number, 
    gave_up: boolean, 
    reveal_count: number,
    manualRating?: Rating
) {
    if (!wordId || typeof wordId !== 'string') return { completed: false };
    const cleanWordId = wordId.trim().toLowerCase();
    if (!cleanWordId) return { completed: false };

    let progress = await db.fsrs_progress.get(cleanWordId);
    if (!progress) {
        progress = await db.fsrs_progress.where('word_id').equalsIgnoreCase(cleanWordId).first();
    }
    if (!progress) {
        const emptyCard = createEmptyCard(new Date());
        progress = {
            word_id: cleanWordId,
            course_id: courseId,
            state: emptyCard.state,
            due: emptyCard.due,
            stability: emptyCard.stability,
            difficulty: emptyCard.difficulty,
            elapsed_days: emptyCard.elapsed_days,
            scheduled_days: emptyCard.scheduled_days,
            reps: emptyCard.reps,
            lapses: emptyCard.lapses,
            last_review: emptyCard.last_review || new Date(),
        };
    } else {
        progress.word_id = cleanWordId;
    }

    const todayStr = new Date().toDateString();
    if (!progress.lastGatePassDate || progress.lastGatePassDate !== todayStr) {
        progress.todayDictationPassed = false;
        progress.todayFlashcardPassed = false;
        progress.max_wrongs = 0;
        progress.max_time = 0;
        progress.gave_up = false;
        progress.reveal_count = 0;
    }
    progress.lastGatePassDate = todayStr;
    
    progress.max_wrongs = (progress.max_wrongs || 0) + (wrongs || 0);
    progress.max_time = Math.max(progress.max_time || 0, Number(timeSec) || 0);
    progress.reveal_count = (progress.reveal_count || 0) + (reveal_count || 0);

    // Mark gate as completed (pass or reveal/gave_up both count as "done" for scheduling purposes)
    if (gate === 'dictation') progress.todayDictationPassed = true;
    if (gate === 'flashcard') progress.todayFlashcardPassed = true;
    // Track gave_up separately
    if (gave_up) progress.gave_up = true;

    // Check if Dual-Gate is complete: both gates done (pass or gave_up)
    if (progress.todayDictationPassed && progress.todayFlashcardPassed) {
        const rating = manualRating !== undefined 
            ? manualRating 
            : calculateFSRSRating(progress.max_wrongs || 0, progress.max_time || 0, !!progress.gave_up, progress.reveal_count || 0);
        
        const card: Card = {
            due: progress.due,
            stability: progress.stability,
            state: progress.state,
            difficulty: progress.difficulty,
            elapsed_days: progress.elapsed_days,
            scheduled_days: progress.scheduled_days,
            reps: progress.reps,
            lapses: progress.lapses,
            last_review: progress.last_review || new Date(),
        } as unknown as Card;

        const isFirstReview = card.state === 0;
        const schedulingCards = fsrs.repeat(card, new Date());
        const newCardState = (schedulingCards as any)[rating].card;

        // Standard FSRS production rule: First-time graduated cards capped at next day (tomorrow)
        if (isFirstReview && rating !== Rating.Again) {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            if (newCardState.due.getTime() > tomorrow.getTime()) {
                newCardState.due = tomorrow;
            }
        }

        // Apply new state and reset gate passes
        progress.state = newCardState.state;
        progress.due = newCardState.due;
        progress.stability = newCardState.stability;
        progress.difficulty = newCardState.difficulty;
        progress.elapsed_days = newCardState.elapsed_days;
        progress.scheduled_days = newCardState.scheduled_days;
        progress.reps = newCardState.reps;
        progress.lapses = newCardState.lapses;
        progress.last_review = newCardState.last_review || new Date();

        progress.todayDictationPassed = false;
        progress.todayFlashcardPassed = false;
        progress.max_wrongs = 0;
        progress.max_time = 0;
        progress.gave_up = false;
        progress.reveal_count = 0;

        progress.synced = false;
        progress.updated_at = new Date().toISOString();
        await db.fsrs_progress.put(progress);
        
        // On Dual-Gate Graduation of initial learning cards: Purge from learning_queue
        if (isFirstReview) {
          try {
            const lqMatches = await db.learning_queue.where('base_form').equalsIgnoreCase(cleanWordId).toArray();
            for (const lq of lqMatches) {
              if (lq.id) await db.learning_queue.delete(lq.id);
            }
            const { data: authData } = await supabase.auth.getUser();
            if (authData?.user) {
              await supabase.from('learning_queue').delete().eq('user_id', authData.user.id).ilike('base_form', cleanWordId);
            }
          } catch (e) {}
        }

        syncOfflineProgress().catch(console.error);

        const nextDue = new Date(newCardState.due);
        const diffTime = nextDue.getTime() - Date.now();
        let diffDays = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
        
        let ratingName = "Hard";
        if (rating === Rating.Again) {
            ratingName = "Again";
            diffDays = 0;
        } else if (rating === Rating.Good) {
            ratingName = "Good";
        } else if (rating === Rating.Easy) {
            ratingName = "Easy";
        }

        let dayStr = "";
        if (rating === Rating.Again) {
            dayStr = "5 mins";
        } else if (diffDays <= 1) {
            dayStr = "1 day";
        } else {
            dayStr = `${diffDays} days`;
        }

        return {
            rating,
            ratingName,
            nextDueDays: diffDays,
            dayStr,
            toastMsg: `${ratingName} | ${dayStr}`,
            nextDue: newCardState.due,
            completed: true
        };
    } else {
        progress.synced = false;
        progress.updated_at = new Date().toISOString();
        await db.fsrs_progress.put(progress);

        // On Single-Gate Pass: Only record in learning_queue for ungraduated cards in initial Study Mode
        if (progress.state === 0) {
          try {
            const existingLq = await db.learning_queue.where('base_form').equalsIgnoreCase(cleanWordId).first();
            if (existingLq && existingLq.id) {
              await db.learning_queue.update(existingLq.id, {
                dictation_passed: !!progress.todayDictationPassed,
                flashcard_passed: !!progress.todayFlashcardPassed,
                synced: false
              });
            }
          } catch (e) {}
        }

        return { completed: false };
    }
}

export async function getFSRSStats(courseId?: string) {
    const all = await db.fsrs_progress.toArray();
    const records = courseId ? all.filter(r => !r.course_id || r.course_id === courseId) : all;
    
    let totalStudied = 0;
    let learning = 0;
    let young = 0;
    let mature = 0;
    let dueTomorrow = 0;
    let totalReps = 0;
    let totalLapses = 0;

    const now = new Date();
    const endOfTomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 2, 0, 0, 0, -1);

    for (const r of records) {
        if (r.state > 0) {
            totalStudied++;
        }
        totalReps += Number(r.reps) || 0;
        totalLapses += Number(r.lapses) || 0;

        if (r.state === 1 || r.state === 3) {
            learning++;
        } else if (r.state === 2) {
            const scheduledDays = Number(r.scheduled_days) || 0;
            if (scheduledDays >= 21) {
                mature++;
            } else {
                young++;
            }
        }

        const due = new Date(r.due);
        if (!isNaN(due.getTime()) && due > now && due <= endOfTomorrow) {
            dueTomorrow++;
        }
    }

    const hitRate = totalReps > 0 ? Math.round(((totalReps - totalLapses) / totalReps) * 100) : 100;

    return {
        totalStudied,
        learning,
        young,
        mature,
        totalReps,
        hitRate,
        dueTomorrow
    };
}

