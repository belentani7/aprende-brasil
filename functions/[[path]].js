// Cloudflare Pages Function — fallback SPA.
//
// O _redirects com catch-all tem prioridade sobre assets estáticos no Pages
// (chegava a servir /assets/*.js como text/html). Aqui os assets são servidos
// normalmente por context.next() e só um 404 real cai no index.html.

export async function onRequest(context) {
  const response = await context.next();

  if (response.status !== 404) {
    return response;
  }

  const url = new URL(context.request.url);
  url.pathname = "/index.html";
  url.search = "";

  const fallback = await context.env.ASSETS.fetch(url.toString());
  return new Response(fallback.body, {
    status: 200,
    headers: fallback.headers,
  });
}
