import { supabase } from './supabase';

/**
 * Returns the public URL for an MP3 file stored in R2.
 * @param filename - The name of the file
 * @returns The full public URL
 */
export const getMp3PublicUrl = (filename: string): string => {
  const path = filename.startsWith('/') ? filename : `/${filename}`;
  return `/api/r2${path}`;
};

/**
 * Fetches a presigned URL for uploading a file to R2 via Supabase Edge Functions.
 * Assuming a backend endpoint or Supabase function handles the secure AWS S3 client generation.
 * @param filename - The target filename
 * @param contentType - The MIME type of the file
 * @returns The presigned URL
 */
export const fetchR2PresignedUrl = async (filename: string, contentType: string): Promise<string> => {
  // We use Supabase Edge Functions to securely get a presigned URL since it's a frontend app
  const { data, error } = await supabase.functions.invoke('get-presigned-url', {
    body: { filename, contentType },
  });

  if (error) {
    console.error('Error fetching presigned URL:', error.message);
    throw new Error('Failed to fetch presigned URL');
  }

  return data.url;
};

/**
 * Uploads a file directly to R2 using a generated presigned URL.
 * @param file - The file object to upload
 * @param presignedUrl - The presigned URL obtained from `fetchR2PresignedUrl`
 */
export const uploadFileToR2 = async (file: File, presignedUrl: string): Promise<void> => {
  const response = await fetch(presignedUrl, {
    method: 'PUT',
    body: file,
    headers: {
      'Content-Type': file.type,
    },
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }
};

export const fetchCourseData = async (r2_json_url: string) => {
  const url = getMp3PublicUrl(r2_json_url);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch course data from ${r2_json_url}`);
  return res.json();
};
