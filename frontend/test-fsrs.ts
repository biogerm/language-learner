import "fake-indexeddb/auto";
import { submitGatePass } from "./src/utils/fsrs.ts";
import { db } from "./src/db/dexie.ts";

async function testFSRS() {
  console.log("Testing FSRS logic...");

  const wordId = "mock-word-123";
  
  console.log(`Submitting gate pass for ${wordId} (Rating Good: 1 wrong, 10s, false, 0 reveals)...`);
  // max_wrongs: 1, max_time: 10, gave_up: false, reveal_count: 0 -> should evaluate to Good or Easy. 
  // Let's pass: 2 reveals for 'Good', or 1 wrong 16s for Good. 
  // Wait, the logic for Good is:
  // if (reveals === 2) return Rating.Good;
  const result = await submitGatePass(wordId, 0, 10, false, 2);

  console.log(`Rating computed: ${result.rating}`);
  console.log(`Next due returned: ${result.nextDue}`);

  const record = await db.fsrs_progress.get(wordId);
  if (!record) {
    console.error("Dexie record not found!");
    process.exit(1);
  }

  console.log(`Dexie recorded due date: ${record.due}`);
  
  if (record.due.getTime() > Date.now()) {
    console.log("Success: Next due date > current time.");
  } else {
    console.error("Fail: Next due date is not in the future.");
    process.exit(1);
  }
}

testFSRS();
