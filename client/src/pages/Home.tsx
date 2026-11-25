import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "wouter";
import { api, type ModuleData, type TrackData } from "@/lib/api";
import { MODULES, trackCoverage } from "@/lib/curriculum";
import { buildWeek, streak } from "@/lib/week";
import { useDialogA11y } from "@/hooks/useDialogA11y";
import { toast } from "sonner";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  BrainCircuit,
  Check,
  ChevronDown,
  CircleHelp,
  Clock3,
  Code2,
  Headphones,
  Languages,
  LayoutGrid,
  Menu,
  MessageCircle,
  Mic2,
  Play,
  Search,
  Sparkles,
  Star,
  Target,
  Trophy,
  Volume2,
  X,
  Zap,
} from "lucide-react";

type TrackId = string;
type ViewId = "inicio" | "catalogo" | "agenda";
type TutorMessage = { role: "assistant" | "user"; text: string };

const ICON_MAP: Record<string, typeof Code2> = {
  Code2,
  BarChart3,
  Languages,
  BookOpen,
};

const initialMessages: TutorMessage[] = [
  {
    role: "assistant",
    text: "Oi! Sou o Nilo, seu tutor de aprendizagem. Posso explicar um conceito, criar um exercício ou montar uma revisão rápida.",
  },
];

function ProgressRing({ value }: { value: number }) {
  return (
    <div
      className="progress-ring"
      style={{ "--progress": `${value * 3.6}deg` } as React.CSSProperties}
      role="img"
      aria-label={`${value}% do currículo concluído`}
    >
      <div className="progress-ring__inner">
        <span>{value}%</span>
      </div>
    </div>
  );
}

export default function Home() {
  const [tracks, setTracks] = useState<TrackData[]>([]);
  const [modules, setModules] = useState<ModuleData[]>([]);
  const [totalModules, setTotalModules] = useState(-1);
  const [activeTrack, setActiveTrack] = useState<TrackId>("alfabetizacao");
  const [activeView, setActiveView] = useState<ViewId>("inicio");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [selectedModule, setSelectedModule] = useState<ModuleData | null>(null);
  const [isTutorOpen, setIsTutorOpen] = useState(false);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [messages, setMessages] = useState<TutorMessage[]>(initialMessages);
  const [messageInput, setMessageInput] = useState("");
  const [voiceActive, setVoiceActive] = useState(false);
  const [tutorLoading, setTutorLoading] = useState(false);
  const [progress, setProgress] = useState<Record<string, number>>({});
  const [activity, setActivity] = useState<Record<string, number>>({});
  const [, navigate] = useLocation();

  const now = useMemo(() => new Date(), []);
  const week = useMemo(() => buildWeek(now, activity), [now, activity]);
  const weekSteps = week.reduce((total, day) => total + day.steps, 0);
  const currentStreak = streak(activity, now);
  const startedModules = Object.keys(progress).length;
  const completedModules = Object.values(progress).filter(
    value => value >= 100
  ).length;
  const overallPercent =
    Math.round(
      (Object.values(progress).reduce((total, value) => total + value, 0) /
        MODULES.length) *
        10
    ) / 10;

  useEffect(() => {
    api
      .getTracks()
      .then(setTracks)
      .catch(() => {});
    api
      .getProgressMap()
      .then(setProgress)
      .catch(() => {});
    api
      .getActivity()
      .then(setActivity)
      .catch(() => {});
  }, []);

  useEffect(() => {
    let active = true;
    api
      .getModules({ track: activeTrack, search: search || undefined, page })
      .then(res => {
        if (!active) return;
        setTotalModules(res.total);
        setModules(prev => (page === 1 ? res.items : [...prev, ...res.items]));
      })
      .catch(() => {
        if (active) toast.error("Não foi possível carregar o catálogo.");
      });
    return () => {
      active = false;
    };
  }, [activeTrack, search, page]);

  useEffect(() => {
    if (!isTutorOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsTutorOpen(false);
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [isTutorOpen]);

  const closeModuleModal = useCallback(() => setSelectedModule(null), []);
  const modalRef = useDialogA11y<HTMLDivElement>(
    Boolean(selectedModule),
    closeModuleModal
  );

  const handleModuleOpen = (mod: ModuleData) => setSelectedModule(mod);

  const handlePlay = (mod: ModuleData) => {
    setSelectedModule(null);
    navigate(`/modulo/${mod.id}`);
  };

  const speakText = (text: string) => {
    if (!("speechSynthesis" in window)) {
      toast.info("Leitura em voz alta indisponível", {
        description: "Este navegador não oferece a síntese de voz local.",
      });
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "pt-BR";
    utterance.rate = 0.94;
    utterance.pitch = 1.02;
    utterance.onstart = () => setVoiceActive(true);
    utterance.onend = () => setVoiceActive(false);
    window.speechSynthesis.speak(utterance);
  };

  const handleTutorSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = messageInput.trim();
    if (!trimmed || tutorLoading) return;
    setMessages(prev => [...prev, { role: "user", text: trimmed }]);
    setMessageInput("");
    setTutorLoading(true);
    try {
      const data = await api.askTutor(trimmed, activeTrack);
      setMessages(prev => [...prev, { role: "assistant", text: data.answer }]);
    } catch {
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          text: "Tive um pequeno problema. Tente explicar o conceito com suas palavras — é uma ótima forma de aprender.",
        },
      ]);
    } finally {
      setTutorLoading(false);
    }
  };

  const updateView = (view: ViewId) => {
    setActiveView(view);
    setIsMobileNavOpen(false);
    if (view === "catalogo")
      document
        .getElementById("catalogo")
        ?.scrollIntoView({ behavior: "smooth" });
    if (view === "agenda")
      document.getElementById("agenda")?.scrollIntoView({ behavior: "smooth" });
    if (view === "inicio") window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const selectTrack = (trackId: TrackId, scroll = false) => {
    setActiveTrack(trackId);
    setActiveView("catalogo");
    setPage(1);
    setIsMobileNavOpen(false);
    if (scroll)
      document
        .getElementById("catalogo")
        ?.scrollIntoView({ behavior: "smooth" });
  };

  const getIcon = (name: string) => ICON_MAP[name] || BookOpen;
  const activeTrackData = tracks.find(t => t.id === activeTrack);
  const selectedProgress = selectedModule
    ? (progress[selectedModule.id] ?? 0)
    : 0;
  const hasMore = totalModules >= 0 && modules.length < totalModules;

  return (
    <div className="app-shell">
      <a className="skip-link" href="#conteudo">
        Ir para o conteúdo
      </a>

      <aside
        className={`sidebar ${isMobileNavOpen ? "sidebar--open" : ""}`}
        id="menu-lateral"
      >
        <div className="brand-lockup">
          <div className="brand-mark">
            <Sparkles size={19} fill="currentColor" />
          </div>
          <div>
            <div className="brand-name">
              aprende<span>.</span>
            </div>
            <div className="brand-subtitle">Brasil</div>
          </div>
        </div>

        <div className="sidebar-section-label">Seu espaço</div>
        <nav className="sidebar-nav" aria-label="Navegação principal">
          <button
            className={`sidebar-link ${activeView === "inicio" ? "is-active" : ""}`}
            onClick={() => updateView("inicio")}
            aria-current={activeView === "inicio" ? "page" : undefined}
          >
            <LayoutGrid size={18} /> <span>Visão geral</span>
          </button>
          <button
            className={`sidebar-link ${activeView === "catalogo" ? "is-active" : ""}`}
            onClick={() => updateView("catalogo")}
            aria-current={activeView === "catalogo" ? "page" : undefined}
          >
            <BookOpen size={18} /> <span>Catálogo</span>
            <span className="nav-count" aria-hidden="true">
              {totalModules}
            </span>
          </button>
          <button
            className={`sidebar-link ${activeView === "agenda" ? "is-active" : ""}`}
            onClick={() => updateView("agenda")}
            aria-current={activeView === "agenda" ? "page" : undefined}
          >
            <Clock3 size={18} /> <span>Minha agenda</span>
          </button>
        </nav>

        <div className="sidebar-section-label sidebar-section-label--space">
          Trilhas
        </div>
        <div className="track-nav">
          {tracks.map(track => {
            const Icon = getIcon(track.icon);
            return (
              <button
                key={track.id}
                className={`track-nav-item track-nav-item--${track.color} ${activeTrack === track.id ? "is-current" : ""}`}
                onClick={() => selectTrack(track.id)}
                aria-pressed={activeTrack === track.id}
              >
                <span className="track-nav-icon">
                  <Icon size={17} />
                </span>
                <span>{track.label}</span>
                {activeTrack === track.id && (
                  <span className="track-dot" aria-hidden="true" />
                )}
              </button>
            );
          })}
        </div>

        <div className="sidebar-spacer" />
        <div className="sidebar-promo">
          <div className="promo-orbit promo-orbit--one" aria-hidden="true" />
          <div className="promo-orbit promo-orbit--two" aria-hidden="true" />
          <Zap size={20} className="promo-icon" aria-hidden="true" />
          <strong>Aprenda em pequenos passos.</strong>
          <span>Constância vence a pressa.</span>
          <button onClick={() => updateView("catalogo")}>
            Ver catálogo <ArrowRight size={13} />
          </button>
        </div>
      </aside>

      {isMobileNavOpen && (
        <button
          className="sidebar-backdrop"
          aria-label="Fechar menu"
          onClick={() => setIsMobileNavOpen(false)}
        />
      )}

      <main className="main-content" id="conteudo" tabIndex={-1}>
        <header className="topbar">
          <button
            className="mobile-menu-button"
            aria-label={isMobileNavOpen ? "Fechar menu" : "Abrir menu"}
            aria-expanded={isMobileNavOpen}
            aria-controls="menu-lateral"
            onClick={() => setIsMobileNavOpen(open => !open)}
          >
            <Menu size={20} />
          </button>
          <div className="breadcrumb" aria-label="Você está em">
            <span>Espaço de aprendizagem</span>
            <span className="breadcrumb-slash" aria-hidden="true">
              /
            </span>
            <strong>
              {activeView === "inicio"
                ? "Visão geral"
                : activeView === "catalogo"
                  ? "Catálogo"
                  : "Minha agenda"}
            </strong>
          </div>
          <div className="topbar-actions">
            <button
              className="topbar-icon-button"
              aria-label="Abrir o tutor Nilo"
              onClick={() => setIsTutorOpen(true)}
            >
              <CircleHelp size={18} />
            </button>
            <Link href="/progresso" className="login-button">
              Meu progresso <ArrowRight size={14} />
            </Link>
            <Link href="/sobre" className="login-button login-button--ghost">
              Sobre o projeto <ArrowRight size={14} />
            </Link>
          </div>
        </header>

        <div className="content-wrap">
          <section
            className="welcome-row"
            id="inicio"
            aria-labelledby="titulo-boas-vindas"
          >
            <div>
              <div className="eyebrow">
                <span className="eyebrow-dot" /> BEM-VINDO(A) AO APRENDE BRASIL
              </div>
              <h1 id="titulo-boas-vindas">
                Aprender é para todos<span className="headline-period">.</span>
              </h1>
              <p className="welcome-note">
                Alfabetização, informática, matemática e idiomas — no seu ritmo.
              </p>
            </div>
            <div className="streak-chip">
              <span className="streak-flame" aria-hidden="true">
                ✦
              </span>
              <div>
                <strong>
                  {currentStreak > 0
                    ? `${currentStreak} ${currentStreak === 1 ? "dia" : "dias"}`
                    : `${tracks.length} trilhas`}
                </strong>
                <span>
                  {currentStreak > 0 ? "estudando seguido" : "disponíveis"}
                </span>
              </div>
              <Trophy size={18} aria-hidden="true" />
            </div>
          </section>

          <section className="hero-card" aria-labelledby="hero-titulo">
            <div className="hero-copy">
              <div className="hero-kicker">
                <span className="live-dot" /> COMECE AGORA
              </div>
              <h2 id="hero-titulo">
                Ler e escrever
                <br />
                muda tudo.
              </h2>
              <p>
                Comece pela <strong>Alfabetização</strong> — das letras às
                primeiras frases, passo a passo.
              </p>
              <button
                className="primary-button"
                onClick={() => selectTrack("alfabetizacao", true)}
              >
                Começar a aprender <ArrowRight size={16} />
              </button>
              <div className="hero-meta">
                <span>
                  <Clock3 size={14} /> 8-20 min por módulo
                </span>
                <span>
                  <Target size={14} /> Sem pressa, no seu ritmo
                </span>
              </div>
            </div>
            <div className="hero-visual" aria-hidden="true">
              <div className="hero-grid" />
              <div className="hero-sun" />
              <div className="hero-planet hero-planet--large" />
              <div className="hero-planet hero-planet--small" />
              <div className="hero-card-note hero-card-note--top">
                <span>A B C</span>
                <small>letras</small>
              </div>
              <div className="hero-card-note hero-card-note--bottom">
                <span>1 2 3</span>
                <small>números</small>
              </div>
            </div>
          </section>

          <section className="stat-grid" aria-label="Catálogo por trilha">
            {tracks.map(t => {
              const Icon = getIcon(t.icon);
              const coverage = trackCoverage(t);
              return (
                <div className="stat-card" key={t.id}>
                  <div className="stat-card-top">
                    <span className="stat-label">{t.label}</span>
                    <Icon size={17} aria-hidden="true" />
                  </div>
                  <div className="stat-value-row">
                    <strong>{t.module_count}</strong>
                    <span>módulos prontos</span>
                  </div>
                  <div
                    className="mini-progress"
                    role="progressbar"
                    aria-label={`${t.label}: ${Math.round(coverage)}% do catálogo previsto`}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-valuenow={Math.round(coverage)}
                  >
                    <span style={{ width: `${coverage}%` }} />
                  </div>
                  <p>{t.description}</p>
                </div>
              );
            })}
          </section>

          <section
            className="section-block"
            id="catalogo"
            aria-labelledby="trilhas-titulo"
          >
            <div className="section-heading">
              <div>
                <div className="eyebrow">EXPLORE SEU POTENCIAL</div>
                <h2 id="trilhas-titulo">Trilhas para ir além</h2>
              </div>
            </div>
            <div className="track-cards">
              {tracks.map(track => {
                const Icon = getIcon(track.icon);
                const isActive = activeTrack === track.id;
                const coverage = trackCoverage(track);
                return (
                  <button
                    key={track.id}
                    className={`track-card track-card--${track.color} ${isActive ? "is-selected" : ""}`}
                    onClick={() => selectTrack(track.id)}
                    aria-pressed={isActive}
                  >
                    <div className="track-card-head">
                      <span className="track-card-icon">
                        <Icon size={20} aria-hidden="true" />
                      </span>
                      <span className="track-card-arrow">
                        <ArrowRight size={15} aria-hidden="true" />
                      </span>
                    </div>
                    <div className="track-card-eyebrow">{track.eyebrow}</div>
                    <h3>{track.label}</h3>
                    <p>{track.description}</p>
                    <div className="track-card-foot">
                      <span>{track.module_count} módulos</span>
                      <span className="track-progress-line" aria-hidden="true">
                        <i style={{ width: `${coverage}%` }} />
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </section>

          <section
            className="section-block module-section"
            aria-labelledby="modulos-titulo"
          >
            <div className="section-heading section-heading--modules">
              <div>
                <div className="eyebrow">
                  <span className="eyebrow-dot eyebrow-dot--blue" />{" "}
                  {search.trim()
                    ? "BUSCA EM TODAS AS TRILHAS"
                    : activeTrackData?.label?.toUpperCase() || "MÓDULOS"}
                </div>
                <h2 id="modulos-titulo">Módulos disponíveis</h2>
              </div>
              <div className="module-tools">
                <div className="search-box">
                  <Search size={16} aria-hidden="true" />
                  <input
                    value={search}
                    onChange={e => {
                      setSearch(e.target.value);
                      setPage(1);
                    }}
                    placeholder="Buscar módulo"
                    aria-label="Buscar módulo pelo título ou descrição"
                    type="search"
                  />
                </div>
              </div>
            </div>

            <p className="module-count" aria-live="polite">
              {totalModules < 0
                ? "Carregando módulos…"
                : totalModules === 0
                  ? "Nenhum módulo encontrado"
                  : `Mostrando ${modules.length} de ${totalModules} ${totalModules === 1 ? "módulo" : "módulos"}`}
            </p>

            <div className="module-list">
              {modules.map(mod => {
                const Icon = getIcon(mod.icon);
                const percent = Math.round(progress[mod.id] ?? 0);
                return (
                  <article
                    className="module-row"
                    key={mod.id}
                    onClick={() => handleModuleOpen(mod)}
                  >
                    <div className={`module-icon module-icon--${mod.accent}`}>
                      <Icon size={20} aria-hidden="true" />
                    </div>
                    <div className="module-info">
                      <div className="module-title-row">
                        <h3>
                          <button
                            className="module-open"
                            onClick={e => {
                              e.stopPropagation();
                              handleModuleOpen(mod);
                            }}
                          >
                            {mod.title}
                          </button>
                        </h3>
                        {mod.featured && (
                          <span className="small-tag">
                            <Star
                              size={11}
                              fill="currentColor"
                              aria-hidden="true"
                            />{" "}
                            recomendado
                          </span>
                        )}
                      </div>
                      <p>{mod.subtitle}</p>
                      <div className="module-details">
                        <span>{mod.level}</span>
                        <span className="detail-separator" aria-hidden="true" />
                        <span>
                          <Clock3 size={13} /> {mod.duration_min} min
                        </span>
                        <span className="detail-separator" aria-hidden="true" />
                        <span>{mod.step_count ?? 5} etapas</span>
                      </div>
                    </div>
                    {percent > 0 && (
                      <div className="module-progress">
                        <div className="module-progress-head">
                          <span>
                            <Check size={11} aria-hidden="true" /> seu progresso
                          </span>
                          <strong>{percent}%</strong>
                        </div>
                        <div
                          className="mini-progress"
                          role="progressbar"
                          aria-label={`Progresso em ${mod.title}`}
                          aria-valuemin={0}
                          aria-valuemax={100}
                          aria-valuenow={percent}
                        >
                          <span style={{ width: `${percent}%` }} />
                        </div>
                      </div>
                    )}
                    <Link
                      href={`/modulo/${mod.id}`}
                      className="module-play"
                      aria-label={`Abrir ${mod.title}`}
                      onClick={e => e.stopPropagation()}
                    >
                      <Play size={15} fill="currentColor" aria-hidden="true" />
                    </Link>
                  </article>
                );
              })}
              {totalModules >= 0 && modules.length === 0 && (
                <div className="empty-state">
                  <Search size={22} aria-hidden="true" />
                  <strong>Nenhum módulo encontrado</strong>
                  <span>
                    Tente buscar por outra palavra ou troque de trilha.
                  </span>
                </div>
              )}
            </div>

            {hasMore && (
              <div className="load-more-row">
                <button
                  className="secondary-button load-more"
                  onClick={() => setPage(p => p + 1)}
                >
                  Carregar mais módulos <ChevronDown size={15} />
                </button>
              </div>
            )}
          </section>

          <section
            className="agenda-section"
            id="agenda"
            aria-labelledby="agenda-titulo"
          >
            <div className="agenda-copy">
              <div className="eyebrow">PARA MANTER O RITMO</div>
              <h2 id="agenda-titulo">Seu próximo pequeno passo</h2>
              <p>
                {weekSteps > 0
                  ? `Você marcou ${weekSteps} ${weekSteps === 1 ? "etapa" : "etapas"} nos últimos sete dias. Uma sessão curta hoje mantém o ritmo.`
                  : "Ainda não há etapas marcadas nesta semana. Comece por um módulo curto — cinco minutos já contam."}
              </p>
              <button
                className="secondary-button"
                onClick={() => selectTrack(activeTrack, true)}
              >
                Ver módulos <ArrowRight size={15} />
              </button>
            </div>
            <div className="agenda-days">
              <div className="agenda-week-label">
                <span>ÚLTIMOS 7 DIAS</span>
                <span>
                  {startedModules} iniciados · {completedModules} concluídos
                </span>
              </div>
              <div
                className="agenda-day-grid"
                role="list"
                aria-label="Etapas concluídas por dia"
              >
                {week.map(item => (
                  <div
                    key={item.key}
                    className={`agenda-day ${item.isToday ? "is-today" : ""}`}
                    role="listitem"
                    aria-label={`${item.label}, dia ${item.day}: ${item.steps} ${item.steps === 1 ? "etapa" : "etapas"}`}
                    title={`${item.steps} ${item.steps === 1 ? "etapa" : "etapas"}`}
                  >
                    <span>{item.label}</span>
                    <strong>{item.day}</strong>
                    <i
                      className={item.steps > 0 ? "is-done" : ""}
                      aria-hidden="true"
                    />
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section
            className="progress-section"
            aria-labelledby="progresso-titulo"
          >
            <div>
              <div className="eyebrow">SEU CAMINHO</div>
              <h2 id="progresso-titulo">Progresso geral</h2>
              <p>
                {startedModules === 0
                  ? "Seu progresso fica salvo apenas neste navegador. Nada é enviado para servidores."
                  : `Você já começou ${startedModules} de 205 módulos. Tudo salvo neste navegador.`}
              </p>
            </div>
            <div className="progress-overview">
              <ProgressRing value={Math.round(overallPercent)} />
              <div>
                <strong>{completedModules}</strong>
                <span>módulos concluídos</span>
              </div>
            </div>
          </section>

          <footer className="footer">
            <span>
              aprende<span className="footer-period">.</span> Brasil
            </span>
            <span>Aprender é uma prática diária.</span>
            <span className="footer-links">
              <Link href="/sobre">Privacidade</Link>
              <button onClick={() => setIsTutorOpen(true)}>Ajuda</button>
            </span>
          </footer>
        </div>
      </main>

      <button
        className={`tutor-fab ${isTutorOpen ? "is-open" : ""}`}
        onClick={() => setIsTutorOpen(open => !open)}
        aria-label={isTutorOpen ? "Fechar tutor Nilo" : "Abrir tutor Nilo"}
        aria-expanded={isTutorOpen}
        aria-controls="tutor-nilo"
      >
        <span className="tutor-fab-pulse" aria-hidden="true" />
        <MessageCircle size={20} aria-hidden="true" />
        <span>Nilo</span>
      </button>

      {isTutorOpen && (
        <aside className="tutor-panel" id="tutor-nilo" aria-label="Tutor Nilo">
          <div className="tutor-panel-head">
            <div className="tutor-avatar">
              <BrainCircuit size={19} aria-hidden="true" />
            </div>
            <div>
              <strong>Nilo, seu tutor</strong>
              <span>Aprendizagem com curiosidade</span>
            </div>
            <button
              onClick={() => setIsTutorOpen(false)}
              aria-label="Fechar tutor"
            >
              <X size={18} />
            </button>
          </div>
          <div className="tutor-suggestion-row">
            <button
              onClick={() =>
                setMessageInput("Explique este tema de um jeito simples")
              }
            >
              Explicar simples
            </button>
            <button onClick={() => setMessageInput("Crie um exercício rápido")}>
              Criar exercício
            </button>
          </div>
          <div
            className="tutor-messages"
            role="log"
            aria-live="polite"
            aria-label="Conversa com o tutor"
          >
            {messages.map((msg, i) => (
              <div
                className={`tutor-message tutor-message--${msg.role}`}
                key={i}
              >
                <span>{msg.text}</span>
                {msg.role === "assistant" && (
                  <button
                    className="speak-button"
                    onClick={() => speakText(msg.text)}
                    aria-label="Ouvir resposta em voz alta"
                  >
                    <Volume2 size={13} />
                  </button>
                )}
              </div>
            ))}
            {tutorLoading && (
              <div
                className="tutor-message tutor-message--assistant tutor-message--typing"
                aria-label="Nilo está escrevendo"
              >
                <span />
                <span />
                <span />
              </div>
            )}
          </div>
          <form className="tutor-input-row" onSubmit={handleTutorSubmit}>
            <input
              value={messageInput}
              onChange={e => setMessageInput(e.target.value)}
              placeholder="Escreva sua dúvida..."
              aria-label="Mensagem para o tutor"
            />
            <button
              type="button"
              className={voiceActive ? "is-speaking" : ""}
              onClick={() =>
                speakText("Olá! Estou pronto para ajudar você a aprender.")
              }
              aria-label="Testar leitura em voz alta"
              aria-pressed={voiceActive}
            >
              <Mic2 size={17} />
            </button>
            <button type="submit" aria-label="Enviar mensagem">
              <ArrowRight size={17} />
            </button>
          </form>
          <div className="tutor-voice-note">
            <Headphones size={13} aria-hidden="true" /> Voz em pt-BR disponível.
          </div>
        </aside>
      )}

      {selectedModule && (
        <div className="modal-backdrop" onClick={closeModuleModal}>
          <div
            className="module-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-titulo"
            ref={modalRef}
            onClick={e => e.stopPropagation()}
          >
            <button
              className="modal-close"
              onClick={closeModuleModal}
              aria-label="Fechar detalhes do módulo"
            >
              <X size={18} />
            </button>
            <div className={`modal-icon modal-icon--${selectedModule.accent}`}>
              {(() => {
                const I = getIcon(selectedModule.icon);
                return <I size={26} aria-hidden="true" />;
              })()}
            </div>
            <div className="eyebrow">
              {selectedModule.level} · {selectedModule.duration_min} min
            </div>
            <h2 id="modal-titulo">{selectedModule.title}</h2>
            <p>{selectedModule.subtitle}</p>
            {selectedProgress > 0 && (
              <>
                <div className="modal-progress-row">
                  <span>Seu progresso</span>
                  <strong>{Math.round(selectedProgress)}%</strong>
                </div>
                <div
                  className="mini-progress"
                  role="progressbar"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={Math.round(selectedProgress)}
                  aria-label="Progresso neste módulo"
                >
                  <span style={{ width: `${selectedProgress}%` }} />
                </div>
              </>
            )}
            <div className="modal-next-step">
              <span className="modal-check">
                <Check size={14} aria-hidden="true" />
              </span>
              <div>
                <strong>Próxima etapa</strong>
                <p>Conhecer o conceito em 3 minutos</p>
              </div>
            </div>
            <button
              className="primary-button primary-button--full"
              onClick={() => handlePlay(selectedModule)}
            >
              <Play size={16} fill="currentColor" aria-hidden="true" />
              {selectedProgress > 0 ? "Continuar módulo" : "Começar módulo"}
            </button>
            <button
              className="modal-tutor-link"
              onClick={() => {
                setSelectedModule(null);
                setIsTutorOpen(true);
              }}
            >
              Tirar uma dúvida com Nilo <ArrowRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
