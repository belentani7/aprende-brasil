import {
  ArrowRight,
  BarChart3,
  BookOpen,
  Code2,
  Globe,
  Heart,
  Languages,
  Shield,
  Sparkles,
  Users,
} from "lucide-react";
import { Link } from "wouter";
import { MODULES, TRACKS } from "@/lib/curriculum";

const TOTAL_STEPS = MODULES.reduce(
  (total, module) => total + (module.step_count ?? 0),
  0
);

const TRACK_ICON = { BookOpen, Code2, BarChart3, Languages } as const;

const TRACK_TEXT: Record<
  string,
  { description: string; icon: keyof typeof TRACK_ICON }
> = {
  alfabetizacao: {
    description:
      "Das vogais às primeiras frases. Ler e escrever o próprio nome, bilhetes, listas, receitas e documentos do dia a dia.",
    icon: "BookOpen",
  },
  informatica: {
    description:
      "Do primeiro clique ao currículo digital. Usar celular, internet, e-mail, mensagens e reconhecer golpes online.",
    icon: "Code2",
  },
  matematica: {
    description:
      "Contar, somar, medir, calcular troco, ler gráficos e usar porcentagem. Matemática para decisões reais.",
    icon: "BarChart3",
  },
  idiomas: {
    description:
      "Inglês e espanhol do zero: cumprimentos, apresentações, situações do dia a dia e preparação para entrevistas.",
    icon: "Languages",
  },
};

export default function Sobre() {
  return (
    <div className="sobre-page">
      <header className="sobre-header">
        <div className="sobre-header-inner">
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
          <Link href="/" className="primary-button">
            Entrar na plataforma <ArrowRight size={16} />
          </Link>
        </div>
      </header>

      <main>
        <section className="sobre-hero" aria-labelledby="sobre-titulo">
          <div className="sobre-hero-inner">
            <p className="eyebrow">EDUCAÇÃO ABERTA · PT-BR</p>
            <h1 id="sobre-titulo">
              Alfabetização e educação digital
              <br />
              para quem não teve acesso.
            </h1>
            <p className="sobre-hero-sub">
              Uma plataforma gratuita e aberta com conteúdo real de
              alfabetização, informática, matemática e idiomas. Projetada para
              ser usada por qualquer pessoa, organização ou comunidade que
              queira ensinar — sem matrícula e sem pedir dados pessoais.
            </p>
            <div className="sobre-hero-actions">
              <Link href="/" className="primary-button primary-button--large">
                Começar a aprender <ArrowRight size={16} />
              </Link>
              <a
                href="#como-funciona"
                className="secondary-button secondary-button--outline"
              >
                Como funciona
              </a>
            </div>
          </div>
        </section>

        <section className="sobre-stats" aria-label="Números do projeto">
          <div className="sobre-stats-inner">
            <div className="sobre-stat">
              <strong>{MODULES.length}</strong>
              <span>módulos prontos</span>
            </div>
            <div className="sobre-stat">
              <strong>{TRACKS.length}</strong>
              <span>trilhas educativas</span>
            </div>
            <div className="sobre-stat">
              <strong>{TOTAL_STEPS}</strong>
              <span>etapas pedagógicas</span>
            </div>
            <div className="sobre-stat">
              <strong>100%</strong>
              <span>gratuito e aberto</span>
            </div>
          </div>
        </section>

        <section
          className="sobre-section"
          id="como-funciona"
          aria-labelledby="oferecemos"
        >
          <h2 id="oferecemos">O que oferecemos</h2>
          <p className="sobre-section-sub">
            Conteúdo estruturado e progressivo, do primeiro contato com as
            letras até a autonomia digital. Cada módulo tem cinco etapas:
            entender, ver um exemplo, praticar, verificar e seguir adiante.
          </p>
          <div className="sobre-cards">
            {TRACKS.map(track => {
              const Icon = TRACK_ICON[TRACK_TEXT[track.id]?.icon ?? "BookOpen"];
              const text = TRACK_TEXT[track.id];
              return (
                <div
                  className={`sobre-card sobre-card--${track.color}`}
                  key={track.id}
                >
                  <Icon size={28} aria-hidden="true" />
                  <h3>{track.label}</h3>
                  <p>{text?.description ?? track.description}</p>
                  <span>{track.module_count} módulos · 5 etapas cada</span>
                </div>
              );
            })}
          </div>
        </section>

        <section
          className="sobre-section sobre-section--alt"
          aria-labelledby="organizacoes"
        >
          <h2 id="organizacoes">Para organizações e educadores</h2>
          <p className="sobre-section-sub">
            Tudo o que você precisa para montar uma instituição educativa mínima
            com conteúdo completo.
          </p>
          <div className="sobre-features">
            <div className="sobre-feature">
              <Users size={22} aria-hidden="true" />
              <div>
                <h3>Pronto para usar</h3>
                <p>
                  O site é estático: qualquer hospedagem de arquivos serve. O
                  backend FastAPI existe apenas para desenvolvimento e para o
                  tutor com LLM.
                </p>
              </div>
            </div>
            <div className="sobre-feature">
              <Globe size={22} aria-hidden="true" />
              <div>
                <h3>100% em português brasileiro</h3>
                <p>
                  Todo o conteúdo, a interface e o tutor em pt-BR. Pensado para
                  o contexto social e cultural do Brasil, com leitura em voz
                  alta no navegador.
                </p>
              </div>
            </div>
            <div className="sobre-feature">
              <Shield size={22} aria-hidden="true" />
              <div>
                <h3>Sem coleta de dados</h3>
                <p>
                  O progresso e os favoritos ficam no <code>localStorage</code>{" "}
                  do seu navegador. Não há cadastro, login, cookies de
                  rastreamento ou publicidade.
                </p>
              </div>
            </div>
            <div className="sobre-feature">
              <Heart size={22} aria-hidden="true" />
              <div>
                <h3>Pedagogia primeiro</h3>
                <p>
                  Cada módulo segue a mesma sequência: objetivo → explicação →
                  exemplo → prática → verificação → próximo passo.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="sobre-section" aria-labelledby="comecar">
          <h2 id="comecar">Como rodar o projeto</h2>
          <div className="sobre-steps">
            <div className="sobre-step">
              <span className="sobre-step-num">1</span>
              <h3>Instale</h3>
              <p>
                Clone o repositório e rode <code>npm install</code>. O currículo
                já vem no repositório em <code>data/aprende.db</code>.
              </p>
            </div>
            <div className="sobre-step">
              <span className="sobre-step-num">2</span>
              <h3>Gere os dados</h3>
              <p>
                O comando <code>npm run build</code> exporta o currículo para
                JSON e compila o site em <code>dist/public</code>.
              </p>
            </div>
            <div className="sobre-step">
              <span className="sobre-step-num">3</span>
              <h3>Desenvolva</h3>
              <p>
                Use <code>npm run dev</code> para o site em <code>:5173</code> e{" "}
                <code>npm run dev:api</code> para a API opcional em{" "}
                <code>:8000</code>.
              </p>
            </div>
            <div className="sobre-step">
              <span className="sobre-step-num">4</span>
              <h3>Ensine</h3>
              <p>
                Publique a pasta <code>dist/public</code> em qualquer host
                estático e compartilhe o endereço. Sem cadastro para começar.
              </p>
            </div>
          </div>
        </section>

        <section className="sobre-cta" aria-labelledby="cta-titulo">
          <h2 id="cta-titulo">
            Educação é um direito.
            <br />
            Vamos torná-la acessível.
          </h2>
          <Link href="/" className="primary-button primary-button--large">
            Acessar a plataforma <ArrowRight size={16} />
          </Link>
        </section>
      </main>

      <footer className="sobre-footer">
        <span>
          aprende<span className="footer-period">.</span> Brasil
        </span>
        <span>Projeto aberto · Código livre · MIT License</span>
        <span>
          Conteúdo próprio, escrito e revisado para o contexto brasileiro.
        </span>
      </footer>
    </div>
  );
}
