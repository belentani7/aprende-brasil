import { useEffect, useMemo, useState } from "react";
import { useLocation } from "wouter";
import { api, type TrackData, type ModuleData } from "@/lib/api";
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
  Plus,
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
  Code2, BarChart3, Languages, BookOpen,
};

const weekActivity = [
  { day: "SEG", value: 55 },
  { day: "TER", value: 76 },
  { day: "QUA", value: 42 },
  { day: "QUI", value: 88 },
  { day: "SEX", value: 64 },
  { day: "SÁB", value: 32 },
  { day: "DOM", value: 18 },
];

const initialMessages: TutorMessage[] = [
  {
    role: "assistant",
    text: "Oi! Sou o Nilo, seu tutor de aprendizagem. Posso explicar um conceito, criar um exercício ou montar uma revisão rápida.",
  },
];

function ProgressRing({ value }: { value: number }) {
  return (
    <div className="progress-ring" style={{ "--progress": `${value * 3.6}deg` } as React.CSSProperties}>
      <div className="progress-ring__inner">
        <span>{value}%</span>
      </div>
    </div>
  );
}

export default function Home() {
  const [tracks, setTracks] = useState<TrackData[]>([]);
  const [modules, setModules] = useState<ModuleData[]>([]);
  const [featuredModules, setFeaturedModules] = useState<ModuleData[]>([]);
  const [activeTrack, setActiveTrack] = useState<TrackId>("alfabetizacao");
  const [activeView, setActiveView] = useState<ViewId>("inicio");
  const [search, setSearch] = useState("");
  const [selectedModule, setSelectedModule] = useState<ModuleData | null>(null);
  const [isTutorOpen, setIsTutorOpen] = useState(false);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [messages, setMessages] = useState<TutorMessage[]>(initialMessages);
  const [messageInput, setMessageInput] = useState("");
  const [voiceActive, setVoiceActive] = useState(false);
  const [tutorLoading, setTutorLoading] = useState(false);
  const [totalModules, setTotalModules] = useState(0);
  const [, navigate] = useLocation();

  useEffect(() => {
    api.getTracks().then(setTracks).catch(() => {});
    api.getFeatured().then(setFeaturedModules).catch(() => {});
  }, []);

  useEffect(() => {
    api.getModules({ track: activeTrack, search: search || undefined })
      .then((res) => { setModules(res.items); setTotalModules(res.total); })
      .catch(() => {});
  }, [activeTrack, search]);

  const handleModuleOpen = (mod: ModuleData) => {
    setSelectedModule(mod);
    toast.success("Módulo aberto", { description: `${mod.title} está pronto para você.` });
  };

  const handlePlay = (mod: ModuleData) => {
    setSelectedModule(null);
    navigate(`/modulo/${mod.id}`);
  };

  const speakText = (text: string) => {
    if (!("speechSynthesis" in window)) {
      toast.info("Voz em preparação", { description: "Seu navegador não disponibilizou a leitura local." });
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
    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setMessageInput("");
    setTutorLoading(true);
    try {
      const data = await api.askTutor(trimmed, activeTrack);
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Tive um pequeno problema. Tente explicar o conceito com suas próprias palavras — é uma ótima forma de aprender." },
      ]);
    } finally {
      setTutorLoading(false);
    }
  };

  const updateView = (view: ViewId) => {
    setActiveView(view);
    setIsMobileNavOpen(false);
    if (view === "catalogo") document.getElementById("catalogo")?.scrollIntoView({ behavior: "smooth" });
    if (view === "agenda") document.getElementById("agenda")?.scrollIntoView({ behavior: "smooth" });
    if (view === "inicio") window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const getIcon = (name: string) => ICON_MAP[name] || BookOpen;
  const activeTrackData = tracks.find((t) => t.id === activeTrack);

  return (
    <div className="app-shell">
      <aside className={`sidebar ${isMobileNavOpen ? "sidebar--open" : ""}`}>
        <div className="brand-lockup">
          <div className="brand-mark"><Sparkles size={19} fill="currentColor" /></div>
          <div>
            <div className="brand-name">aprende<span>.</span></div>
            <div className="brand-subtitle">Brasil</div>
          </div>
        </div>

        <div className="sidebar-section-label">Seu espaço</div>
        <nav className="sidebar-nav" aria-label="Navegação principal">
          <button className={`sidebar-link ${activeView === "inicio" ? "is-active" : ""}`} onClick={() => updateView("inicio")}>
            <LayoutGrid size={18} /> <span>Visão geral</span>
          </button>
          <button className={`sidebar-link ${activeView === "catalogo" ? "is-active" : ""}`} onClick={() => updateView("catalogo")}>
            <BookOpen size={18} /> <span>Catálogo</span><span className="nav-count">{totalModules}</span>
          </button>
          <button className={`sidebar-link ${activeView === "agenda" ? "is-active" : ""}`} onClick={() => updateView("agenda")}>
            <Clock3 size={18} /> <span>Minha agenda</span>
          </button>
        </nav>

        <div className="sidebar-section-label sidebar-section-label--space">Trilhas</div>
        <div className="track-nav">
          {tracks.map((track) => {
            const Icon = getIcon(track.icon);
            return (
              <button key={track.id} className={`track-nav-item track-nav-item--${track.color} ${activeTrack === track.id ? "is-current" : ""}`} onClick={() => { setActiveTrack(track.id); setActiveView("catalogo"); setIsMobileNavOpen(false); }}>
                <span className="track-nav-icon"><Icon size={17} /></span>
                <span>{track.label}</span>
                {activeTrack === track.id && <span className="track-dot" />}
              </button>
            );
          })}
        </div>

        <div className="sidebar-spacer" />
        <div className="sidebar-promo">
          <div className="promo-orbit promo-orbit--one" />
          <div className="promo-orbit promo-orbit--two" />
          <Zap size={20} className="promo-icon" />
          <strong>Aprenda em pequenos passos.</strong>
          <span>Constância vence a pressa.</span>
          <button onClick={() => toast("Meta ajustada", { description: "Sua meta diária agora é de 20 minutos." })}>Ajustar meta <ArrowRight size={13} /></button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button className="mobile-menu-button" aria-label="Abrir menu" onClick={() => setIsMobileNavOpen((o) => !o)}><Menu size={20} /></button>
          <div className="breadcrumb"><span>Espaço de aprendizagem</span><span className="breadcrumb-slash">/</span><strong>{activeView === "inicio" ? "Visão geral" : activeView === "catalogo" ? "Catálogo" : "Minha agenda"}</strong></div>
          <div className="topbar-actions">
            <button className="topbar-icon-button" aria-label="Ajuda" onClick={() => toast("Abra o tutor Nilo para tirar dúvidas.")}><CircleHelp size={18} /></button>
          </div>
        </header>

        <div className="content-wrap">
          <section className="welcome-row" id="inicio">
            <div>
              <div className="eyebrow"><span className="eyebrow-dot" /> BEM-VINDO(A) AO APRENDE BRASIL</div>
              <h1>Aprender é para todos<span className="headline-period">.</span></h1>
              <p className="welcome-note">Alfabetização, informática, matemática e idiomas — no seu ritmo.</p>
            </div>
            <div className="streak-chip"><span className="streak-flame">✦</span><div><strong>{tracks.length} trilhas</strong><span>disponíveis</span></div><Trophy size={18} /></div>
          </section>

          <section className="hero-card">
            <div className="hero-copy">
              <div className="hero-kicker"><span className="live-dot" /> COMECE AGORA</div>
              <h2>Ler e escrever<br />muda tudo.</h2>
              <p>Comece pela <strong>Alfabetização</strong> — das letras às primeiras frases, passo a passo.</p>
              <button className="primary-button" onClick={() => { setActiveTrack("alfabetizacao"); setActiveView("catalogo"); }}>Começar a aprender <ArrowRight size={16} /></button>
              <div className="hero-meta"><span><Clock3 size={14} /> 8-20 min por módulo</span><span><Target size={14} /> Sem pressa, no seu ritmo</span></div>
            </div>
            <div className="hero-visual" aria-hidden="true">
              <div className="hero-grid" />
              <div className="hero-sun" />
              <div className="hero-planet hero-planet--large" />
              <div className="hero-planet hero-planet--small" />
              <div className="hero-card-note hero-card-note--top"><span>A B C</span><small>letras</small></div>
              <div className="hero-card-note hero-card-note--bottom"><span>1 2 3</span><small>números</small></div>
            </div>
          </section>

          <section className="stat-grid">
            {tracks.map((t) => {
              const Icon = getIcon(t.icon);
              return (
                <div className="stat-card" key={t.id}>
                  <div className="stat-card-top"><span className="stat-label">{t.label}</span><Icon size={17} /></div>
                  <div className="stat-value-row"><strong>{t.module_count}</strong><span>módulos prontos</span></div>
                  <div className="mini-progress"><span style={{ width: `${Math.round((t.module_count / t.target_modules) * 100)}%` }} /></div>
                  <p>{t.description}</p>
                </div>
              );
            })}
          </section>

          <section className="section-block" id="catalogo">
            <div className="section-heading">
              <div>
                <div className="eyebrow">EXPLORE SEU POTENCIAL</div>
                <h2>Trilhas para ir além</h2>
              </div>
            </div>
            <div className="track-cards">
              {tracks.map((track) => {
                const Icon = getIcon(track.icon);
                const isActive = activeTrack === track.id;
                return (
                  <button key={track.id} className={`track-card track-card--${track.color} ${isActive ? "is-selected" : ""}`} onClick={() => { setActiveTrack(track.id); setActiveView("catalogo"); }}>
                    <div className="track-card-head"><span className="track-card-icon"><Icon size={20} /></span><span className="track-card-arrow"><ArrowRight size={15} /></span></div>
                    <div className="track-card-eyebrow">{track.eyebrow}</div>
                    <h3>{track.label}</h3>
                    <p>{track.description}</p>
                    <div className="track-card-foot"><span>{track.module_count} módulos</span><span className="track-progress-line"><i style={{ width: `${Math.round((track.module_count / track.target_modules) * 100)}%` }} /></span></div>
                  </button>
                );
              })}
            </div>
          </section>

          <section className="section-block module-section">
            <div className="section-heading section-heading--modules">
              <div>
                <div className="eyebrow"><span className="eyebrow-dot eyebrow-dot--blue" /> {activeTrackData?.label?.toUpperCase() || "MÓDULOS"}</div>
                <h2>Módulos disponíveis</h2>
              </div>
              <div className="module-tools">
                <div className="search-box"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar módulo" aria-label="Buscar módulo" /></div>
              </div>
            </div>
            <div className="module-list">
              {modules.map((mod) => {
                const Icon = getIcon(mod.icon);
                return (
                  <article className="module-row" key={mod.id} onClick={() => handleModuleOpen(mod)}>
                    <div className={`module-icon module-icon--${mod.accent}`}><Icon size={20} /></div>
                    <div className="module-info">
                      <div className="module-title-row">
                        <h3>{mod.title}</h3>
                        {mod.featured && <span className="small-tag"><Star size={11} fill="currentColor" /> recomendado</span>}
                      </div>
                      <p>{mod.subtitle}</p>
                      <div className="module-details">
                        <span>{mod.level}</span>
                        <span className="detail-separator" />
                        <span><Clock3 size={13} /> {mod.duration_min} min</span>
                      </div>
                    </div>
                    <button className="module-play" aria-label={`Abrir ${mod.title}`} onClick={(e) => { e.stopPropagation(); handleModuleOpen(mod); }}><Play size={15} fill="currentColor" /></button>
                  </article>
                );
              })}
              {modules.length === 0 && (
                <div className="empty-state"><Search size={22} /><strong>Nenhum módulo encontrado</strong><span>Tente buscar por outra palavra ou troque de trilha.</span></div>
              )}
            </div>
          </section>

          <section className="agenda-section" id="agenda">
            <div className="agenda-copy">
              <div className="eyebrow">PARA MANTER O RITMO</div>
              <h2>Seu próximo pequeno passo</h2>
              <p>Uma sessão curta hoje mantém seu cérebro aquecido e sua curiosidade em movimento.</p>
              <button className="secondary-button" onClick={() => toast.success("Sessão adicionada", { description: "Sua próxima sessão de estudo está marcada." })}><Plus size={16} /> Adicionar sessão</button>
            </div>
            <div className="agenda-days">
              <div className="agenda-week-label">ESTA SEMANA</div>
              <div className="agenda-day-grid">
                {weekActivity.map((item, i) => (
                  <button key={item.day} className={`agenda-day ${i === 3 ? "is-today" : ""}`} onClick={() => toast(i === 3 ? "Hoje é um ótimo dia para começar." : `${item.day}: sessão livre`)}>
                    <span>{item.day}</span>
                    <strong>{String(i + 15).padStart(2, "0")}</strong>
                    <i className={i < 4 ? "is-done" : ""} />
                  </button>
                ))}
              </div>
            </div>
          </section>

          <footer className="footer">
            <span>aprende<span className="footer-period">.</span> Brasil</span>
            <span>Aprender é uma prática diária.</span>
            <span className="footer-links">
              <button onClick={() => toast("Privacidade", { description: "Sua jornada pertence a você." })}>Privacidade</button>
              <button onClick={() => toast("Ajuda", { description: "O tutor Nilo está sempre disponível." })}>Ajuda</button>
            </span>
          </footer>
        </div>
      </main>

      <button className={`tutor-fab ${isTutorOpen ? "is-open" : ""}`} onClick={() => setIsTutorOpen((o) => !o)} aria-label="Abrir tutor Nilo">
        <span className="tutor-fab-pulse" /><MessageCircle size={20} /><span>Nilo</span>
      </button>

      {isTutorOpen && (
        <section className="tutor-panel" aria-label="Tutor Nilo">
          <div className="tutor-panel-head">
            <div className="tutor-avatar"><BrainCircuit size={19} /></div>
            <div><strong>Nilo, seu tutor</strong><span>Aprendizagem com curiosidade</span></div>
            <button onClick={() => setIsTutorOpen(false)} aria-label="Fechar tutor"><X size={18} /></button>
          </div>
          <div className="tutor-suggestion-row">
            <button onClick={() => setMessageInput("Explique este tema de um jeito simples")}>Explicar simples</button>
            <button onClick={() => setMessageInput("Crie um exercício rápido")}>Criar exercício</button>
          </div>
          <div className="tutor-messages">
            {messages.map((msg, i) => (
              <div className={`tutor-message tutor-message--${msg.role}`} key={i}>
                <span>{msg.text}</span>
                {msg.role === "assistant" && (
                  <button className="speak-button" onClick={() => speakText(msg.text)} aria-label="Ouvir resposta"><Volume2 size={13} /></button>
                )}
              </div>
            ))}
            {tutorLoading && <div className="tutor-message tutor-message--assistant tutor-message--typing"><span /><span /><span /></div>}
          </div>
          <form className="tutor-input-row" onSubmit={handleTutorSubmit}>
            <input value={messageInput} onChange={(e) => setMessageInput(e.target.value)} placeholder="Escreva sua dúvida..." aria-label="Mensagem para o tutor" />
            <button type="button" className={voiceActive ? "is-speaking" : ""} onClick={() => speakText("Olá! Estou pronto para ajudar você a aprender.")} aria-label="Testar voz"><Mic2 size={17} /></button>
            <button type="submit" aria-label="Enviar mensagem"><ArrowRight size={17} /></button>
          </form>
          <div className="tutor-voice-note"><Headphones size={13} /> Voz em pt-BR disponível.</div>
        </section>
      )}

      {selectedModule && (
        <div className="modal-backdrop" onClick={() => setSelectedModule(null)}>
          <section className="module-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedModule(null)} aria-label="Fechar módulo"><X size={18} /></button>
            <div className={`modal-icon modal-icon--${selectedModule.accent}`}>
              {(() => { const I = getIcon(selectedModule.icon); return <I size={26} />; })()}
            </div>
            <div className="eyebrow">{selectedModule.level} · {selectedModule.duration_min} min</div>
            <h2>{selectedModule.title}</h2>
            <p>{selectedModule.subtitle}</p>
            <div className="modal-next-step">
              <span className="modal-check"><Check size={14} /></span>
              <div><strong>Próxima etapa</strong><p>Conhecer o conceito em 3 minutos</p></div>
            </div>
            <button className="primary-button primary-button--full" onClick={() => handlePlay(selectedModule)}><Play size={16} fill="currentColor" /> Começar módulo</button>
            <button className="modal-tutor-link" onClick={() => { setSelectedModule(null); setIsTutorOpen(true); }}>Tirar uma dúvida com Nilo <ArrowRight size={14} /></button>
          </section>
        </div>
      )}
    </div>
  );
}
