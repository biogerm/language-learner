import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

const s3 = new S3Client({
  region: 'auto',
  endpoint: process.env.R2_Endpoint_S3!,
  credentials: {
    accessKeyId: process.env.R2_AccessKeyID!,
    secretAccessKey: process.env.R2_SecretAccessKey!,
  },
});

const BUCKET_NAME = process.env.R2_BUCKET_NAME || 'language-learner-courses';

async function uploadFileToR2(filePath: string, bucketKey: string) {
  const content = fs.readFileSync(filePath);
  const command = new PutObjectCommand({
    Bucket: BUCKET_NAME,
    Key: bucketKey,
    Body: content,
    ContentType: 'audio/mpeg',
  });

  try {
    await s3.send(command);
    console.log(`✅ Uploaded: ${bucketKey}`);
  } catch (err) {
    console.error(`❌ Error uploading ${bucketKey}:`, err);
  }
}

function getFilesRecursively(directory: string): string[] {
  let files: string[] = [];
  if (!fs.existsSync(directory)) return files;
  const items = fs.readdirSync(directory, { withFileTypes: true });
  for (const item of items) {
    const fullPath = path.join(directory, item.name);
    if (item.isDirectory()) {
      files = files.concat(getFilesRecursively(fullPath));
    } else if (item.isFile() && item.name.endsWith('.mp3')) {
      files.push(fullPath);
    }
  }
  return files;
}

async function uploadDirectory(baseDir: string, r2Prefix: string) {
  const files = getFilesRecursively(baseDir);
  console.log(`Found ${files.length} MP3 files in ${baseDir}. Starting upload...`);
  
  // We can upload in batches to avoid overwhelming the network
  const BATCH_SIZE = 50;
  for (let i = 0; i < files.length; i += BATCH_SIZE) {
    const batch = files.slice(i, i + BATCH_SIZE);
    await Promise.all(batch.map(async (file) => {
      // Keep the relative path inside the directory
      const relativePath = path.relative(baseDir, file);
      // Construct the key like audio/words_audio/abc.mp3
      const key = `${r2Prefix}/${relativePath.replace(/\\/g, '/')}`;
      await uploadFileToR2(file, key);
    }));
  }
}

async function main() {
  const legacyAudioBase = '../SFI/web_app/audio';
  
  const wordsAudioDir = path.join(legacyAudioBase, 'words_audio');
  const sentencesAudioDir = path.join(legacyAudioBase, 'sentences_audio');

  console.log('Uploading words_audio...');
  await uploadDirectory(wordsAudioDir, 'words_audio');

  console.log('Uploading sentences_audio...');
  await uploadDirectory(sentencesAudioDir, 'sentences_audio');

  console.log('🎉 All audio files uploaded to R2!');
}

main().catch(console.error);
