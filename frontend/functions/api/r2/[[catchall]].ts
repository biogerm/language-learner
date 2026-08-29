export async function onRequest(context: { request: Request; params: { catchall?: string | string[] } }) {
  const url = new URL(context.request.url);
  const subPath = url.pathname.replace(/^\/api\/r2\/?/, '');
  const targetUrl = `https://cdn.languagelearner.se/${subPath}${url.search}`;

  const response = await fetch(targetUrl, {
    method: context.request.method,
  });

  const newHeaders = new Headers(response.headers);
  newHeaders.set('Access-Control-Allow-Origin', '*');

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders,
  });
}
