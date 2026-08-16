import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables from .env.local
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

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

// Configure Supabase client
// Using Service Role Key to bypass Row Level Security for admin data seeding
const supabaseUrl = process.env.VITE_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_API_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * Uploads a local file to Cloudflare R2 bucket.
 */
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

async function getCourseData(legacyPath: string) {
  const jsPath = path.join(legacyPath, 'data.js');

  if (fs.existsSync(jsPath)) {
    let jsContent = fs.readFileSync(jsPath, 'utf8');
    jsContent = jsContent.replace('const APP_DATA = ', '').trim();
    if (jsContent.endsWith(';')) jsContent = jsContent.slice(0, -1);
    return JSON.parse(jsContent);
  }
  
  throw new Error(`Course data file not found at ${legacyPath}`);
}

async function seed() {
  const legacyDir = path.resolve('../SFI/web_app');
  
  console.log('1. Reading legacy data...');
  const appData = await getCourseData(legacyDir);
  
  const tempJsonPath = path.join(process.cwd(), 'temp_data.json');
  fs.writeFileSync(tempJsonPath, JSON.stringify(appData, null, 2));
  
  console.log('2. Uploading data.json to R2...');
  await uploadFileToR2(tempJsonPath, 'data.json');
  fs.unlinkSync(tempJsonPath); // Cleanup

  console.log('3. Skipping MP3 upload (already uploaded to R2)...');
  // MP3 upload logic commented out to save time since it was successfully completed in Loop 1.

  console.log('4. Inserting course metadata into Supabase...');
  // Iterate through top-level keys in APP_DATA (e.g., 'c_niva')
  for (const [courseId, courseContent] of Object.entries(appData)) {
    const { error } = await supabase
      .from('courses')
      .upsert({
        id: courseId,
        title: courseId,
        description: 'Imported legacy course',
        r2_json_url: 'data.json',
        created_at: new Date().toISOString()
      }, { onConflict: 'id' });

    if (error) {
      console.error(`Failed to insert course ${courseId}:`, error);
    } else {
      console.log(`Successfully inserted course ${courseId} into Supabase DB`);
    }
  }

  console.log('=== Seeding completed successfully! ===');
}

seed().catch(console.error);
