import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from frontend/.env.local
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

async function uploadFileToR2(content: string, bucketKey: string) {
  const command = new PutObjectCommand({
    Bucket: BUCKET_NAME,
    Key: bucketKey,
    Body: content,
    ContentType: 'application/json',
  });

  try {
    await s3.send(command);
    console.log(`Successfully uploaded: ${bucketKey}`);
  } catch (err) {
    console.error(`Error uploading ${bucketKey}:`, err);
  }
}

async function getCourseData() {
  const jsPath = '../SFI/web_app/data.js';
  if (fs.existsSync(jsPath)) {
    let jsContent = fs.readFileSync(jsPath, 'utf8');
    jsContent = jsContent.replace('const APP_DATA = ', '').trim();
    if (jsContent.endsWith(';')) jsContent = jsContent.slice(0, -1);
    return JSON.parse(jsContent);
  }
  throw new Error(`Course data file not found at ${jsPath}`);
}

async function seed() {
  console.log('1. Reading legacy data.js...');
  const appData = await getCourseData();
  
  // sfid
  if (appData['sfid']) {
    console.log('2. Uploading sfid_data.json to R2...');
    await uploadFileToR2(JSON.stringify(appData['sfid'], null, 2), 'courses/sfid/sfid_data.json');
    
    console.log('Inserting SFI D into Supabase...');
    const { error } = await supabase.from('courses').upsert({
      id: 'sfid',
      title: 'SFI D',
      description: 'SFI Level D Swedish Course',
      r2_base_url: 'courses/sfid/',
      r2_json_url: 'courses/sfid/sfid_data.json',
      created_at: new Date().toISOString()
    }, { onConflict: 'id' });
    if (error) console.error(error);
  }

  // c_niva (Nivatest)
  let nivaData = appData['c_niva'];
  const nivaSentencesPath = '../SFI/courses/Nivatest/source_data/sentences.json';
  if (fs.existsSync(nivaSentencesPath) && !nivaData) {
    nivaData = JSON.parse(fs.readFileSync(nivaSentencesPath, 'utf8'));
  }

  if (nivaData) {
    console.log('3. Uploading niva_data.json to R2...');
    await uploadFileToR2(JSON.stringify(nivaData, null, 2), 'courses/c_niva/niva_data.json');
    
    console.log('Inserting SFI C into Supabase...');
    const { error } = await supabase.from('courses').upsert({
      id: 'c_niva',
      title: 'SFI C',
      description: 'SFI Level C Swedish Course',
      r2_base_url: 'courses/c_niva/',
      r2_json_url: 'courses/c_niva/niva_data.json',
      created_at: new Date().toISOString()
    }, { onConflict: 'id' });
    if (error) console.error(error);
  }
  
  console.log('=== Seeding completed successfully! ===');
}

seed().catch(console.error);
