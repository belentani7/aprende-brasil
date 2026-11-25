import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "wouter";
import ActivityCard from "@/components/ActivityCard";
import { api, type ModuleWithSteps } from "@/lib/api";
import { trackLabel } from "@/lib/curriculum";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  Clock3,
  Loader2,
  Sparkles,
  Star,
  Volume2,
} from "lucide-react";

const STEP_LABEL: Record<string, string> = {
  explanation: "Entender",
  example: "Exemplo",
  practice: "Praticar",
  check: "Verificar",
  next: "Próximo passo",
};

export default function Modulo() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [module, setModule] = useState<ModuleWithSteps | null>(null);
  const [loading, setLoading] = useState(true);
  const [done, setDone] = useState<number[]>([]);
  const [percent, setPercent] = useState(0);
  const [favorite, setFavorite] = useState(false);
  const [savedNote, setSavedNote] = useState("");
  const [learnedNote, setLearnedNote] = useState("");
  const headingRef = useRef<HTMLHeadingElement>(null);
  const answeredRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    if (!id) return;
    let active = true;
    setLoading(true);
    setModule(null);

    Promise.all([
      api.getModule(id),
      api.getModuleProgress(id),
      api.getFavorites(),
    ])
      .then(([loaded, progress, favorites]) => {
        if (!active) return;
        setModule(loaded);
        const valid = progress.completed.filter(order =>
          loaded.steps.some(step => step.order === order)
        );
        // Migração: versões antigas salvavam só o percentual, sem as etapas.
        const restored = valid.length
          ? valid
          : loaded.steps
              .filter(
                step =>
                  step.order <=
                  Math.round((progress.percent / 100) * loaded.steps.length)
              )
              .map(step => step.order);
        setDone(restored);
        setPercent(progress.percent);
        setFavorite(favorites.includes(id));
        document.title = `${loaded.title} · aprende. Brasil`;
      })
      .catch(() => {
        if (!active) return;
        toast.error("Não foi possível carregar o módulo.", {
          description:
            "Confira o endereço ou volte ao catálogo para escolher outro.",
        });
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
      document.title = "aprende. Brasil — educação aberta em pequenos passos";
      if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    };
  }, [id]);

  useEffect(() => {
    if (module && !loading) headingRef.current?.focus();
  }, [module, loading]);

  const total = module?.steps.length ?? 0;
  const progress = Math.round(percent);

  const persist = async (completed: number[]) => {
    if (!module || total === 0) return;
    const nextPercent = (completed.length / total) * 100;
    try {
      const result = await api.saveProgress(module.id, nextPercent, completed);
      setPercent(result.percent);
      setSavedNote(
        result.percent >= 100
          ? "Módulo concluído. Progresso salvo neste navegador."
          : `Progresso salvo: ${Math.round(result.percent)}%.`
      );
    } catch {
      setSavedNote("Não foi possível salvar o progresso agora.");
    }
  };

  const toggleStep = (order: number) => {
    setDone(previous => {
      const completed = previous.includes(order)
        ? previous.filter(value => value !== order)
        : [...previous, order];
      void persist(completed);
      return completed;
    });
  };

  const finish = async () => {
    if (!module) return;
    const all = module.steps.map(step => step.order);
    setDone(all);
    await persist(all);
    // A conclusão agenda a revisão espaçada com base no desempenho real nas
    // atividades — e avisa quando o módulo volta, sem prometer domínio.
    const note = await api.completeModule(module.id);
    setSavedNote(note);
    toast.success("Módulo concluído!", { description: note });
  };

  const handleActivityResult = (
    activityId: string,
    result: { correct: boolean },
    stepOrder: number
  ) => {
    if (!module) return;
    answeredRef.current.add(activityId);
    void api.recordAttempt({
      moduleId: module.id,
      activityId,
      correct: result.correct,
    });
    if (result.correct) {
      setLearnedNote(
        `Atividade respondida. ${answeredRef.current.size} atividade(s) praticada(s) neste módulo.`
      );
      // Acertar a atividade já marca a etapa de prática: fazer é a evidência,
      // não apenas ler.
      if (!done.includes(stepOrder)) {
        const completed = [...done, stepOrder];
        setDone(completed);
        void persist(completed);
      }
    }
  };

  const toggleFavorite = async () => {
    if (!module) return;
    try {
      const res = await api.toggleFavorite(module.id);
      setFavorite(res.favorited);
      toast(
        res.favorited ? "Adicionado aos favoritos" : "Removido dos favoritos"
      );
    } catch {
      toast.error("Não foi possível atualizar o favorito.");
    }
  };

  const speak = (text: string) => {
    if (!("speechSynthesis" in window)) {
      toast.info("Leitura em voz alta indisponível neste navegador.");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "pt-BR";
    utterance.rate = 0.94;
    window.speechSynthesis.speak(utterance);
  };

  if (loading) {
    return (
      <div className="modulo-loading" role="status" aria-live="polite">
        <Loader2 className="animate-spin" size={20} aria-hidden="true" />{" "}
        Carregando módulo...
      </div>
    );
  }

  if (!module) {
    return (
      <div className="modulo-empty">
        <h1>Módulo não encontrado</h1>
        <p>
          Talvez o endereço esteja incompleto. Escolha um módulo no catálogo.
        </p>
        <Link href="/" className="primary-button">
          <ArrowLeft size={16} /> Voltar ao catálogo
        </Link>
      </div>
    );
  }

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
        <nav className="modulo-topbar-actions" aria-label="Navegação do módulo">
          <Link href="/" className="text-button">
            <ArrowLeft size={14} /> Catálogo
          </Link>
          <Link href="/sobre" className="text-button">
            Sobre o projeto <ArrowRight size={14} />
          </Link>
        </nav>
      </header>

      <main className="modulo-wrap">
        <ol className="modulo-breadcrumb" aria-label="Trilha de navegação">
          <li>
            <Link href="/">Início</Link>
          </li>
          <li aria-hidden="true">/</li>
          <li>{trackLabel(module.track_id)}</li>
          <li aria-hidden="true">/</li>
          <li aria-current="page">{module.title}</li>
        </ol>

        <header className={`modulo-hero modulo-hero--${module.accent}`}>
          <div className="modulo-hero-copy">
            <div className="eyebrow">
              <BookOpen size={13} aria-hidden="true" /> {module.level} ·{" "}
              <Clock3 size={13} aria-hidden="true" /> {module.duration_min} min
              · {total} etapas
            </div>
            <h1 ref={headingRef} tabIndex={-1}>
              {module.title}
            </h1>
            <p>{module.subtitle}</p>
          </div>
          <button
            onClick={toggleFavorite}
            className={`modulo-favorite ${favorite ? "is-favorite" : ""}`}
            aria-pressed={favorite}
            aria-label={
              favorite ? "Remover dos favoritos" : "Adicionar aos favoritos"
            }
          >
            <Star
              size={16}
              fill={favorite ? "currentColor" : "none"}
              aria-hidden="true"
            />
            {favorite ? "Favorito" : "Favoritar"}
          </button>
        </header>

        <section className="modulo-progress" aria-labelledby="progresso-modulo">
          <div className="modulo-progress-head">
            <strong id="progresso-modulo">Progresso do módulo</strong>
            <span>
              {done.length} de {total} etapas · {progress}%
            </span>
          </div>
          <div
            className="modulo-progress-bar"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={progress}
            aria-label="Progresso do módulo"
          >
            <span style={{ width: `${progress}%` }} />
          </div>
          <p className="sr-only" aria-live="polite">
            {savedNote} {learnedNote}
          </p>
        </section>

        <ol className="modulo-steps">
          {module.steps.map(step => {
            const isDone = done.includes(step.order);
            const typeLabel = STEP_LABEL[step.type] || step.type;
            return (
              <li
                key={step.order}
                className={`modulo-step ${isDone ? "is-done" : ""}`}
              >
                <button
                  onClick={() => toggleStep(step.order)}
                  aria-pressed={isDone}
                  aria-label={`${isDone ? "Desmarcar" : "Marcar"} etapa ${step.order}: ${step.title}`}
                  className="step-check"
                >
                  {isDone ? (
                    <Check size={15} aria-hidden="true" />
                  ) : (
                    <span aria-hidden="true">{step.order}</span>
                  )}
                </button>
                <div className="step-body">
                  <div className="step-meta">
                    <span className="step-type">{typeLabel}</span>
                    <h2>{step.title}</h2>
                  </div>
                  <p>{step.content?.text}</p>
                  {step.content?.objectives?.length ? (
                    <div className="step-objectives">
                      <h3>Neste módulo você vai:</h3>
                      <ul>
                        {step.content.objectives.map(objective => (
                          <li key={objective}>
                            <Check size={13} aria-hidden="true" /> {objective}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                  {step.content?.examples?.length ? (
                    <ul className="step-examples">
                      {step.content.examples.map(example => (
                        <li key={example}>{example}</li>
                      ))}
                    </ul>
                  ) : null}
                  {step.content?.vocabulary?.length ? (
                    <dl className="step-vocabulary">
                      {step.content.vocabulary.map(entry => (
                        <div key={entry.term}>
                          <dt>{entry.term}</dt>
                          <dd>
                            {entry.definition}
                            {entry.example ? ` — ${entry.example}` : ""}
                          </dd>
                        </div>
                      ))}
                    </dl>
                  ) : null}
                  {step.content?.activities?.length ? (
                    <div className="step-activities">
                      <h3 className="step-activities-title">
                        Pratique agora
                        <span>
                          {step.content.activities.length} atividade
                          {step.content.activities.length > 1 ? "s" : ""}
                        </span>
                      </h3>
                      {step.content.activities.map(activity => (
                        <ActivityCard
                          key={activity.id}
                          activity={activity}
                          onResult={result =>
                            handleActivityResult(
                              activity.id,
                              result,
                              step.order
                            )
                          }
                        />
                      ))}
                    </div>
                  ) : null}
                </div>
                <button
                  onClick={() =>
                    speak(
                      [
                        step.title,
                        step.content?.text || "",
                        ...(step.content?.activities ?? []).map(
                          activity => activity.prompt
                        ),
                      ].join(". ")
                    )
                  }
                  aria-label={`Ouvir a etapa ${step.title}`}
                  className="step-speak"
                >
                  <Volume2 size={16} aria-hidden="true" />
                </button>
              </li>
            );
          })}
        </ol>

        <div className="modulo-actions">
          <button
            onClick={finish}
            className="primary-button"
            disabled={progress >= 100}
          >
            <Sparkles size={17} aria-hidden="true" />
            {progress >= 100 ? "Módulo concluído" : "Concluir módulo"}
          </button>
          <Link href="/" className="secondary-button secondary-button--outline">
            Escolher outro módulo <ArrowRight size={15} />
          </Link>
        </div>
      </main>
    </div>
  );
}
