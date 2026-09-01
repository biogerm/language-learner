const { S3Client, ListObjectsV2Command } = require('@aws-sdk/client-s3');
require('dotenv').config({ path: '.env.local' });

const s3 = new S3Client({
  region: 'auto',
  endpoint: process.env.R2_Endpoint_S3,
  credentials: {
    accessKeyId: process.env.R2_AccessKeyID,
    secretAccessKey: process.env.R2_SecretAccessKey,
  }
});

async function run() {
  const res = await s3.send(new ListObjectsV2Command({
    Bucket: 'language-learner-courses',
    Prefix: 'words_audio/k',
  }));
  const keys = (res.Contents || []).map(c => c.Key).filter(k => k.includes('nd.mp3') || k.includes('nda.mp3'));
  for (const k of keys) {
      console.log(k, Buffer.from(k).toString('hex'));
      console.log('NFC:', k.normalize('NFC'), Buffer.from(k.normalize('NFC')).toString('hex'));
      console.log('NFD:', k.normalize('NFD'), Buffer.from(k.normalize('NFD')).toString('hex'));
  }
}
run().catch(console.error);
