#!/usr/bin/env python3
"""Gera o currículo da Aprende Brasil (205 módulos) e popula o SQLite.

- Alfabetização: usa o banco de palavras aberto (data/open/palavras-pt.txt).
- Informática / Matemática / Idiomas: conteúdo pedagógico real, curado em
  scripts/content_*.py (5 etapas por módulo, sem placeholders).

Rodar: python -m scripts.build_curriculum
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.database import Base, SessionLocal, engine  # noqa: E402
from api.models import Module, ModuleStep, Track  # noqa: E402
from scripts.content_idiomas import IDIOMAS  # noqa: E402
from scripts.content_informatica import INFORMATICA  # noqa: E402
from scripts.content_matematica import MATEMATICA  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WORDS_FILE = ROOT / "data" / "open" / "palavras-pt.txt"

TRACKS = {
    "alfabetizacao": ("Alfabetização", "Ler e escrever", "Primeiros passos na leitura e escrita em português brasileiro.", "orange", "BookOpen"),
    "informatica": ("Informática", "Pensamento digital", "Do primeiro clique à criação de projetos digitais.", "blue", "Code2"),
    "matematica": ("Matemática", "Raciocínio aplicado", "Números, formas e decisões para a vida real.", "violet", "BarChart3"),
    "idiomas": ("Idiomas", "Comunicação global", "Pratique inglês, espanhol e português no seu ritmo.", "green", "Languages"),
}

ALFABETO = "abcdefghijklmnopqrstuvwxyz"
CONSOANTES = "bcdfghjklmnpqrstvwxyz"
VOGAIS = "aeiou"


def load_words() -> list[str]:
    if WORDS_FILE.exists():
        return [w.strip() for w in WORDS_FILE.read_text(encoding="utf-8").splitlines() if w.strip()]
    return []


WORDS = load_words()


def _has_weird(word: str) -> bool:
    allowed = set("abcdefghijklmnopqrstuvwxyzàáâãçéêíóôõúü")
    return any(ch not in allowed for ch in word)


CLEAN = [w for w in WORDS if not _has_weird(w)]


def by_prefix(letter: str, max_len: int = 8, limit: int = 8) -> list[str]:
    out = []
    for w in CLEAN:
        if w.startswith(letter) and 2 <= len(w) <= max_len:
            out.append(w)
            if len(out) >= limit:
                break
    return out


def by_len(min_len: int, max_len: int, limit: int = 8) -> list[str]:
    out = []
    for w in CLEAN:
        if min_len <= len(w) <= max_len:
            out.append(w)
            if len(out) >= limit:
                break
    return out


def steps(*rows) -> list[tuple[str, str, str]]:
    """Cada row: (tipo, título, texto)."""
    return list(rows)


def add(db, mid, track, title, subtitle, level, order, duration, featured, step_rows):
    if db.get(Module, mid):
        return
    label, eyebrow, desc, color, icon = TRACKS[track]
    db.add(Module(
        id=mid, track_id=track, title=title, subtitle=subtitle, level=level,
        level_order=order, duration_min=duration, featured=featured, accent=color, icon=icon,
    ))
    db.flush()
    for i, (tp, tt, tx) in enumerate(step_rows, 1):
        db.add(ModuleStep(module_id=mid, order=i, step_type=tp, title=tt,
                          content_json=json.dumps({"text": tx}, ensure_ascii=False)))


# ── Alfabetização ────────────────────────────────────────────────────────
def seed_alfabetizacao(db):
    T = "alfabetizacao"
    n = 0
    # 1. Letras
    for letter in ALFABETO:
        exemplos = by_prefix(letter, 7, 6)
        sample = ", ".join(exemplos) if exemplos else f"{letter}..."
        is_vowel = letter in VOGAIS
        add(db, f"alfa-letra-{letter}", T, f"A letra {letter.upper()}",
            f"{'Vogal' if is_vowel else 'Consoante'} {letter.upper()} — som e escrita.",
            "Começo", 0 if is_vowel else 1, 8, letter in "aeioubcdf", steps(
                ("explanation", f"O som de {letter.upper()}",
                 f"A letra {letter.upper()} é uma {'vogal' if is_vowel else 'consoante'}. "
                 f"{'As vogais abrem a voz e formam o centro da sílaba.' if is_vowel else 'As consoantes precisam de uma vogal para formar sílaba.'}"),
                ("example", "Palavras com essa letra", f"Leia em voz alta: {sample}."),
                ("practice", "Escreva e fale", f"Escreva cinco vezes a letra {letter.upper()}. Depois escreva uma palavra que comece com ela."),
                ("check", "Verificação", f"Quantas palavras com {letter.upper()} você encontrou hoje? Escreva duas."),
                ("next", "Próximo passo", f"Você dominou a letra {letter.upper()}! Siga para a próxima."),
            ))
        n += 1
    # 2. Famílias silábicas
    for c in CONSOANTES:
        silabas = " ".join(f"{c.upper()}{v.upper()}" for v in VOGAIS)
        palavras = by_prefix(c, 7, 5)
        add(db, f"alfa-silaba-{c}", T, f"Família silábica do {c.upper()}",
            f"{silabas}", "Essencial", 2, 12, c in "bcdfm", steps(
                ("explanation", "Como formar", f"Junte {c.upper()} com cada vogal: {silabas}."),
                ("example", "Palavras reais", f"Palavras com a família do {c.upper()}: {', '.join(palavras)}."),
                ("practice", "Complete", f"Escreva todas as sílabas do {c.upper()}: {silabas}. Leia cada uma."),
                ("check", "Ditado", f"Peça para alguém ditar palavras com {c.upper()} e escreva a sílaba que ouviu."),
                ("next", "Avançar", "Família dominada! Continue para a próxima letra."),
            ))
        n += 1
    # 3. Temas de palavras
    temas = [
        ("corpo", "Mão, pé, olho, boca", "corpo humano"),
        ("casa", "Porta, mesa, cama, janela", "a casa"),
        ("comida", "Arroz, feijão, pão, café", "a comida"),
        ("familia", "Mãe, pai, filho, avó", "a família"),
        ("rua", "Ônibus, escola, mercado", "a rua"),
        ("cores", "Vermelho, azul, amarelo", "as cores"),
        ("dias", "Segunda, terça, janeiro", "o calendário"),
        ("animais", "Cachorro, gato, pássaro", "os animais"),
        ("trabalho", "Emprego, salário, contrato", "o trabalho"),
        ("saude", "Médico, remédio, consulta", "a saúde"),
        ("documentos", "CPF, RG, certidão", "os documentos"),
        ("natureza", "Sol, chuva, rio, árvore", "a natureza"),
        ("emocoes", "Alegria, tristeza, medo", "as emoções"),
        ("compras", "Preço, troco, nota fiscal", "as compras"),
        ("transporte", "Ônibus, metrô, bicicleta", "o transporte"),
        ("escola", "Aula, caderno, professor", "a escola"),
        ("dinheiro", "Real, centavo, poupança", "o dinheiro"),
        ("tempo", "Hoje, amanhã, semana", "o tempo"),
        ("tecnologia", "Celular, internet, senha", "a tecnologia"),
        ("musica", "Canção, ritmo, violão", "a música"),
        ("esporte", "Futebol, corrida, time", "o esporte"),
        ("cidade", "Praça, bairro, prefeitura", "a cidade"),
        ("campo", "Roça, plantação, colheita", "o campo"),
        ("mar", "Praia, onda, peixe", "o mar"),
    ]
    for i, (tid, exemplos, tema) in enumerate(temas):
        add(db, f"alfa-tema-{tid}", T, f"Palavras de {tema}",
            exemplos, "Prática", 5 + i // 6, 12, i < 3, steps(
                ("explanation", f"Vocabulário de {tema}", f"Vamos aprender palavras que você usa quando falamos de {tema}."),
                ("example", "Leia e repita", f"{exemplos}. Leia cada palavra em voz alta, devagar."),
                ("practice", "Escreva", f"Escreva 5 palavras de {tema} e divida cada uma em sílabas."),
                ("check", "Ditado", "Peça para alguém ditar 5 palavras do tema. Escreva e confira."),
                ("next", "Muito bem", f"Seu vocabulário de {tema} cresceu!"),
            ))
        n += 1
    # 4. Frases
    frases = [
        ("simples", "Minha primeira frase", "Sujeito + verbo.", "Eu leio. Ela canta. Ele corre."),
        ("complemento", "Frases com complemento", "Sujeito + verbo + objeto.", "Eu leio um livro. Ela canta uma música."),
        ("pergunta", "Fazer perguntas", "Como, quando, onde, por quê.", "Como você se chama? Onde mora?"),
        ("negativa", "Frases negativas", "Usando NÃO.", "Eu não sei. Ela não veio."),
        ("bilhete", "Escrever um bilhete", "Comunicar algo simples.", "Mãe, fui ao mercado. Volto às 5."),
        ("lista", "Escrever uma lista", "Organizar itens.", "1. Arroz  2. Feijão  3. Óleo  4. Café"),
        ("recado", "Dar um recado", "Informar alguém.", "Dona Maria ligou. Pediu para ligar às 10h."),
        ("convite", "Escrever um convite", "Chamar alguém.", "Venha! Dia 15, às 15h, na casa da vovó."),
        ("descricao", "Descrever algo", "Dizer como algo é.", "Minha casa é pequena. Tem dois quartos."),
        ("opiniao", "Dar sua opinião", "Dizer o que pensa.", "Eu acho que estudar é importante."),
        ("carta", "Escrever uma carta", "Saudação, mensagem, despedida.", "Olá! Escrevo para contar que estou bem. Abraços."),
        ("email", "Escrever um e-mail", "Assunto, saudação, mensagem.", "Assunto: Matrícula. Bom dia, gostaria de informações."),
    ]
    for i, (fid, title, sub, ex) in enumerate(frases):
        add(db, f"alfa-frase-{fid}", T, title, sub, "Intermediário", 8 + i // 3, 15, i < 2, steps(
            ("explanation", "Como montar", f"Vamos aprender a {title.lower()}."),
            ("example", "Exemplos", ex),
            ("practice", "Escreva", "Agora escreva 3 frases do mesmo tipo com suas palavras."),
            ("check", "Revisão", "Releia: faz sentido? Tem ponto final? Começa com maiúscula?"),
            ("next", "Avance", "Sua escrita está evoluindo!"),
        ))
        n += 1
    # 5. Textos
    textos = [
        ("receita", "Ler uma receita", "Ingredientes e modo de fazer."),
        ("noticia", "Ler uma notícia", "O que, onde, quando."),
        ("formulario", "Preencher um formulário", "Nome, CPF, endereço."),
        ("placa", "Ler placas e avisos", "Informações do dia a dia."),
        ("conta", "Ler uma conta de luz", "Valor, vencimento, código."),
        ("bula", "Ler uma bula", "Dose, horário, efeitos."),
        ("contrato", "Entender um contrato", "Partes, obrigações, assinatura."),
        ("cardapio", "Ler um cardápio", "Pratos, preços, pedido."),
        ("onibus", "Ler um horário de ônibus", "Linhas, horários, destino."),
        ("instrucoes", "Seguir instruções", "Passo a passo de uma tarefa."),
    ]
    for i, (tid, title, sub) in enumerate(textos):
        add(db, f"alfa-texto-{tid}", T, title, sub, "Avançado", 12 + i // 3, 20, i < 2, steps(
            ("explanation", "O que é", f"Vamos aprender a {title.lower()}."),
            ("example", "Exemplo real", f"Veja este exemplo de {sub.lower()}."),
            ("practice", "Faça você", "Pratique com um exemplo real do seu dia a dia."),
            ("check", "Compreensão", "O que entendeu? Quais informações são mais importantes?"),
            ("next", "Parabéns", "Você está lendo textos reais!"),
        ))
        n += 1
    return n


# ── Informática / Matemática / Idiomas ───────────────────────────────────
def seed_from_content(db, track: str, level: str, items) -> int:
    """Semeia módulos com conteúdo curado: (id, título, subtítulo, etapas)."""
    for i, (mid, title, sub, step_rows) in enumerate(items):
        add(db, mid, track, title, sub, level, i // 8, 12 + (i % 3) * 2, i % 7 == 0, step_rows)
    return len(items)


def main() -> int:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Rebuild determinístico do catálogo
    db.query(ModuleStep).delete()
    db.query(Module).delete()
    db.query(Track).delete()
    db.commit()
    for tid, (label, eyebrow, desc, color, icon) in TRACKS.items():
        db.add(Track(id=tid, label=label, eyebrow=eyebrow, description=desc, color=color, icon=icon, target_modules=0))
    db.commit()

    n = 0
    n += seed_alfabetizacao(db)
    n += seed_from_content(db, "informatica", "Começo", INFORMATICA)
    n += seed_from_content(db, "matematica", "Essencial", MATEMATICA)
    n += seed_from_content(db, "idiomas", "A1 · Iniciante", IDIOMAS)
    db.commit()

    for tid in TRACKS:
        c = db.query(Module).filter(Module.track_id == tid).count()
        print(f"  {TRACKS[tid][0]}: {c} módulos")
    total = db.query(Module).count()
    print(f"\nTotal: {total} módulos, {db.query(ModuleStep).count()} etapas")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
