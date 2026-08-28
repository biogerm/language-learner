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
  const fileContent = fs.readFileSync(filePath);
  const command = new PutObjectCommand({
    Bucket: BUCKET_NAME,
    Key: bucketKey,
    Body: fileContent,
    ContentType: 'application/json',
  });

  await s3.send(command);
  console.log(`Successfully uploaded: ${bucketKey}`);
}

async function run() {
  await uploadFileToR2(
    path.resolve(__dirname, '../public/courses/sfid/course_sfid_articles.json'), 
    'courses/sfid/course_sfid_articles.json'
  );
  await uploadFileToR2(
    path.resolve(__dirname, '../public/courses/sfid/course_sfid_vocab.json'), 
    'courses/sfid/course_sfid_vocab.json'
  );
}
run();
