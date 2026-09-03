import { useMemo, useState } from "react";
import { startLogin } from "@/const";
import { trpc } from "@/lib/trpc";
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
  Compass,
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

type TrackId = "informatica" | "matematica" | "idiomas";
type ViewId = "inicio" | "catalogo" | "agenda";
type TutorMessage = { role: "assistant" | "user"; text: string };

type Module = {
  id: string;
  track: TrackId;
  title: string;
  subtitle: string;
  level: string;
  duration: string;
  progress: number;
  accent: string;
  icon: typeof Code2;
  featured?: boolean;
};

const tracks = [
  {
    id: "informatica" as TrackId,
    label: "Informática",
    eyebrow: "Pensamento digital",
    description: "Do primeiro algoritmo à criação de produtos digitais.",
    modules: "680 módulos",
    color: "orange",
    icon: Code2,
  },
  {
    id: "matematica" as TrackId,
    label: "Matemática",
    eyebrow: "Raciocínio aplicado",
    description: "Aprenda a pensar com clareza, padrões e problemas reais.",
    modules: "720 módulos",
    color: "blue",
    icon: BarChart3,
  },
  {
    id: "idiomas" as TrackId,
    label: "Idiomas",
    eyebrow: "Comunicação global",
    description: "Pratique inglês, espanhol e português no seu ritmo.",
    modules: "600 módulos",
    color: "green",
    icon: Languages,
  },
];

const modules: Module[] = [
  {
    id: "algoritmos-01",
    track: "informatica",
    title: "Pensamento computacional",
    subtitle: "Como transformar curiosidade em passos executáveis.",
    level: "Começo",
    duration: "18 min",
    progress: 72,
    accent: "orange",
    icon: Code2,
    featured: true,
  },
  {
    id: "dados-01",
    track: "informatica",
    title: "Dados que contam histórias",
    subtitle: "Leitura de tabelas, gráficos e decisões melhores.",
    level: "Essencial",
    duration: "24 min",
    progress: 18,
    accent: "violet",
    icon: BarChart3,
  },
  {
    id: "web-01",
    track: "informatica",
    title: "Sua primeira página web",
    subtitle: "HTML, CSS e a alegria de publicar algo seu.",
    level: "Prática",
    duration: "32 min",
    progress: 0,
    accent: "blue",
    icon: LayoutGrid,
  },
  {
    id: "algebra-01",
    track: "matematica",
    title: "Álgebra sem mistério",
    subtitle: "Variáveis como ferramentas para enxergar relações.",
    level: "Começo",
    duration: "21 min",
    progress: 45,
    accent: "blue",
    icon: BarChart3,
    featured: true,
  },
  {
    id: "probabilidade-01",
    track: "matematica",
    title: "Decisões sob incerteza",
    subtitle: "Probabilidade para interpretar o mundo real.",
    level: "Intermediário",
    duration: "27 min",
    progress: 0,
    accent: "orange",
    icon: Target,
  },
  {
    id: "ingles-01",
    track: "idiomas",
    title: "Conversas do dia a dia",
    subtitle: "Apresente-se, faça perguntas e ganhe confiança.",
    level: "A1 · Iniciante",
    duration: "16 min",
    progress: 88,
    accent: "green",
    icon: Languages,
    featured: true,
  },
  {
    id: "espanhol-01",
    track: "idiomas",
    title: "Falsos amigos, grandes descobertas",
    subtitle: "Aproxime português e espanhol sem cair em armadilhas.",
    level: "A2 · Básico",
    duration: "19 min",
    progress: 0,
    accent: "violet",
    icon: MessageCircle,
  },
];

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
    role: "assistant" as const,
    text: "Oi, Isa! Sou o Nilo, seu tutor de aprendizagem. Posso explicar um conceito, criar um exercício ou montar uma revisão rápida.",
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

function TrackIcon({ track }: { track: TrackId }) {
  const Icon = tracks.find((item) => item.id === track)?.icon ?? Code2;
  return <Icon size={18} strokeWidth={2.2} />;
}

export default function Home() {
  const [activeTrack, setActiveTrack] = useState<TrackId>("informatica");
  const [activeView, setActiveView] = useState<ViewId>("inicio");
  const [search, setSearch] = useState("");
  const [selectedModule, setSelectedModule] = useState<Module | null>(null);
  const [isTutorOpen, setIsTutorOpen] = useState(false);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [messages, setMessages] = useState<TutorMessage[]>(initialMessages);
  const [messageInput, setMessageInput] = useState("");
  const [voiceActive, setVoiceActive] = useState(false);

  const tutorMutation = trpc.tutor.ask.useMutation({
    onSuccess: (data) => {
      setMessages((current) => [...current, { role: "assistant", text: data.answer }]);
    },
    onError: () => {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: "Tive um pequeno problema para pensar agora. Enquanto isso, tente explicar o conceito com suas próprias palavras — essa é uma ótima forma de aprender.",
        },
      ]);
    },
  });

  const visibleModules = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();
    return modules.filter((module) => {
      const matchesTrack = module.track === activeTrack;
      const matchesSearch = !normalizedSearch || `${module.title} ${module.subtitle}`.toLowerCase().includes(normalizedSearch);
      return matchesTrack && matchesSearch;
    });
  }, [activeTrack, search]);

  const handleModuleOpen = (module: Module) => {
    setSelectedModule(module);
    toast.success("Módulo aberto", { description: `${module.title} está pronto para você continuar.` });
  };

  const handlePlay = (module: Module) => {
    setSelectedModule(null);
    toast.success("Aula iniciada", { description: "Seu progresso será salvo a cada etapa." });
    if (module.progress === 0) {
      setTimeout(() => toast("Primeiro passo", { description: "Comece com a atividade guiada de 3 minutos." }), 450);
    }
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

  const handleTutorSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = messageInput.trim();
    if (!trimmed || tutorMutation.isPending) return;
    setMessages((current) => [...current, { role: "user", text: trimmed }]);
    setMessageInput("");
    tutorMutation.mutate({ message: trimmed, subject: activeTrack });
  };

  const updateView = (view: ViewId) => {
    setActiveView(view);
    setIsMobileNavOpen(false);
    if (view === "catalogo") document.getElementById("catalogo")?.scrollIntoView({ behavior: "smooth" });
    if (view === "agenda") document.getElementById("agenda")?.scrollIntoView({ behavior: "smooth" });
    if (view === "inicio") window.scrollTo({ top: 0, behavior: "smooth" });
  };

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
            <BookOpen size={18} /> <span>Catálogo</span><span className="nav-count">2.000</span>
          </button>
          <button className={`sidebar-link ${activeView === "agenda" ? "is-active" : ""}`} onClick={() => updateView("agenda")}>
            <Clock3 size={18} /> <span>Minha agenda</span>
          </button>
        </nav>

        <div className="sidebar-section-label sidebar-section-label--space">Trilhas</div>
        <div className="track-nav">
          {tracks.map((track) => {
            const Icon = track.icon;
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
        <div className="sidebar-profile">
          <div className="avatar avatar--small">IS</div>
          <div className="profile-copy"><strong>Isadora Silva</strong><span>Nível exploradora</span></div>
          <ChevronDown size={15} className="muted-icon" />
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button className="mobile-menu-button" aria-label="Abrir menu" onClick={() => setIsMobileNavOpen((open) => !open)}><Menu size={20} /></button>
          <div className="breadcrumb"><span>Espaço de aprendizagem</span><span className="breadcrumb-slash">/</span><strong>{activeView === "inicio" ? "Visão geral" : activeView === "catalogo" ? "Catálogo" : "Minha agenda"}</strong></div>
          <div className="topbar-actions">
            <button className="topbar-icon-button" aria-label="Ajuda" onClick={() => toast("Como podemos ajudar?", { description: "Abra o tutor Nilo para tirar dúvidas em qualquer módulo." })}><CircleHelp size={18} /></button>
            <button className="login-button" onClick={() => startLogin()}>Entrar <ArrowRight size={15} /></button>
          </div>
        </header>

        <div className="content-wrap">
          <section className="welcome-row" id="inicio">
            <div>
              <div className="eyebrow"><span className="eyebrow-dot" /> QUINTA-FEIRA, 03 DE SETEMBRO</div>
              <h1>Olá, Isadora<span className="headline-period">.</span></h1>
              <p className="welcome-note">Vamos dar mais um passo no que importa para você.</p>
            </div>
            <div className="streak-chip"><span className="streak-flame">✦</span><div><strong>7 dias</strong><span>de sequência</span></div><Trophy size={18} /></div>
          </section>

          <section className="hero-card">
            <div className="hero-copy">
              <div className="hero-kicker"><span className="live-dot" /> RECOMENDADO PARA HOJE</div>
              <h2>Você está mais perto<br />do que imagina.</h2>
              <p>Continue sua jornada em <strong>Pensamento computacional</strong> e complete a próxima etapa.</p>
              <button className="primary-button" onClick={() => handleModuleOpen(modules[0])}>Continuar aprendendo <ArrowRight size={16} /></button>
              <div className="hero-meta"><span><Clock3 size={14} /> 18 min restantes</span><span><Target size={14} /> Meta do dia: 20 min</span></div>
            </div>
            <div className="hero-visual" aria-hidden="true">
              <div className="hero-grid" />
              <div className="hero-sun" />
              <div className="hero-planet hero-planet--large" />
              <div className="hero-planet hero-planet--small" />
              <div className="hero-card-note hero-card-note--top"><span>72%</span><small>progresso</small></div>
              <div className="hero-card-note hero-card-note--bottom"><span>+</span><small>curiosidade</small></div>
            </div>
          </section>

          <section className="stat-grid">
            <div className="stat-card stat-card--progress"><div className="stat-card-top"><span className="stat-label">Progresso geral</span><BarChart3 size={17} /></div><div className="stat-value-row"><strong>34%</strong><span>+8% esta semana</span></div><div className="mini-progress"><span style={{ width: "34%" }} /></div><p>Você completou 68 de 200 módulos do seu plano atual.</p></div>
            <div className="stat-card"><div className="stat-card-top"><span className="stat-label">Tempo de estudo</span><Clock3 size={17} /></div><div className="stat-value-row"><strong>4h 20</strong><span>minutos</span></div><div className="activity-bars">{weekActivity.map((item) => <div className="activity-bar-wrap" key={item.day}><div className="activity-bar" style={{ height: `${item.value}%` }} /><span>{item.day}</span></div>)}</div></div>
            <div className="stat-card stat-card--goal"><div className="stat-card-top"><span className="stat-label">Meta semanal</span><Target size={17} /></div><div className="goal-row"><ProgressRing value={68} /><div><strong>4 de 6</strong><p>sessões concluídas</p><button onClick={() => updateView("agenda")}>Ver agenda <ArrowRight size={13} /></button></div></div></div>
          </section>

          <section className="section-block" id="catalogo">
            <div className="section-heading"><div><div className="eyebrow">EXPLORE SEU POTENCIAL</div><h2>Trilhas para ir além</h2></div><button className="text-button" onClick={() => { setSearch(""); setActiveView("catalogo"); toast("Catálogo completo", { description: "Explore os módulos por trilha e nível." }); }}>Ver todos <ArrowRight size={14} /></button></div>
            <div className="track-cards">
              {tracks.map((track) => {
                const Icon = track.icon;
                const isActive = activeTrack === track.id;
                return <button key={track.id} className={`track-card track-card--${track.color} ${isActive ? "is-selected" : ""}`} onClick={() => { setActiveTrack(track.id); setActiveView("catalogo"); }}><div className="track-card-head"><span className="track-card-icon"><Icon size={20} /></span><span className="track-card-arrow"><ArrowRight size={15} /></span></div><div className="track-card-eyebrow">{track.eyebrow}</div><h3>{track.label}</h3><p>{track.description}</p><div className="track-card-foot"><span>{track.modules}</span><span className="track-progress-line"><i style={{ width: track.id === "informatica" ? "42%" : track.id === "matematica" ? "28%" : "56%" }} /></span></div></button>;
              })}
            </div>
          </section>

          <section className="section-block module-section">
            <div className="section-heading section-heading--modules"><div><div className="eyebrow"><span className="eyebrow-dot eyebrow-dot--blue" /> CONTINUE DE ONDE PAROU</div><h2>Módulos em destaque</h2></div><div className="module-tools"><div className="search-box"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar módulo" aria-label="Buscar módulo" /></div><button className="filter-button" onClick={() => toast("Filtros em breve", { description: "Estamos preparando filtros por nível, duração e formato." })}>Filtros <ChevronDown size={15} /></button></div></div>
            <div className="module-list">
              {visibleModules.map((module) => { const Icon = module.icon; return <article className="module-row" key={module.id} onClick={() => handleModuleOpen(module)}><div className={`module-icon module-icon--${module.accent}`}><Icon size={20} /></div><div className="module-info"><div className="module-title-row"><h3>{module.title}</h3>{module.featured && <span className="small-tag"><Star size={11} fill="currentColor" /> recomendado</span>}</div><p>{module.subtitle}</p><div className="module-details"><span>{module.level}</span><span className="detail-separator" /> <span><Clock3 size={13} /> {module.duration}</span></div></div><div className="module-progress"><div className="module-progress-head"><span>{module.progress === 0 ? "Ainda não iniciado" : `${module.progress}% concluído`}</span>{module.progress > 0 && <Check size={15} />}</div><div className="mini-progress"><span style={{ width: `${module.progress}%` }} /></div></div><button className="module-play" aria-label={`Abrir ${module.title}`} onClick={(event) => { event.stopPropagation(); handleModuleOpen(module); }}><Play size={15} fill="currentColor" /></button></article>; })}
              {visibleModules.length === 0 && <div className="empty-state"><Search size={22} /><strong>Nenhum módulo encontrado</strong><span>Tente buscar por outra palavra ou troque de trilha.</span></div>}
            </div>
          </section>

          <section className="agenda-section" id="agenda">
            <div className="agenda-copy"><div className="eyebrow">PARA MANTER O RITMO</div><h2>Seu próximo pequeno passo</h2><p>Uma sessão curta hoje mantém seu cérebro aquecido e sua curiosidade em movimento.</p><button className="secondary-button" onClick={() => toast.success("Sessão adicionada", { description: "Amanhã, às 18h30, no seu calendário de estudo." })}><Plus size={16} /> Adicionar sessão</button></div>
            <div className="agenda-days"><div className="agenda-week-label">ESTA SEMANA <span>03 — 09 SET</span></div><div className="agenda-day-grid">{weekActivity.map((item, index) => <button key={item.day} className={`agenda-day ${index === 3 ? "is-today" : ""}`} onClick={() => toast(item.day === "QUI" ? "Hoje é um ótimo dia para começar." : `${item.day}: sessão livre`, { description: "Escolha um módulo e avance no seu ritmo." })}><span>{item.day}</span><strong>{index === 3 ? "03" : String(index + 30).padStart(2, "0")}</strong><i className={index < 4 ? "is-done" : ""} /></button>)}</div></div>
          </section>

          <footer className="footer"><span>aprende<span className="footer-period">.</span> Brasil</span><span>Aprender é uma prática diária.</span><span className="footer-links"><button onClick={() => toast("Privacidade", { description: "Sua jornada pertence a você." })}>Privacidade</button><button onClick={() => toast("Ajuda", { description: "O tutor Nilo está sempre disponível." })}>Ajuda</button></span></footer>
        </div>
      </main>

      <button className={`tutor-fab ${isTutorOpen ? "is-open" : ""}`} onClick={() => setIsTutorOpen((open) => !open)} aria-label="Abrir tutor Nilo"><span className="tutor-fab-pulse" /><MessageCircle size={20} /><span>Nilo</span></button>

      {isTutorOpen && <section className="tutor-panel" aria-label="Tutor Nilo"><div className="tutor-panel-head"><div className="tutor-avatar"><BrainCircuit size={19} /></div><div><strong>Nilo, seu tutor</strong><span>Aprendizagem com curiosidade</span></div><button onClick={() => setIsTutorOpen(false)} aria-label="Fechar tutor"><X size={18} /></button></div><div className="tutor-suggestion-row"><button onClick={() => setMessageInput("Explique este tema de um jeito simples")}>Explicar simples</button><button onClick={() => setMessageInput("Crie um exercício rápido")}>Criar exercício</button></div><div className="tutor-messages">{messages.map((message, index) => <div className={`tutor-message tutor-message--${message.role}`} key={`${message.role}-${index}`}><span>{message.text}</span>{message.role === "assistant" && <button className="speak-button" onClick={() => speakText(message.text)} aria-label="Ouvir resposta"><Volume2 size={13} /></button>}</div>)}{tutorMutation.isPending && <div className="tutor-message tutor-message--assistant tutor-message--typing"><span /><span /><span /></div>}</div><form className="tutor-input-row" onSubmit={handleTutorSubmit}><input value={messageInput} onChange={(event) => setMessageInput(event.target.value)} placeholder="Escreva sua dúvida..." aria-label="Mensagem para o tutor" /><button type="button" className={voiceActive ? "is-speaking" : ""} onClick={() => speakText("Olá! Estou pronto para ajudar você a aprender.")} aria-label="Testar voz"><Mic2 size={17} /></button><button type="submit" aria-label="Enviar mensagem"><ArrowRight size={17} /></button></form><div className="tutor-voice-note"><Headphones size={13} /> Voz em pt-BR disponível. OpenVoice pronto para conectar.</div></section>}

      {selectedModule && <div className="modal-backdrop" onClick={() => setSelectedModule(null)}><section className="module-modal" onClick={(event) => event.stopPropagation()}><button className="modal-close" onClick={() => setSelectedModule(null)} aria-label="Fechar módulo"><X size={18} /></button><div className={`modal-icon modal-icon--${selectedModule.accent}`}><selectedModule.icon size={26} /></div><div className="eyebrow">{selectedModule.level} · {selectedModule.duration}</div><h2>{selectedModule.title}</h2><p>{selectedModule.subtitle}</p><div className="modal-progress-row"><span>Seu progresso</span><strong>{selectedModule.progress}%</strong></div><div className="mini-progress"><span style={{ width: `${selectedModule.progress}%` }} /></div><div className="modal-next-step"><span className="modal-check"><Check size={14} /></span><div><strong>Próxima etapa</strong><p>{selectedModule.progress > 0 ? "Retomar atividade guiada" : "Conhecer o conceito em 3 minutos"}</p></div></div><button className="primary-button primary-button--full" onClick={() => handlePlay(selectedModule)}><Play size={16} fill="currentColor" /> Começar módulo</button><button className="modal-tutor-link" onClick={() => { setSelectedModule(null); setIsTutorOpen(true); }}>Tirar uma dúvida com Nilo <ArrowRight size={14} /></button></section></div>}
    </div>
  );
}
