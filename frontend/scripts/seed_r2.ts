import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

// Configure AWS S3 Client for Cloudflare R2
const s3 = new S3Client({
  region: 'auto',
  endpoint: process.env.R2_Endpoint_S3!,
  credentials: {
    accessKeyId: process.env.R2_AccessKeyID!,
    secretAccessKey: process.env.R2_SecretAccessKey!,
  },
});

const BUCKET_NAME = process.env.R2_BUCKET_NAME || 'language-learner-courses';

const supabaseUrl = process.env.VITE_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_API_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function uploadFileToR2(filePath: string, bucketKey: string) {
  if (!fs.existsSync(filePath)) {
    console.warn(`File not found, skipping: ${filePath}`);
    return;
  }
  
  const fileContent = fs.readFileSync(filePath);
  let mimeType = 'application/octet-stream';
  if (filePath.endsWith('.mp3')) mimeType = 'audio/mpeg';
  if (filePath.endsWith('.json')) mimeType = 'application/json';

  const command = new PutObjectCommand({
    Bucket: BUCKET_NAME,
    Key: bucketKey,
    Body: fileContent,
    ContentType: mimeType,
  });

  try {
    await s3.send(command);
    console.log(`Successfully uploaded: ${bucketKey}`);
  } catch (err) {
    console.error(`Error uploading ${bucketKey}:`, err);
  }
}

async function seed() {
  const courseId = 'sfid';
  const baseDir = path.resolve(__dirname, '../../course', courseId);
  
  console.log('1. Uploading master_dictionary.json to R2...');
  const masterDictPath = path.join(baseDir, 'phase1/master_dictionary.json');
  await uploadFileToR2(masterDictPath, `courses/${courseId}/data/master_dictionary.json`);
  
  console.log('2. Uploading translated articles to R2...');
  const articlesDir = path.join(baseDir, 'phase2/articles_translated');
  if (fs.existsSync(articlesDir)) {
    const files = fs.readdirSync(articlesDir).filter(f => f.endsWith('.json'));
    for (const file of files) {
      const filePath = path.join(articlesDir, file);
      await uploadFileToR2(filePath, `courses/${courseId}/data/articles/${file}`);
    }
  }

  console.log('3. Uploading audio files to R2...');
  const audioSentencesDir = path.join(baseDir, 'phase4/output/sentences_audio');
  if (fs.existsSync(audioSentencesDir)) {
    const files = fs.readdirSync(audioSentencesDir).filter(f => f.endsWith('.mp3'));
    for (const file of files) {
      await uploadFileToR2(path.join(audioSentencesDir, file), `courses/${courseId}/audio/sentences/${file}`);
    }
  }
  const audioWordsDir = path.join(baseDir, 'phase4/output/words_audio');
  if (fs.existsSync(audioWordsDir)) {
    const files = fs.readdirSync(audioWordsDir).filter(f => f.endsWith('.mp3'));
    for (const file of files) {
      await uploadFileToR2(path.join(audioWordsDir, file), `courses/${courseId}/audio/words/${file}`);
    }
  }

  console.log('4. Inserting course metadata into Supabase...');
  const { error } = await supabase
    .from('courses')
    .upsert({
      id: courseId,
      title: 'SFI D',
      description: 'SFI Level D Swedish Course',
      r2_base_url: `courses/${courseId}`,
      created_at: new Date().toISOString()
    }, { onConflict: 'id' });

  if (error) {
    console.error(`Failed to insert course ${courseId}:`, error);
  } else {
    console.log(`Successfully inserted course ${courseId} into Supabase DB`);
  }

  console.log('=== Seeding completed successfully! ===');
}

seed().catch(console.error);
