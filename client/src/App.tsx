import { lazy, Suspense } from "react";
import { Toaster } from "@/components/ui/sonner";
import { Route, Router as WouterRouter, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import Home from "./pages/Home";

// Rotas secundárias em chunks próprios: quem só abre o painel não baixa o
// código da leção, da página institucional nem do 404.
const Modulo = lazy(() => import("./pages/Modulo"));
const Sobre = lazy(() => import("./pages/Sobre"));
const NotFound = lazy(() => import("./pages/NotFound"));

function RouteFallback() {
  return (
    <div className="route-fallback" role="status" aria-live="polite">
      <span className="route-fallback-dot" aria-hidden="true" />
      Carregando…
    </div>
  );
}

function Routes() {
  return (
    <Suspense fallback={<RouteFallback />}>
      <Switch>
        <Route path="/" component={Home} />
        <Route path="/sobre" component={Sobre} />
        <Route path="/modulo/:id" component={Modulo} />
        <Route path="/404" component={NotFound} />
        <Route component={NotFound} />
      </Switch>
    </Suspense>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Toaster />
      {/* BASE_URL acompanha o --base do Vite: "" nos CDNs e
          "/aprende-brasil" no GitHub Pages, que serve em subpath.
          O trailing slash é removido: o wouter espera base sem ele. */}
      <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
        <Routes />
      </WouterRouter>
    </ErrorBoundary>
  );
}

export default App;
