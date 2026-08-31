export const onRequest: PagesFunction = async (context) => {
  const url = new URL(context.request.url);
  const text = url.searchParams.get('text') || '';
  if (!text) {
    return new Response('Missing text', { status: 400 });
  }

  const googleTtsUrl = 'https://translate.google.com/translate_tts?ie=UTF-8&tl=sv&client=tw-ob&q=' + encodeURIComponent(text);
  
  try {
    const response = await fetch(googleTtsUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });

    if (!response.ok) {
      return new Response('TTS upstream error: ' + response.statusText, { status: response.status });
    }

    const headers = new Headers();
    headers.set('Content-Type', 'audio/mpeg');
    headers.set('Access-Control-Allow-Origin', '*');
    headers.set('Cache-Control', 'public, max-age=86400');

    return new Response(response.body, {
      status: 200,
      headers
    });
  } catch (err: any) {
    return new Response('TTS fetch failed: ' + err.message, { status: 500 });
  }
};
