/**
 * Service worker da Aprende Brasil.
 *
 * Princípios:
 * - **Versionado**: mudar `VERSION` invalida os caches antigos na ativação.
 * - **Sem travar atualização**: a nova versão não assume no meio de uma lição;
 *   ela avisa a página e a pessoa decide recarregar (`SKIP_WAITING`).
 * - **Nada de cache de API autenticada**: requisições com `Authorization` ou
 *   para `/api/` nunca vão para o cache. Progresso sensível não fica em disco
 *   do service worker.
 * - **Offline útil**: o catálogo e as etapas (JSON empacotados no bundle) já
 *   estão no cache de assets; a última página visitada abre mesmo sem rede.
 */

const VERSION = "v3";
const SHELL_CACHE = `aprende-shell-${VERSION}`;
const ASSET_CACHE = `aprende-assets-${VERSION}`;
const DATA_CACHE = `aprende-data-${VERSION}`;

// Relativo à raiz do registro: funciona em "/" e em "/aprende-brasil/".
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./favicon.svg"];

self.addEventListener("install", event => {
  event.waitUntil(
    caches
      .open(SHELL_CACHE)
      .then(cache => cache.addAll(SHELL))
      .catch(() => {
        /* se a pré-carga falhar, o runtime cache resolve depois */
      })
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter(key => !key.endsWith(VERSION))
          .map(key => caches.delete(key))
      );
      await self.clients.claim();
    })()
  );
});

self.addEventListener("message", event => {
  if (event.data === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

function isApiRequest(url) {
  return url.pathname.includes("/api/");
}

async function networkFirst(request) {
  const cache = await caches.open(SHELL_CACHE);
  try {
    const response = await fetch(request);
    if (response && response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await cache.match(request);
    if (cached) return cached;
    // Última tentativa: a raiz do app serve o SPA offline.
    const shell = await cache.match("./index.html");
    if (shell) return shell;
    throw error;
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(ASSET_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response && response.ok) {
    cache.put(request, response.clone());
  }
  return response;
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(DATA_CACHE);
  const cached = await cache.match(request);
  const fetched = fetch(request)
    .then(response => {
      if (response && response.ok) cache.put(request, response.clone());
      return response;
    })
    .catch(() => cached);
  return cached || fetched;
}

self.addEventListener("fetch", event => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);

  // Nunca cacheia dados de sessão/API, nem requisições autenticadas.
  if (
    url.origin !== self.location.origin ||
    isApiRequest(url) ||
    request.headers.has("authorization")
  ) {
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(networkFirst(request));
    return;
  }

  if (url.pathname.includes("/assets/")) {
    event.respondWith(cacheFirst(request));
    return;
  }

  if (url.pathname.includes("/open-data/")) {
    event.respondWith(staleWhileRevalidate(request));
  }
});
