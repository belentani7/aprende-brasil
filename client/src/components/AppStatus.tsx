import { useEffect, useState } from "react";
import { RefreshCw, WifiOff, X } from "lucide-react";
import { subscribePwa, type PwaUpdate } from "@/lib/pwa";

/**
 * Faixa de estado do app: sem conexão e atualização disponível.
 *
 * Fica fora do fluxo de leitura (no topo, discreta) e usa `aria-live` para que
 * leitores de tela anunciem a mudança sem interromper o parágrafo em foco.
 */
export default function AppStatus() {
  const [online, setOnline] = useState(
    typeof navigator === "undefined" ? true : navigator.onLine
  );
  const [pwa, setPwa] = useState<PwaUpdate | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const goOnline = () => setOnline(true);
    const goOffline = () => setOnline(false);
    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);
    return () => {
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
    };
  }, []);

  useEffect(() => subscribePwa(setPwa), []);

  const showOffline = !online;
  const showUpdate = Boolean(pwa?.updateAvailable) && !dismissed;

  if (!showOffline && !showUpdate) return null;

  return (
    <div className="app-status" role="status" aria-live="polite">
      {showOffline && (
        <p className="app-status__item app-status__item--offline">
          <WifiOff size={14} aria-hidden="true" />
          Você está sem conexão. O conteúdo já aberto continua funcionando e o
          progresso fica salvo neste aparelho.
        </p>
      )}
      {showUpdate && pwa && (
        <div className="app-status__item app-status__item--update">
          <span>
            <RefreshCw size={14} aria-hidden="true" /> Há uma versão nova do
            aplicativo.
          </span>
          <button
            type="button"
            className="app-status__action"
            onClick={pwa.applyUpdate}
          >
            Atualizar agora
          </button>
          <button
            type="button"
            className="app-status__dismiss"
            onClick={() => setDismissed(true)}
            aria-label="Continuar na versão atual"
          >
            <X size={14} aria-hidden="true" />
          </button>
        </div>
      )}
    </div>
  );
}
