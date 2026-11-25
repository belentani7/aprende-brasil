import { useEffect, useRef, useState } from "react";
import { Link } from "wouter";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  Download,
  RotateCcw,
  Sparkles,
  Trash2,
  Upload,
} from "lucide-react";
import { api } from "@/lib/api";
import { findModule, trackLabel } from "@/lib/curriculum";
import {
  masteryOf,
  MASTERY_LABEL,
  dueModules,
  type ReviewMap,
} from "@/lib/srs";

type Summary = Awaited<ReturnType<typeof api.getSummary>>;

export default function Progresso() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [reviews, setReviews] = useState<ReviewMap>({});
  const [attempts, setAttempts] = useState<Awaited<
    ReturnType<typeof api.getAttempts>
  > | null>(null);
  const [busy, setBusy] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);

  const load = async () => {
    const [nextSummary, nextReviews, nextAttempts] = await Promise.all([
      api.getSummary(),
      api.getReviews(),
      api.getAttempts(),
    ]);
    setSummary(nextSummary);
    setReviews(nextReviews);
    setAttempts(nextAttempts);
  };

  useEffect(() => {
    void load();
    document.title = "Seu progresso · aprende. Brasil";
    return () => {
      document.title = "aprende. Brasil — educação aberta em pequenos passos";
    };
  }, []);

  useEffect(() => {
    headingRef.current?.focus();
  }, []);

  const exportFile = async () => {
    setBusy(true);
    try {
      const data = await api.exportData();
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const stamp = new Date().toISOString().slice(0, 10);
      link.href = url;
      link.download = `aprende-brasil-progresso-${stamp}.json`;
      link.click();
      URL.revokeObjectURL(url);
      toast.success("Arquivo de progresso gerado", {
        description:
          "Guarde o JSON: ele serve para restaurar em outro aparelho.",
      });
    } catch {
      toast.error("Não foi possível exportar agora.");
    } finally {
      setBusy(false);
    }
  };

  const importFile = async (file: File) => {
    setBusy(true);
    try {
      const text = await file.text();
      const payload: unknown = JSON.parse(text);
      const result = await api.importData(payload);
      if (!result.ok) {
        toast.error("Arquivo recusado", {
          description:
            "O formato não é de um progresso exportado por aqui, ou a versão é diferente.",
        });
        return;
      }
      await load();
      toast.success("Progresso restaurado", {
        description: `${result.modules} módulo(s) e ${result.favorites} favorito(s).${
          result.ignored.length
            ? ` ${result.ignored.length} item(ns) ignorado(s) por não existirem no currículo.`
            : ""
        }`,
      });
    } catch {
      toast.error("Arquivo ilegível", {
        description: "Verifique se é o JSON exportado por esta página.",
      });
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const reset = async () => {
    const confirmed = window.confirm(
      "Apagar todo o progresso guardado neste navegador? Isso não pode ser desfeito."
    );
    if (!confirmed) return;
    setBusy(true);
    try {
      await api.resetData();
      await load();
      toast("Progresso apagado neste navegador.");
    } finally {
      setBusy(false);
    }
  };

  const due = dueModules(reviews);
  const modulesWithAttempts = Array.from(
    new Set((attempts ?? []).map(a => a.moduleId))
  );

  return (
    <div className="modulo-page">
      <header className="modulo-topbar">
        <Link
          href="/"
          className="brand-lockup brand-lockup--inline"
          aria-label="aprende. Brasil — início"
        >
          <div className="brand-mark">
            <Sparkles size={19} fill="currentColor" aria-hidden="true" />
          </div>
          <div>
            <div className="brand-name">
              aprende<span>.</span>
            </div>
            <div className="brand-subtitle">Brasil</div>
          </div>
        </Link>
        <nav className="modulo-topbar-actions" aria-label="Navegação">
          <Link href="/" className="text-button">
            <ArrowLeft size={14} /> Catálogo
          </Link>
        </nav>
      </header>

      <main className="modulo-wrap">
        <header className="modulo-hero modulo-hero--green">
          <div className="modulo-hero-copy">
            <div className="eyebrow">
              <BarChart3 size={13} aria-hidden="true" /> Dados reais deste
              navegador
            </div>
            <h1 ref={headingRef} tabIndex={-1}>
              Seu progresso
            </h1>
            <p>
              Tudo aqui vem do que você fez — nada é estimado. O progresso fica
              só neste aparelho, sem conta e sem envio para servidor.
            </p>
          </div>
        </header>

        {summary && (
          <section
            className="progresso-grid"
            aria-label="Resumo do aprendizado"
          >
            <div className="progresso-card">
              <span className="progresso-label">Módulos iniciados</span>
              <strong>
                {summary.started}
                <span> / {summary.total_modules}</span>
              </strong>
            </div>
            <div className="progresso-card">
              <span className="progresso-label">Módulos concluídos</span>
              <strong>{summary.completed}</strong>
            </div>
            <div className="progresso-card">
              <span className="progresso-label">Atividades respondidas</span>
              <strong>{summary.activities_answered}</strong>
            </div>
            <div className="progresso-card">
              <span className="progresso-label">Acertos nas atividades</span>
              <strong>
                {summary.activities_accuracy === null
                  ? "—"
                  : `${summary.activities_accuracy}%`}
              </strong>
            </div>
            <div className="progresso-card">
              <span className="progresso-label">Revisões pendentes</span>
              <strong>{summary.reviews_due}</strong>
            </div>
            <div className="progresso-card">
              <span className="progresso-label">Favoritos</span>
              <strong>{summary.favorites}</strong>
            </div>
          </section>
        )}

        <p className="progresso-note">
          Concluir um módulo não significa domínio. A etiqueta de cada módulo
          mostra o que você já demonstrou nas atividades e nas revisões.
        </p>

        {due.length > 0 && (
          <section className="progresso-section" aria-labelledby="revisoes">
            <h2 id="revisoes">Para revisar</h2>
            <p>
              Estes módulos voltaram no seu calendário de revisão. Relembrar no
              momento certo vale mais que reler tudo de uma vez.
            </p>
            <ul className="progresso-list">
              {due.slice(0, 6).map(moduleId => {
                const module = findModule(moduleId);
                if (!module) return null;
                return (
                  <li key={moduleId}>
                    <Link href={`/modulo/${moduleId}`}>
                      <span className="progresso-list-title">
                        {module.title}
                      </span>
                      <span className="progresso-list-meta">
                        {trackLabel(module.track_id)} <ArrowRight size={13} />
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        <section className="progresso-section" aria-labelledby="dominio">
          <h2 id="dominio">O que você já praticou</h2>
          {modulesWithAttempts.length === 0 ? (
            <p>
              Ainda não há atividades respondidas. Abra um módulo e faça a etapa
              “Praticar”: o resultado aparece aqui.
            </p>
          ) : (
            <ul className="progresso-list">
              {modulesWithAttempts.map(moduleId => {
                const module = findModule(moduleId);
                if (!module) return null;
                const moduleAttempts = (attempts ?? []).filter(
                  a => a.moduleId === moduleId
                );
                const mastery = masteryOf(moduleAttempts, reviews, moduleId);
                return (
                  <li key={moduleId}>
                    <Link href={`/modulo/${moduleId}`}>
                      <span className="progresso-list-title">
                        {module.title}
                      </span>
                      <span className="progresso-list-meta">
                        <span className={`mastery mastery--${mastery}`}>
                          {MASTERY_LABEL[mastery]}
                        </span>
                        {moduleAttempts.length} tentativa
                        {moduleAttempts.length > 1 ? "s" : ""}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        <section className="progresso-section" aria-labelledby="dados">
          <h2 id="dados">Levar o progresso com você</h2>
          <p>
            O arquivo exportado guarda progresso, etapas concluídas, favoritos,
            tentativas e o calendário de revisões. Ele não contém nenhum dado
            pessoal — só o identificador dos módulos.
          </p>
          <div className="progresso-actions">
            <button
              type="button"
              className="primary-button"
              onClick={exportFile}
              disabled={busy}
            >
              <Download size={16} aria-hidden="true" /> Exportar progresso
            </button>
            <button
              type="button"
              className="secondary-button secondary-button--outline"
              onClick={() => fileRef.current?.click()}
              disabled={busy}
            >
              <Upload size={16} aria-hidden="true" /> Importar arquivo
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="application/json,.json"
              className="sr-only"
              aria-label="Escolher arquivo de progresso"
              onChange={event => {
                const file = event.target.files?.[0];
                if (file) void importFile(file);
              }}
            />
            <button
              type="button"
              className="text-button progresso-danger"
              onClick={reset}
              disabled={busy}
            >
              <Trash2 size={14} aria-hidden="true" /> Apagar dados deste
              navegador
            </button>
          </div>
          <p className="progresso-fineprint">
            <RotateCcw size={12} aria-hidden="true" /> A importação nunca reduz
            o progresso que você já tem: ela só soma.
          </p>
        </section>
      </main>
    </div>
  );
}
