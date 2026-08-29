import 'fake-indexeddb/auto';
import { db } from '../src/db/dexie';
import { resolveWordMetadata, buildStudyQueue } from '../src/utils/queueBuilder';

async function runTest() {
  console.log('--- 1. TEST DYNAMIC SENTENCE FETCH ---');
  
  // Seed mock course_data
  await db.course_data.put({
    courseId: 'sfid',
    dictionary: [
      { base_form: 'hej', word_in_sentence: 'hej', sentence_id: 'art_1_s001' },
      { base_form: 'tack', word_in_sentence: 'tack', sentence_id: 'art_1_s002' }
    ],
    articles: {
      stages: [
        {
          stage_id: 'stage_1',
          articles: [
            {
              article_id: 'art_1',
              sentences: [
                { sentence_id: 'art_1_s001', sv: 'Hej världen!', en: 'Hello world!' },
                { sentence_id: 'art_1_s002', sv: 'Tack så mycket!', en: 'Thank you very much!' }
              ]
            }
          ]
        }
      ]
    }
  });

  // Seed custom_dictionary without literal sentence string, only sentence_id and course_id
  await db.custom_dictionary.clear();
  await db.custom_dictionary.add({
    base_form: 'världen',
    word_in_sentence: 'världen',
    en_translation: 'the world',
    contextual_en: 'world',
    stage_id: 'stage_1',
    article_id: 'art_1',
    sentence_id: 'art_1_s001',
    course_id: 'sfid'
  });

  // Test System Word
  const resSystem = await resolveWordMetadata('hej', {}, 'sfid');
  console.log('System word resolved sentence:', resSystem.sentence);
  if (resSystem.sentence !== 'Hej världen!') {
    throw new Error(`Expected "Hej världen!", got "${resSystem.sentence}"`);
  }

  // Test Custom Word
  const resCustom = await resolveWordMetadata('världen', {}, 'sfid');
  console.log('Custom word resolved sentence:', resCustom.sentence);
  if (resCustom.sentence !== 'Hej världen!') {
    throw new Error(`Expected "Hej världen!", got "${resCustom.sentence}"`);
  }

  console.log('✅ TEST 1 PASSED: Dynamic sentence fetch works for both system & custom words!\n');

  console.log('--- 2. TEST STUDY QUEUE FSRS FILTERING ---');
  await db.learning_queue.clear();
  await db.learning_queue.bulkAdd([
    {
      article_id: 'art_1',
      base_form: 'hej',
      word_in_sentence: 'hej',
      en_translation: 'hello',
      contextual_en: '',
      stage_id: 'stage_1',
      sentence_id: 'art_1_s001',
      dictation_passed: false,
      flashcard_passed: false
    },
    {
      article_id: 'art_1',
      base_form: 'tack',
      word_in_sentence: 'tack',
      en_translation: 'thanks',
      contextual_en: '',
      stage_id: 'stage_1',
      sentence_id: 'art_1_s002',
      dictation_passed: false,
      flashcard_passed: false
    }
  ]);

  // Seed FSRS: mark 'hej' as active (state: 1)
  await db.fsrs_progress.clear();
  await db.fsrs_progress.put({
    word_id: 'hej',
    course_id: 'sfid',
    state: 1,
    due: new Date(),
    stability: 2,
    difficulty: 5,
    elapsed_days: 0,
    scheduled_days: 1,
    reps: 1,
    lapses: 0,
    last_review: new Date()
  });

  const studyStats = await buildStudyQueue('study', 'sfid', 'art_1', 'dictation');
  console.log('Study queue result:', {
    total: studyStats.total,
    remaining: studyStats.remaining,
    inFsrsCount: studyStats.inFsrsCount,
    queueWords: studyStats.queue.map(q => q.base_form)
  });

  if (studyStats.inFsrsCount !== 1) {
    throw new Error(`Expected inFsrsCount to be 1, got ${studyStats.inFsrsCount}`);
  }
  if (studyStats.queue.some(q => q.base_form === 'hej')) {
    throw new Error('Word "hej" should have been filtered out of study queue!');
  }
  if (studyStats.queue.length !== 1 || studyStats.queue[0].base_form !== 'tack') {
    throw new Error('Only "tack" should remain in the study queue!');
  }

  console.log('✅ TEST 2 PASSED: Study queue successfully filters out words in FSRS review!\n');
}

runTest().catch(err => {
  console.error('❌ TEST FAILED:', err);
  process.exit(1);
});
