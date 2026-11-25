import { ArrowLeft, Compass } from "lucide-react";
import { Link } from "wouter";

export default function NotFound() {
  return (
    <main className="nao-encontrado">
      <div className="nao-encontrado-card">
        <span className="nao-encontrado-icon">
          <Compass size={30} aria-hidden="true" />
        </span>
        <p className="eyebrow">ERRO 404</p>
        <h1>Esta página não existe.</h1>
        <p>
          O endereço pode estar incompleto ou o conteúdo mudou de lugar. O
          catálogo continua no mesmo caminho — e sempre aberto.
        </p>
        <div className="nao-encontrado-actions">
          <Link href="/" className="primary-button">
            <ArrowLeft size={16} aria-hidden="true" /> Voltar ao início
          </Link>
          <Link
            href="/sobre"
            className="secondary-button secondary-button--outline"
          >
            Conhecer o projeto
          </Link>
        </div>
      </div>
    </main>
  );
}
