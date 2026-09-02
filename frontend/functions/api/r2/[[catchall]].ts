export async function onRequest(context: { request: Request; params: { catchall?: string | string[] } }) {
  const url = new URL(context.request.url);
  const subPath = url.pathname.replace(/^\/api\/r2\/?/, '');
  const targetUrl = `https://cdn.languagelearner.se/${subPath}${url.search}`;

  let response = await fetch(targetUrl, {
    method: context.request.method,
  });

  // Fallback for audio casing mismatch (e.g. lowercase to Capitalized)
  if (response.status === 404 && subPath.startsWith('words_audio/')) {
    const filename = subPath.replace(/^words_audio\//, '');
    const decoded = decodeURIComponent(filename);
    const capitalized = decoded.charAt(0).toUpperCase() + decoded.slice(1);
    if (capitalized !== decoded) {
      const fallbackUrl = `https://cdn.languagelearner.se/words_audio/${encodeURIComponent(capitalized)}${url.search}`;
      const fallbackResp = await fetch(fallbackUrl, { method: context.request.method });
      if (fallbackResp.ok) response = fallbackResp;
    }
  }

  const newHeaders = new Headers(response.headers);
  newHeaders.set('Access-Control-Allow-Origin', '*');

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders,
  });
}
