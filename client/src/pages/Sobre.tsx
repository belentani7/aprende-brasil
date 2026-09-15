import { ArrowRight, BookOpen, Code2, BarChart3, Languages, Users, Globe, Shield, Heart, Sparkles } from "lucide-react";
import { Link } from "wouter";

export default function Sobre() {
  return (
    <div className="sobre-page">
      <header className="sobre-header">
        <div className="sobre-header-inner">
          <div className="brand-lockup">
            <div className="brand-mark"><Sparkles size={19} fill="currentColor" /></div>
            <div>
              <div className="brand-name">aprende<span>.</span></div>
              <div className="brand-subtitle">Brasil</div>
            </div>
          </div>
          <Link href="/" className="primary-button">Entrar na plataforma <ArrowRight size={16} /></Link>
        </div>
      </header>

      <section className="sobre-hero">
        <div className="sobre-hero-inner">
          <h1>Alfabetização e educação digital<br />para quem não teve acesso.</h1>
          <p className="sobre-hero-sub">
            Uma plataforma gratuita e aberta com conteúdo real de alfabetização, informática, matemática e idiomas.
            Projetada para ser usada por qualquer pessoa, organização ou comunidade que queira ensinar.
          </p>
          <div className="sobre-hero-actions">
            <Link href="/" className="primary-button primary-button--large">Começar a aprender <ArrowRight size={16} /></Link>
            <a href="#como-funciona" className="secondary-button">Como funciona</a>
          </div>
        </div>
      </section>

      <section className="sobre-stats">
        <div className="sobre-stats-inner">
          <div className="sobre-stat"><strong>71+</strong><span>módulos prontos</span></div>
          <div className="sobre-stat"><strong>4</strong><span>trilhas educativas</span></div>
          <div className="sobre-stat"><strong>355</strong><span>etapas pedagógicas</span></div>
          <div className="sobre-stat"><strong>100%</strong><span>gratuito e aberto</span></div>
        </div>
      </section>

      <section className="sobre-section" id="como-funciona">
        <h2>O que oferecemos</h2>
        <p className="sobre-section-sub">Conteúdo estruturado e progressivo, do primeiro contato com as letras até a autonomia digital.</p>
        <div className="sobre-cards">
          <div className="sobre-card sobre-card--orange">
            <BookOpen size={28} />
            <h3>Alfabetização</h3>
            <p>Das vogais às primeiras frases. Ler e escrever o próprio nome, bilhetes, listas, receitas e documentos. Conteúdo para crianças e adultos.</p>
            <span>30 módulos · 5 níveis</span>
          </div>
          <div className="sobre-card sobre-card--blue">
            <Code2 size={28} />
            <h3>Informática</h3>
            <p>Do primeiro clique ao currículo digital. Usar celular, internet, e-mail, WhatsApp, Pix e reconhecer golpes online.</p>
            <span>15 módulos · do básico ao prático</span>
          </div>
          <div className="sobre-card sobre-card--violet">
            <BarChart3 size={28} />
            <h3>Matemática</h3>
            <p>Contar, somar, medir, calcular troco, ler gráficos e usar porcentagem. Matemática para a vida real.</p>
            <span>14 módulos · numeração à análise</span>
          </div>
          <div className="sobre-card sobre-card--green">
            <Languages size={28} />
            <h3>Idiomas</h3>
            <p>Inglês e espanhol do zero. Cumprimentos, apresentações, situações do dia a dia e preparação para entrevistas.</p>
            <span>12 módulos · A1 a comunicação profissional</span>
          </div>
        </div>
      </section>

      <section className="sobre-section sobre-section--alt">
        <h2>Para organizações e educadores</h2>
        <p className="sobre-section-sub">Tudo que você precisa para montar uma instituição educativa mínima com conteúdo completo.</p>
        <div className="sobre-features">
          <div className="sobre-feature">
            <Users size={22} />
            <div>
              <h4>Pronto para usar</h4>
              <p>Instale em qualquer servidor ou computador. Nenhuma configuração complexa — SQLite, Python e um navegador.</p>
            </div>
          </div>
          <div className="sobre-feature">
            <Globe size={22} />
            <div>
              <h4>100% em português brasileiro</h4>
              <p>Todo o conteúdo, interface e tutor em pt-BR. Pensado para o contexto social e cultural do Brasil.</p>
            </div>
          </div>
          <div className="sobre-feature">
            <Shield size={22} />
            <div>
              <h4>Dados abertos e verificáveis</h4>
              <p>Conteúdo baseado em fontes abertas: IBGE, Wiktionary, Project Gutenberg, Wikipedia. Sem custos de licença.</p>
            </div>
          </div>
          <div className="sobre-feature">
            <Heart size={22} />
            <div>
              <h4>Pedagogia primeiro</h4>
              <p>Cada módulo segue: objetivo → explicação → exemplo → prática → verificação → próximo passo. Sem paredes de texto.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="sobre-section">
        <h2>Como começar</h2>
        <div className="sobre-steps">
          <div className="sobre-step">
            <span className="sobre-step-num">1</span>
            <h4>Instale</h4>
            <p>Clone o repositório, instale Python e rode <code>pip install -r requirements.txt</code>.</p>
          </div>
          <div className="sobre-step">
            <span className="sobre-step-num">2</span>
            <h4>Popule o conteúdo</h4>
            <p>Rode <code>pnpm seed</code> para baixar o banco aberto e gerar os 205 módulos educativos.</p>
          </div>
          <div className="sobre-step">
            <span className="sobre-step-num">3</span>
            <h4>Inicie o servidor</h4>
            <p>Rode <code>uvicorn api.main:app</code> e acesse no navegador.</p>
          </div>
          <div className="sobre-step">
            <span className="sobre-step-num">4</span>
            <h4>Ensine</h4>
            <p>Compartilhe o endereço com seus alunos. É só acessar e começar.</p>
          </div>
        </div>
      </section>

      <section className="sobre-cta">
        <h2>Educação é um direito.<br />Vamos torná-la acessível.</h2>
        <Link href="/" className="primary-button primary-button--large">Acessar a plataforma <ArrowRight size={16} /></Link>
      </section>

      <footer className="sobre-footer">
        <span>aprende<span className="footer-period">.</span> Brasil</span>
        <span>Projeto aberto · Código livre · MIT License</span>
        <span>Fontes: IBGE · Wiktionary · Project Gutenberg · Wikipedia · Tatoeba</span>
      </footer>
    </div>
  );
}
