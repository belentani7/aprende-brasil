#!/usr/bin/env python3
"""Gera o currículo da Aprende Brasil (200+ módulos) e popula o SQLite.

- Alfabetização: usa o banco de palavras aberto (data/open/palavras-pt.txt).
- Informática / Matemática / Idiomas: listas curadas com passos concretos.

Rodar: python -m scripts.build_curriculum
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.database import Base, SessionLocal, engine  # noqa: E402
from api.models import Module, ModuleStep, Track  # noqa: E402

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
def seed_topics(db, track, level, items):
    n = 0
    for i, (mid, title, sub) in enumerate(items):
        add(db, mid, track, title, sub, level, i // 8, 12 + (i % 3) * 2, i % 7 == 0, steps(
            ("explanation", "Entender", f"{title}: {sub}"),
            ("example", "Ver um exemplo", f"Exemplo prático sobre {sub.lower()}."),
            ("practice", "Praticar", f"Agora é sua vez: pratique {title.lower()} no seu dia a dia."),
            ("check", "Verificar", "Você conseguiu? O que foi mais difícil?"),
            ("next", "Próximo passo", "Ótimo! Continue praticando."),
        ))
        n += 1
    return n


INFO = [
    ("info-ligar", "Ligar e desligar o computador", "Botão de energia e tela inicial."),
    ("info-mouse", "Usar o mouse", "Clicar, arrastar e rolar."),
    ("info-teclado", "Conhecer o teclado", "Letras, números, espaço, enter."),
    ("info-celular", "Navegar no celular", "Tocar, deslizar, abrir apps."),
    ("info-internet", "O que é a internet", "Como a rede conecta pessoas."),
    ("info-busca", "Pesquisar na internet", "Encontrar o que você precisa."),
    ("info-email", "Criar e usar um e-mail", "Escrever, enviar e receber."),
    ("info-senha", "Criar uma senha segura", "Proteger suas contas."),
    ("info-whatsapp", "Usar o WhatsApp", "Mensagens, fotos e áudios."),
    ("info-fotos", "Organizar fotos", "Pastas e liberar espaço."),
    ("info-pix", "Fazer e receber Pix", "Transferências com segurança."),
    ("info-docs", "Usar um editor de texto", "Escrever, salvar e compartilhar."),
    ("info-planilha", "Planilha simples", "Organizar gastos em colunas."),
    ("info-golpes", "Reconhecer golpes online", "Links falsos e como se proteger."),
    ("info-curriculo", "Fazer um currículo digital", "Modelo pronto para enviar."),
    ("info-arquivos", "Guardar e encontrar arquivos", "Pastas, nomes e buscas."),
    ("info-usb", "Usar um pendrive", "Copiar e ejetar com segurança."),
    ("info-impressora", "Imprimir um documento", "Escolher impressora e papel."),
    ("info-videochamada", "Fazer uma videochamada", "Câmera, microfone e link."),
    ("info-mapa", "Usar mapas e GPS", "Encontrar endereços e rotas."),
    ("info-compras", "Comprar online com segurança", "Sites confiáveis e pagamento."),
    ("info-banco", "Usar o app do banco", "Saldo, extrato e pagamentos."),
    ("info-sus", "Usar serviços públicos online", "Agendamentos e documentos."),
    ("info-nuvem", "Guardar na nuvem", "Acessar arquivos de qualquer lugar."),
    ("info-wifi", "Conectar ao Wi-Fi", "Redes, senha e segurança."),
    ("info-bateria", "Cuidar da bateria", "Carregar e economizar energia."),
    ("info-acessibilidade", "Recursos de acessibilidade", "Zoom, leitor de tela e contraste."),
    ("info-formatar", "Formatar um texto", "Negrito, itálico e alinhamento."),
    ("info-pdf", "Trabalhar com PDF", "Abrir, preencher e assinar."),
    ("info-qrcode", "Ler um QR Code", "Abrir links e pagar."),
    ("info-backup", "Fazer backup", "Proteger seus arquivos."),
    ("info-senhas-gestor", "Gerenciar várias senhas", "Organizar sem anotar no papel."),
    ("info-ia", "Usar assistentes de IA", "Pedir ajuda e revisar respostas."),
    ("info-codigo", "Primeiros passos em programação", "O que é um algoritmo."),
    ("info-scratch", "Criar com blocos", "Lógica visual passo a passo."),
    ("info-html", "Uma página web simples", "Título, texto e imagem."),
    ("info-dados", "Entender dados e gráficos", "Transformar números em decisões."),
    ("info-privacidade", "Proteger sua privacidade", "O que compartilhar e o que não."),
    ("info-etiqueta", "Boa convivência online", "Respeito e comunicação clara."),
    ("info-acessivel", "Criar conteúdo acessível", "Texto alternativo e contraste."),
]

MAT = [
    ("mat-contar", "Contar até 100", "Contagem com objetos do dia a dia."),
    ("mat-soma", "Somar com as mãos", "2 + 3 com dedos e desenhos."),
    ("mat-subtracao", "Subtrair na prática", "Tinha 5, tirei 2."),
    ("mat-dinheiro", "Contar dinheiro", "Moedas e notas do real."),
    ("mat-troco", "Calcular o troco", "Paguei R$10, quanto volta?"),
    ("mat-multiplicar", "Multiplicar é repetir", "3 vezes 4 = 4+4+4."),
    ("mat-dividir", "Dividir para repartir", "12 balas para 3 pessoas."),
    ("mat-medidas", "Medir comprimento", "Metro e centímetro."),
    ("mat-peso", "Medir peso", "Quilos e gramas."),
    ("mat-horas", "Ler as horas", "Relógio analógico e digital."),
    ("mat-calendario", "Usar o calendário", "Dias, semanas e meses."),
    ("mat-receita", "Matemática na receita", "Dobrar e reduzir à metade."),
    ("mat-grafico", "Ler um gráfico", "Barras e linhas."),
    ("mat-porcentagem", "Porcentagem no dia a dia", "Desconto de 20%."),
    ("mat-fracoes", "Frações na pizza", "Metade, terço e quarto."),
    ("mat-formas", "Formas geométricas", "Círculo, quadrado e triângulo."),
    ("mat-area", "Área e perímetro", "Medir um terreno."),
    ("mat-angulos", "Ângulos", "Reto, agudo e obtuso."),
    ("mat-regra3", "Regra de três simples", "Proporções do cotidiano."),
    ("mat-sequencias", "Sequências e padrões", "Descobrir o próximo número."),
    ("mat-equacao", "Equações simples", "Descobrir o valor de x."),
    ("mat-negativos", "Números negativos", "Temperatura e dívidas."),
    ("mat-estatistica", "Média e mediana", "Resumir um conjunto de dados."),
    ("mat-probabilidade", "Probabilidade", "Chance de acontecer."),
    ("mat-juros", "Juros simples", "Entender um empréstimo."),
    ("mat-orcamento", "Fazer um orçamento", "Entradas e saídas."),
    ("mat-nota-fiscal", "Conferir uma nota fiscal", "Itens, valores e total."),
    ("mat-conversao", "Converter unidades", "Metros, litros e gramas."),
    ("mat-tabela", "Ler uma tabela", "Organizar informação."),
    ("mat-simetria", "Simetria", "Formas espelhadas."),
    ("mat-escala", "Escalas e plantas", "Ler uma planta simples."),
    ("mat-tempo", "Calcular tempo", "Duração entre horários."),
    ("mat-capacidade", "Medir capacidade", "Litros e mililitros."),
    ("mat-numeros-romanos", "Números romanos", "I, V, X, L, C."),
    ("mat-pares", "Números pares e ímpares", "Reconhecer o padrão."),
    ("mat-primos", "Números primos", "Só divide por 1 e ele mesmo."),
    ("mat-mdc", "MDC e MMC", "Fatores comuns."),
    ("mat-potencias", "Potências e raízes", "2² = 4, √9 = 3."),
    ("mat-desconto", "Calcular descontos", "Comparar preços."),
    ("mat-planilha", "Matemática na planilha", "Somar colunas automaticamente."),
]

IDIO = [
    ("idio-cumprimentos-en", "Cumprimentos em inglês", "Hello, good morning."),
    ("idio-apresentar-en", "Me apresentar em inglês", "My name is... I am from Brazil."),
    ("idio-numeros-en", "Números em inglês", "One to twenty."),
    ("idio-comida-en", "Comida em inglês", "Rice, beans, water, coffee."),
    ("idio-cores-en", "Cores em inglês", "Red, blue, green."),
    ("idio-dias-en", "Dias e meses em inglês", "Monday, January."),
    ("idio-familia-en", "Família em inglês", "Mother, father, sister."),
    ("idio-mercado-en", "No mercado em inglês", "How much is this?"),
    ("idio-onibus-en", "Transporte em inglês", "Where is the bus stop?"),
    ("idio-medico-en", "No médico em inglês", "I have a headache."),
    ("idio-trabalho-en", "No trabalho em inglês", "Can you help me?"),
    ("idio-viagem-en", "Em viagem em inglês", "Where is the hotel?"),
    ("idio-cumprimentos-es", "Cumprimentos em espanhol", "Hola, buenos días."),
    ("idio-apresentar-es", "Me apresentar em espanhol", "Me llamo... Soy de Brasil."),
    ("idio-numeros-es", "Números em espanhol", "Uno al veinte."),
    ("idio-comida-es", "Comida em espanhol", "Arroz, frijoles, agua."),
    ("idio-falsos-amigos", "Falsos amigos PT-ES", "Exquisito, largo, oficina."),
    ("idio-mercado-es", "No mercado em espanhol", "¿Cuánto cuesta?"),
    ("idio-viagem-es", "Em viagem em espanhol", "¿Dónde está el hotel?"),
    ("idio-medico-es", "No médico em espanhol", "Me duele la cabeza."),
    ("idio-pt-estrangeiros", "Português para estrangeiros", "Bom dia! Como falar no Brasil."),
    ("idio-entrevista-pt", "Entrevista de trabalho", "Perguntas comuns e respostas."),
    ("idio-telefone-pt", "Falar ao telefone", "Atenção, quem fala?"),
    ("idio-email-pt", "Escrever e-mail profissional", "Assunto, saudação e despedida."),
    ("idio-apresentacao-pt", "Fazer uma apresentação", "Estrutura e linguagem."),
    ("idio-reuniao-pt", "Participar de uma reunião", "Concordar e discordar."),
    ("idio-escrita-pt", "Escrever com clareza", "Frases curtas e diretas."),
    ("idio-leitura-en", "Ler um texto curto em inglês", "Ideia principal."),
    ("idio-escuta-en", "Ouvir e entender inglês", "Palavras-chave."),
    ("idio-pronuncia-en", "Pronúncia em inglês", "Sons difíceis."),
    ("idio-pronuncia-es", "Pronúncia em espanhol", "Sons e ritmo."),
    ("idio-cultura-br", "Cultura brasileira", "Regiões, festas e costumes."),
]


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
    n += seed_topics(db, "informatica", "Começo", INFO)
    n += seed_topics(db, "matematica", "Essencial", MAT)
    n += seed_topics(db, "idiomas", "A1 · Iniciante", IDIO)
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
