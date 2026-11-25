import { createRoot } from "react-dom/client";
import App from "./App";
import { registerServiceWorker } from "./lib/pwa";
import "./index.css";

createRoot(document.getElementById("root")!).render(<App />);

// PWA: registro só em produção e com aviso de atualização, nunca em silêncio.
registerServiceWorker();
