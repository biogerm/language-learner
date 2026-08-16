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

        const unsynced = await db.fsrs_progress
            .filter(record => !record.synced && !record.sync_error)
            .toArray();

        if (unsynced.length === 0) return;

        const payload = unsynced.map(record => ({
            user_id: session.user.id,
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
            updated_at: new Date().toISOString()
        }));

        const { error } = await supabase
            .from('fsrs_progress')
            .upsert(payload, { onConflict: 'user_id, course_id, word_id' });

        if (error) {
            console.error('Supabase sync error:', error);
            if (error.code === '42501' || error.message?.includes('RLS') || error.message?.includes('violates row-level security')) {
                await Promise.all(unsynced.map(record => 
                    db.fsrs_progress.update(record.word_id, { sync_error: error.message })
                ));
                window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Sync blocked: Permission denied` }));
            } else {
                window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Sync failed. Retrying later...` }));
            }
            return;
        }

        await Promise.all(unsynced.map(record => 
            db.fsrs_progress.update(record.word_id, { synced: true, sync_error: undefined })
        ));
        console.log(`Successfully synced ${unsynced.length} records.`);
        window.dispatchEvent(new CustomEvent('fsrs-sync', { detail: `Synced ${unsynced.length} cards` }));
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

    // 1. Again
    if (reveals > 4 || wrongs > 20 || time > 60) return Rating.Again;
    
    // 2. Hard
    if (reveals === 3 || reveals === 4) return Rating.Hard;
    if (wrongs >= 3 && wrongs <= 20) return Rating.Hard;
    if (wrongs === 2 && time > 20) return Rating.Hard;

    // 3. Good
    if (reveals === 2) return Rating.Good;
    if (wrongs <= 1 && time > 15) return Rating.Good;
    if (wrongs === 2 && time <= 20) return Rating.Good;

    // 4. Easy
    if (reveals < 2 && wrongs <= 1 && time <= 15) return Rating.Easy;

    return Rating.Hard;
}

export async function submitGatePass(courseId: string, wordId: string, gate: 'dictation' | 'flashcard', wrongs: number, timeSec: number, gave_up: boolean, reveal_count: number) {
    let progress = await db.fsrs_progress.get(wordId);
    if (!progress) {
        const emptyCard = createEmptyCard(new Date());
        progress = {
            word_id: wordId,
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
    }

    const todayStr = new Date().toDateString();
    if (progress.todayDictationPassed || progress.todayFlashcardPassed) {
        if (!progress.lastGatePassDate || progress.lastGatePassDate !== todayStr) {
            const isNewCard = progress.state === 0;
            if (!isNewCard) {
                progress.todayDictationPassed = false;
                progress.todayFlashcardPassed = false;
                progress.max_wrongs = 0;
                progress.max_time = 0;
                progress.gave_up = false;
                progress.reveal_count = 0;
            }
        }
    }
    progress.lastGatePassDate = todayStr;
    
    // Accumulate sticky performance
    progress.max_wrongs = (progress.max_wrongs || 0) + (wrongs || 0);
    progress.max_time = Math.max(progress.max_time || 0, timeSec || 0);
    if (gave_up) progress.gave_up = true;
    progress.reveal_count = (progress.reveal_count || 0) + (reveal_count || 0);
    
    if (gate === 'dictation') progress.todayDictationPassed = true;
    if (gate === 'flashcard') progress.todayFlashcardPassed = true;

    // Check if Dual-Gate is complete
    if (progress.todayDictationPassed && progress.todayFlashcardPassed) {
        const rating = calculateFSRSRating(progress.max_wrongs, progress.max_time, !!progress.gave_up, progress.reveal_count);
        
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

        // Cap first review interval to 1 day
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
        await db.fsrs_progress.put(progress);
        
        syncOfflineProgress().catch(console.error);

        return {
            rating,
            nextDue: newCardState.due,
            completed: true
        };
    } else {
        progress.synced = false;
        await db.fsrs_progress.put(progress);
        return { completed: false };
    }
}
