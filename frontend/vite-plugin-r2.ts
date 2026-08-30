import { S3Client, GetObjectCommand, ListObjectsV2Command } from '@aws-sdk/client-s3';
import { Readable } from 'stream';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: '.env.local' });

const s3 = new S3Client({
  region: 'auto',
  endpoint: process.env.R2_Endpoint_S3!,
  credentials: {
    accessKeyId: process.env.R2_AccessKeyID!,
    secretAccessKey: process.env.R2_SecretAccessKey!,
  },
});

// In-memory case-insensitive key index for words_audio
const wordAudioIndex = new Map<string, string>();
let isIndexLoaded = false;
let isIndexLoading = false;

const cleanKeyForLookup = (key: string) => {
  return key.toLowerCase().replace(/^(words_audio\/)/, '').replace(/\.mp3$/, '').replace(/[.!?,"']/g, '').trim();
};

const ensureIndexLoaded = async () => {
  if (isIndexLoaded || isIndexLoading) return;
  isIndexLoading = true;
  try {
    let isTruncated = true;
    let continuationToken: string | undefined = undefined;
    while (isTruncated) {
      const res: any = await s3.send(new ListObjectsV2Command({
        Bucket: process.env.R2_BUCKET_NAME || 'language-learner-courses',
        Prefix: 'words_audio/',
        ContinuationToken: continuationToken
      }));
      for (const item of (res.Contents || [])) {
        if (item.Key) {
          const clean = cleanKeyForLookup(item.Key);
          if (!wordAudioIndex.has(clean)) {
            wordAudioIndex.set(clean, item.Key);
          }
        }
      }
      isTruncated = res.IsTruncated || false;
      continuationToken = res.NextContinuationToken;
    }
    isIndexLoaded = true;
  } catch (e) {
    console.error('Failed to pre-index words_audio keys:', e);
  } finally {
    isIndexLoading = false;
  }
};

// Start background load immediately
ensureIndexLoaded();

export default function r2ProxyPlugin() {
  return {
    name: 'r2-proxy',
    configureServer(server: any) {
      server.middlewares.use(async (req: any, res: any, next: any) => {
        if (req.url?.startsWith('/api/r2/')) {
          try {
            // 1. Extract and sanitize key
            let rawKey = req.url.replace('/api/r2/', '').split('?')[0];
            let decodedKey = decodeURIComponent(rawKey);
            
            // Normalize path to prevent directory traversal attacks (e.g. ../../)
            let normalizedKey = path.normalize(decodedKey).replace(/^(\.\.[\/\\])+/, '');
            
            // 2. Reject explicitly malicious path traversal attempts
            if (decodedKey.includes('..')) {
              res.statusCode = 403;
              return res.end('Forbidden: Invalid Path');
            }

            let keyToFetch = normalizedKey;

            // If words_audio request, check if we need smart case/punctuation resolution
            if (normalizedKey.startsWith('words_audio/')) {
              await ensureIndexLoaded();
              const clean = cleanKeyForLookup(normalizedKey);
              const indexedKey = wordAudioIndex.get(clean);
              if (indexedKey) {
                keyToFetch = indexedKey;
              }
            }

            const command = new GetObjectCommand({
              Bucket: process.env.R2_BUCKET_NAME || 'language-learner-courses',
              Key: keyToFetch,
            });
            
            const response = await s3.send(command);
            
            // 3. Set proper headers for audio streaming
            const contentType = response.ContentType || (normalizedKey.endsWith('.mp3') ? 'audio/mpeg' : 'application/octet-stream');
            res.setHeader('Content-Type', contentType);
            res.setHeader('Cache-Control', 'public, max-age=31536000');
            res.setHeader('Accept-Ranges', 'bytes');
            if (response.ContentLength) {
              res.setHeader('Content-Length', response.ContentLength);
            }
            
            // 4. Stream with robust error and termination handling
            if (response.Body instanceof Readable) {
              const stream = response.Body;
              
              req.on('close', () => {
                if (!res.writableEnded) {
                  stream.destroy();
                }
              });

              stream.on('error', (streamErr) => {
                console.error('R2 Stream Error:', streamErr);
                if (!res.headersSent) {
                  res.statusCode = 500;
                  res.end('Stream Error');
                }
              });

              stream.pipe(res);
            } else {
              res.end(response.Body);
            }
          } catch (err: any) {
            if (err.name === 'NoSuchKey' || err.$metadata?.httpStatusCode === 404) {
              res.statusCode = 404;
              res.end('Not Found');
            } else {
              console.error('R2 Proxy Internal Error:', err.message);
              res.statusCode = 500;
              res.end('Internal Server Error');
            }
          }
        } else if (req.url?.startsWith('/api/apple-tts')) {
          try {
            const parsed = new URL(req.url, 'http://localhost:5173');
            const text = parsed.searchParams.get('text') || '';
            const voiceParam = parsed.searchParams.get('voice') || 'Alva (Premium)';
            if (!text) {
              res.statusCode = 400;
              return res.end('Missing text parameter');
            }

            const { exec } = await import('child_process');
            const fs = await import('fs');
            const os = await import('os');

            const tmpAiff = path.join(os.tmpdir(), `alva_${Date.now()}_${Math.random().toString(36).slice(2)}.aiff`);
            const tmpWav = path.join(os.tmpdir(), `alva_${Date.now()}_${Math.random().toString(36).slice(2)}.wav`);

            const safeVoice = voiceParam.includes('Premium') ? 'Alva (Premium)' : 'Alva';
            const safeText = text.replace(/["\\]/g, '\\$&');

            exec(`say -v "${safeVoice}" -o "${tmpAiff}" "${safeText}" && afconvert -f WAVE -d LEI16 "${tmpAiff}" "${tmpWav}"`, (err) => {
              try {
                if (err || !fs.existsSync(tmpWav)) {
                  // If Alva (Premium) failed, fallback to standard Alva
                  exec(`say -v "Alva" -o "${tmpAiff}" "${safeText}" && afconvert -f WAVE -d LEI16 "${tmpAiff}" "${tmpWav}"`, (err2) => {
                    if (err2 || !fs.existsSync(tmpWav)) {
                      res.statusCode = 500;
                      return res.end('Apple TTS Error');
                    }
                    const data = fs.readFileSync(tmpWav);
                    try { fs.unlinkSync(tmpAiff); fs.unlinkSync(tmpWav); } catch {}
                    res.setHeader('Content-Type', 'audio/wav');
                    res.setHeader('Cache-Control', 'public, max-age=86400');
                    return res.end(data);
                  });
                  return;
                }

                const data = fs.readFileSync(tmpWav);
                try { fs.unlinkSync(tmpAiff); fs.unlinkSync(tmpWav); } catch {}
                res.setHeader('Content-Type', 'audio/wav');
                res.setHeader('Cache-Control', 'public, max-age=86400');
                return res.end(data);
              } catch (e: any) {
                res.statusCode = 500;
                res.end('Error');
              }
            });
          } catch (e: any) {
            res.statusCode = 500;
            res.end('Error');
          }
        } else if (req.url?.startsWith('/api/tts')) {
          try {
            const parsed = new URL(req.url, 'http://localhost:5173');
            const text = parsed.searchParams.get('text') || '';
            if (!text) {
              res.statusCode = 400;
              return res.end('Missing text parameter');
            }

            const ttsUrl = 'https://translate.google.com/translate_tts?ie=UTF-8&tl=sv&client=tw-ob&q=' + encodeURIComponent(text);
            const https = await import('https');
            const proxyReq = https.get(ttsUrl, {
              rejectUnauthorized: false,
              headers: {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
              }
            }, (proxyRes) => {
              res.setHeader('Content-Type', 'audio/mpeg');
              res.setHeader('Cache-Control', 'public, max-age=86400');
              proxyRes.pipe(res);
            });

            proxyReq.on('error', (err) => {
              console.error('TTS Proxy Error:', err.message);
              res.statusCode = 500;
              res.end('TTS Proxy Error');
            });
          } catch (e: any) {
            res.statusCode = 500;
            res.end('TTS Error');
          }
        } else {
          next();
        }
      });
    },
  };
}
