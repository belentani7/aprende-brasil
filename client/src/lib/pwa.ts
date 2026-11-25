/**
 * Registro do service worker com aviso explícito de atualização.
 *
 * Regras aprendidas na prática:
 * - Nunca chamar `skipWaiting()` automaticamente: a pessoa pode estar no meio
 *   de uma atividade. O aviso aparece e ela escolhe recarregar.
 * - Verificar atualização ao voltar para a aba e de hora em hora, para não
 *   ficar preso a uma versão antiga por dias.
 * - Em navegador sem suporte (ou em http sem SSL), falhar em silêncio: o app
 *   continua funcionando, só não fica instalável.
 */

export type PwaUpdate = {
  ready: boolean;
  updateAvailable: boolean;
  applyUpdate: () => void;
  offlineReady: boolean;
};

const listeners = new Set<(state: PwaUpdate) => void>();

let state: PwaUpdate = {
  ready: false,
  updateAvailable: false,
  applyUpdate: () => {},
  offlineReady: false,
};

function emit(patch: Partial<PwaUpdate>) {
  state = { ...state, ...patch };
  for (const listener of listeners) listener(state);
}

export function subscribePwa(listener: (next: PwaUpdate) => void): () => void {
  listeners.add(listener);
  listener(state);
  return () => listeners.delete(listener);
}

export function registerServiceWorker(): void {
  if (typeof window === "undefined") return;
  if (!("serviceWorker" in navigator)) return;
  if (import.meta.env.DEV) return;
  // Base do Vite: "" ou "/aprende-brasil/"
  const base = import.meta.env.BASE_URL || "/";
  const url = `${base}sw.js`;

  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register(url, { scope: base })
      .then(registration => {
        emit({ ready: true });

        const promptUpdate = () => {
          const waiting = registration.waiting;
          if (!waiting) return;
          emit({
            updateAvailable: true,
            applyUpdate: () => {
              waiting.postMessage("SKIP_WAITING");
              window.location.reload();
            },
          });
        };

        if (registration.waiting) promptUpdate();

        registration.addEventListener("updatefound", () => {
          const installing = registration.installing;
          if (!installing) return;
          installing.addEventListener("statechange", () => {
            if (
              installing.state === "installed" &&
              navigator.serviceWorker.controller
            ) {
              promptUpdate();
            } else if (installing.state === "activated") {
              emit({ offlineReady: true });
            }
          });
        });

        const check = () => void registration.update().catch(() => {});
        document.addEventListener("visibilitychange", () => {
          if (document.visibilityState === "visible") check();
        });
        window.setInterval(check, 60 * 60 * 1000);
      })
      .catch(() => {
        /* sem service worker: app segue funcionando online */
      });
  });
}
