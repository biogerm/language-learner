import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';
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

            const command = new GetObjectCommand({
              Bucket: process.env.R2_BUCKET_NAME || 'language-learner-courses',
              Key: normalizedKey,
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
        } else {
          next();
        }
      });
    },
  };
}
