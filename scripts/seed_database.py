"""
Seed the SQLite database with tracks and real literacy modules.
Run: python -m scripts.seed_database
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.database import engine, Base, SessionLocal
from api.models import Track, Module, ModuleStep

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Tracks ──────────────────────────────────────────────
TRACKS = [
    {"id": "alfabetizacao", "label": "Alfabetização", "eyebrow": "Ler e escrever", "description": "Primeiros passos na leitura e escrita em português brasileiro.", "color": "orange", "icon": "BookOpen", "target_modules": 200},
    {"id": "informatica", "label": "Informática", "eyebrow": "Pensamento digital", "description": "Do primeiro clique à criação de projetos digitais.", "color": "blue", "icon": "Code2", "target_modules": 680},
    {"id": "matematica", "label": "Matemática", "eyebrow": "Raciocínio aplicado", "description": "Números, formas e decisões para a vida real.", "color": "violet", "icon": "BarChart3", "target_modules": 720},
    {"id": "idiomas", "label": "Idiomas", "eyebrow": "Comunicação global", "description": "Pratique inglês, espanhol e português no seu ritmo.", "color": "green", "icon": "Languages", "target_modules": 600},
]

for t in TRACKS:
    if not db.query(Track).get(t["id"]):
        db.add(Track(**t))
db.commit()

# ── Alfabetização: módulos reales ───────────────────────
# Nivel 1: Letras y sonidos
ALFA_LETRAS = [
    ("alfa-vogais", "As cinco vogais", "A, E, I, O, U — os sons que abrem todas as palavras.", "Começo", 0, 8, True),
    ("alfa-consoantes-1", "Consoantes: B, C, D, F", "Sons que precisam de uma vogal para existir.", "Começo", 1, 10, False),
    ("alfa-consoantes-2", "Consoantes: G, H, J, L", "Mais sons para formar sílabas novas.", "Começo", 1, 10, False),
    ("alfa-consoantes-3", "Consoantes: M, N, P, Q", "Sons que aparecem em palavras do dia a dia.", "Começo", 1, 10, False),
    ("alfa-consoantes-4", "Consoantes: R, S, T, V", "Pratique a escrita e o som de cada letra.", "Começo", 1, 10, False),
    ("alfa-consoantes-5", "Consoantes: X, Z e letras especiais", "K, W, Y e os sons que completam o alfabeto.", "Começo", 1, 10, False),
    ("alfa-nome", "Escrever meu nome", "A primeira palavra que é só sua.", "Começo", 0, 8, True),
]

# Nivel 2: Sílabas
ALFA_SILABAS = [
    ("alfa-sil-simples", "Sílabas simples: BA, CA, DA", "Junte uma consoante com uma vogal.", "Essencial", 2, 12, True),
    ("alfa-sil-compostas", "Sílabas com dois sons: BRA, CRI, FLO", "Quando duas consoantes se juntam antes da vogal.", "Essencial", 3, 14, False),
    ("alfa-sil-nasais", "Sílabas nasais: AN, EM, IN", "Sons que saem pelo nariz.", "Essencial", 3, 12, False),
    ("alfa-sil-fechadas", "Sílabas fechadas: AR, ES, IL", "Quando a vogal vem antes da consoante.", "Essencial", 3, 12, False),
    ("alfa-divisao", "Dividir palavras em sílabas", "CA-SA, ES-CO-LA, BO-NE-CA.", "Essencial", 4, 15, False),
]

# Nivel 3: Palabras
ALFA_PALAVRAS = [
    ("alfa-corpo", "Palavras do corpo", "Mão, pé, olho, boca — palavras que você já conhece.", "Prática", 5, 12, False),
    ("alfa-casa", "Palavras da casa", "Porta, mesa, cama, janela.", "Prática", 5, 12, False),
    ("alfa-comida", "Palavras da comida", "Arroz, feijão, pão, água, café.", "Prática", 5, 12, True),
    ("alfa-familia", "Palavras da família", "Mãe, pai, filho, irmã, avó.", "Prática", 5, 10, False),
    ("alfa-rua", "Palavras da rua", "Ônibus, escola, mercado, hospital.", "Prática", 5, 12, False),
    ("alfa-numeros", "Palavras dos números", "Um, dois, três... ler e escrever números por extenso.", "Prática", 6, 14, False),
    ("alfa-dias", "Dias da semana e meses", "Segunda, terça... janeiro, fevereiro...", "Prática", 6, 12, False),
    ("alfa-cores", "Palavras das cores", "Vermelho, azul, amarelo, verde, branco, preto.", "Prática", 5, 10, False),
]

# Nivel 4: Frases
ALFA_FRASES = [
    ("alfa-frase-simples", "Minha primeira frase", "Sujeito + verbo: 'Eu leio', 'Ela canta'.", "Intermediário", 7, 15, True),
    ("alfa-frase-completa", "Frases com complemento", "'Eu leio um livro', 'Ela canta uma música'.", "Intermediário", 8, 15, False),
    ("alfa-pergunta", "Fazer perguntas", "Como, quando, onde, por quê.", "Intermediário", 8, 14, False),
    ("alfa-bilhete", "Escrever um bilhete", "Comunicar algo simples para outra pessoa.", "Intermediário", 9, 18, False),
    ("alfa-lista", "Escrever uma lista", "Lista de compras, de tarefas, de desejos.", "Intermediário", 8, 12, False),
]

# Nivel 5: Textos
ALFA_TEXTOS = [
    ("alfa-texto-curto", "Ler um texto curto", "Um parágrafo sobre o Brasil, com perguntas.", "Avançado", 10, 20, True),
    ("alfa-receita", "Ler uma receita", "Bolo de milho: ingredientes e modo de fazer.", "Avançado", 10, 18, False),
    ("alfa-noticia", "Ler uma notícia simples", "Entender o que aconteceu, onde e quando.", "Avançado", 11, 20, False),
    ("alfa-carta", "Escrever uma carta", "Saudação, mensagem e despedida.", "Avançado", 12, 22, False),
    ("alfa-documento", "Preencher um formulário", "Nome, data de nascimento, endereço, CPF.", "Avançado", 12, 18, True),
]

# ── Informática: módulos básicos ────────────────────────
INFO_MODULES = [
    ("info-ligar", "Ligar e desligar o computador", "O primeiro passo: botão de energia e tela inicial.", "Começo", 0, 10, True, "informatica"),
    ("info-mouse", "Usar o mouse", "Clicar, arrastar, rolar — controle com a mão.", "Começo", 1, 12, False, "informatica"),
    ("info-teclado", "Conhecer o teclado", "Letras, números, espaço, enter e backspace.", "Começo", 1, 14, True, "informatica"),
    ("info-celular", "Navegar no celular", "Tocar, deslizar, abrir e fechar aplicativos.", "Começo", 2, 12, False, "informatica"),
    ("info-internet", "O que é a internet", "Como a rede conecta pessoas e informações.", "Essencial", 3, 15, False, "informatica"),
    ("info-busca", "Pesquisar na internet", "Google: como encontrar o que você precisa.", "Essencial", 4, 14, True, "informatica"),
    ("info-email", "Criar e usar um e-mail", "Escrever, enviar e receber mensagens.", "Essencial", 5, 18, False, "informatica"),
    ("info-senha", "Criar uma senha segura", "Proteger suas contas e sua privacidade.", "Essencial", 5, 12, True, "informatica"),
    ("info-whatsapp", "Usar o WhatsApp", "Mensagens, fotos, áudios e grupos.", "Prática", 6, 16, False, "informatica"),
    ("info-fotos", "Organizar fotos no celular", "Pastas, favoritos e liberar espaço.", "Prática", 6, 14, False, "informatica"),
    ("info-pix", "Fazer e receber Pix", "Transferências pelo celular com segurança.", "Prática", 7, 15, True, "informatica"),
    ("info-docs", "Usar Google Docs", "Escrever, salvar e compartilhar documentos.", "Intermediário", 8, 20, False, "informatica"),
    ("info-planilha", "Planilha simples", "Organizar gastos em linhas e colunas.", "Intermediário", 9, 22, False, "informatica"),
    ("info-golpes", "Reconhecer golpes online", "Links falsos, mensagens suspeitas e como se proteger.", "Intermediário", 8, 16, True, "informatica"),
    ("info-curriculo", "Fazer um currículo digital", "Modelo simples pronto para imprimir ou enviar.", "Avançado", 10, 25, False, "informatica"),
]

# ── Matemática: módulos básicos ─────────────────────────
MAT_MODULES = [
    ("mat-contar", "Contar até 100", "Contagem com objetos do dia a dia.", "Começo", 0, 10, True, "matematica"),
    ("mat-soma", "Somar com as mãos", "2 + 3 = ? Soma com dedos e desenhos.", "Começo", 1, 12, True, "matematica"),
    ("mat-subtracao", "Subtrair na prática", "Tinha 5, tirei 2: quanto sobrou?", "Começo", 2, 12, False, "matematica"),
    ("mat-dinheiro", "Contar dinheiro", "Moedas e notas do real brasileiro.", "Essencial", 3, 15, True, "matematica"),
    ("mat-troco", "Calcular o troco", "Paguei com R$10, quanto recebo de volta?", "Essencial", 4, 14, False, "matematica"),
    ("mat-multiplicar", "Multiplicar é repetir", "3 vezes 4 = 4 + 4 + 4.", "Essencial", 5, 16, False, "matematica"),
    ("mat-dividir", "Dividir para repartir", "12 balas para 3 pessoas.", "Essencial", 6, 16, False, "matematica"),
    ("mat-medidas", "Medir comprimento", "Metro, centímetro e a fita métrica.", "Prática", 7, 14, True, "matematica"),
    ("mat-peso", "Medir peso", "Quilos e gramas no mercado.", "Prática", 7, 12, False, "matematica"),
    ("mat-horas", "Ler as horas", "Relógio analógico e digital.", "Prática", 8, 16, False, "matematica"),
    ("mat-calendario", "Usar o calendário", "Dias, semanas, meses e datas importantes.", "Prática", 8, 14, False, "matematica"),
    ("mat-receita", "Matemática na receita", "Dobrar, metade e proporções na cozinha.", "Intermediário", 9, 18, True, "matematica"),
    ("mat-grafico", "Ler um gráfico", "Barras e linhas que contam histórias com números.", "Intermediário", 10, 18, False, "matematica"),
    ("mat-porcentagem", "Porcentagem no dia a dia", "Desconto de 20%: quanto eu economizo?", "Avançado", 11, 20, False, "matematica"),
]

# ── Idiomas: módulos básicos ────────────────────────────
IDIO_MODULES = [
    ("idio-cumprimentos-en", "Cumprimentos em inglês", "Hello, good morning, how are you?", "A1 · Iniciante", 0, 12, True, "idiomas"),
    ("idio-apresentar-en", "Me apresentar em inglês", "My name is... I am from Brazil.", "A1 · Iniciante", 1, 14, False, "idiomas"),
    ("idio-numeros-en", "Números em inglês", "One, two, three... até twenty.", "A1 · Iniciante", 2, 12, False, "idiomas"),
    ("idio-comida-en", "Comida em inglês", "Rice, beans, water, coffee, bread.", "A1 · Iniciante", 3, 14, True, "idiomas"),
    ("idio-cumprimentos-es", "Cumprimentos em espanhol", "Hola, buenos días, ¿cómo estás?", "A1 · Iniciante", 0, 12, True, "idiomas"),
    ("idio-apresentar-es", "Me apresentar em espanhol", "Me llamo... Soy de Brasil.", "A1 · Iniciante", 1, 14, False, "idiomas"),
    ("idio-falsos-amigos", "Falsos amigos PT-ES", "Exquisito, largo, oficina — cuidado!", "A2 · Básico", 4, 16, True, "idiomas"),
    ("idio-mercado-en", "No mercado em inglês", "How much is this? I would like...", "A2 · Básico", 5, 16, False, "idiomas"),
    ("idio-onibus-en", "Transporte em inglês", "Where is the bus stop? One ticket, please.", "A2 · Básico", 5, 14, False, "idiomas"),
    ("idio-medico-en", "No médico em inglês", "I have a headache. I need help.", "A2 · Básico", 6, 16, False, "idiomas"),
    ("idio-pt-estrangeiros", "Português para estrangeiros", "Bom dia! Como falar no Brasil.", "A1 · Iniciante", 0, 14, True, "idiomas"),
    ("idio-entrevista", "Entrevista de trabalho", "Perguntas comuns em português e como responder.", "Comunicação", 8, 20, False, "idiomas"),
]


def make_steps(module_id, level):
    """Generate pedagogical steps for a module."""
    steps = [
        {"order": 1, "step_type": "explanation", "title": "Entender o conceito", "content_json": json.dumps({"text": "Vamos começar entendendo o que vamos aprender hoje."})},
        {"order": 2, "step_type": "example", "title": "Ver um exemplo", "content_json": json.dumps({"text": "Observe este exemplo com atenção."})},
        {"order": 3, "step_type": "practice", "title": "Praticar", "content_json": json.dumps({"text": "Agora é sua vez! Tente fazer sozinho(a)."})},
        {"order": 4, "step_type": "check", "title": "Verificar", "content_json": json.dumps({"text": "Vamos ver se você entendeu. Responda:"})},
        {"order": 5, "step_type": "next", "title": "Próximo passo", "content_json": json.dumps({"text": "Parabéns! Você completou esta etapa."})},
    ]
    return [ModuleStep(module_id=module_id, **s) for s in steps]


def seed_modules(items, track_id):
    for mid, title, subtitle, level, level_order, duration, featured, *extra in items:
        tid = extra[0] if extra else track_id
        if not db.query(Module).get(mid):
            m = Module(
                id=mid, track_id=tid, title=title, subtitle=subtitle,
                level=level, level_order=level_order, duration_min=duration,
                featured=featured, accent=TRACKS_MAP.get(tid, "blue"),
                icon=ICONS_MAP.get(tid, "BookOpen"),
            )
            db.add(m)
            db.flush()
            for step in make_steps(mid, level):
                db.add(step)


TRACKS_MAP = {"alfabetizacao": "orange", "informatica": "blue", "matematica": "violet", "idiomas": "green"}
ICONS_MAP = {"alfabetizacao": "BookOpen", "informatica": "Code2", "matematica": "BarChart3", "idiomas": "Languages"}

seed_modules(ALFA_LETRAS, "alfabetizacao")
seed_modules(ALFA_SILABAS, "alfabetizacao")
seed_modules(ALFA_PALAVRAS, "alfabetizacao")
seed_modules(ALFA_FRASES, "alfabetizacao")
seed_modules(ALFA_TEXTOS, "alfabetizacao")
seed_modules(INFO_MODULES, "informatica")
seed_modules(MAT_MODULES, "matematica")
seed_modules(IDIO_MODULES, "idiomas")

db.commit()

total = db.query(Module).count()
for t in TRACKS:
    count = db.query(Module).filter(Module.track_id == t["id"]).count()
    print(f"  {t['label']}: {count} módulos")
print(f"\nTotal: {total} módulos con {total * 5} etapas pedagógicas")
print("Base de dados: data/aprende.db")
db.close()
