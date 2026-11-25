"""Conteúdo pedagógico curado — trilha Alfabetização (93 módulos).

Antes, as etapas de exemplo desta trilha eram geradas escolhendo as primeiras
palavras do banco aberto que começavam com uma letra. O resultado eram
sequências como "aabora, aac, aaiún" — palavras raras ou inexistentes no
português falado no Brasil, inúteis para quem está aprendendo a ler.

Aqui as palavras são escolhidas à mão, comuns no dia a dia, e cada etapa tem
uma instrução concreta que a pessoa consegue executar sozinha ou com ajuda.

Formato de cada item:
    (id, título, subtítulo, nível, level_order, duração, destaque, etapas)

Cinco etapas por módulo: explanation, example, practice, check, next.
"""

from __future__ import annotations

Step = tuple[str, str, str]
Item = tuple[str, str, str, str, int, int, bool, list[Step]]


# ── Letras ───────────────────────────────────────────────────────────────
# Para cada letra: palavras reais e comuns, usadas na etapa de exemplo.
LETRAS: dict[str, dict[str, object]] = {
    "a": {
        "palavras": ["água", "amigo", "amor", "árvore", "abelha"],
        "vogal": True,
        "nota": "O A é a vogal que abre mais a boca: aaaa.",
    },
    "b": {
        "palavras": ["bola", "bala", "banana", "barco", "boca"],
        "vogal": False,
        "nota": "O B junta os dois lábios e solta o ar de uma vez.",
    },
    "c": {
        "palavras": ["casa", "café", "cama", "carro", "cachorro"],
        "vogal": False,
        "nota": "O C pode soar como K, em casa, ou como S, em cinema.",
    },
    "d": {
        "palavras": ["dedo", "dia", "doce", "dinheiro", "dado"],
        "vogal": False,
        "nota": "O D encosta a língua atrás dos dentes de cima.",
    },
    "e": {
        "palavras": ["escola", "estrela", "escada", "elefante", "estrada"],
        "vogal": True,
        "nota": "O E pode ser aberto, como em pé, ou fechado, como em você.",
    },
    "f": {
        "palavras": ["faca", "festa", "feijão", "fogo", "família"],
        "vogal": False,
        "nota": "O F sopra o ar entre os dentes e o lábio de baixo.",
    },
    "g": {
        "palavras": ["gato", "gelo", "girafa", "gola", "gosto"],
        "vogal": False,
        "nota": "O G soa como em gato antes de A, O, U e como J antes de E, I.",
    },
    "h": {
        "palavras": ["hoje", "hora", "homem", "hospital", "horta"],
        "vogal": False,
        "nota": "O H não tem som próprio: em hoje, a boca começa direto no O.",
    },
    "i": {
        "palavras": ["ilha", "igreja", "irmão", "idade", "ideia"],
        "vogal": True,
        "nota": "O I é a vogal do sorriso: os lábios ficam esticados.",
    },
    "j": {
        "palavras": ["janela", "jogo", "jardim", "jornal", "jantar"],
        "vogal": False,
        "nota": "O J tem o mesmo som do G em gelo.",
    },
    "k": {
        "palavras": ["kiwi", "kart", "karaokê"],
        "vogal": False,
        "nota": "O K é pouco usado em português: aparece em nomes e palavras estrangeiras, com som de K.",
    },
    "l": {
        "palavras": ["lua", "livro", "leite", "lápis", "laranja"],
        "vogal": False,
        "nota": "O L encosta a ponta da língua atrás dos dentes de cima.",
    },
    "m": {
        "palavras": ["mãe", "mesa", "mão", "mundo", "música"],
        "vogal": False,
        "nota": "O M fecha os lábios e faz o som sair pelo nariz.",
    },
    "n": {
        "palavras": ["navio", "nome", "nove", "noite", "nuvem"],
        "vogal": False,
        "nota": "O N encosta a língua no céu da boca e o som sai pelo nariz.",
    },
    "o": {
        "palavras": ["olho", "ovo", "ouro", "onda", "ônibus"],
        "vogal": True,
        "nota": "O O deixa a boca redonda: ooo.",
    },
    "p": {
        "palavras": ["pai", "pão", "pato", "porta", "peixe"],
        "vogal": False,
        "nota": "O P junta os lábios e solta o ar sem voz, como um sopro curto.",
    },
    "q": {
        "palavras": ["queijo", "quatro", "quilo", "quintal", "quadro"],
        "vogal": False,
        "nota": "O Q quase sempre vem seguido de U: QUA, QUE, QUI, QUO.",
    },
    "r": {
        "palavras": ["rato", "rua", "rosa", "roda", "remédio"],
        "vogal": False,
        "nota": "O R no começo da palavra é forte, como em rato; entre vogais é suave, como em cara.",
    },
    "s": {
        "palavras": ["sol", "sapato", "sopa", "saudade", "suco"],
        "vogal": False,
        "nota": "O S faz o som de cobra: ssss.",
    },
    "t": {
        "palavras": ["tatu", "terra", "tempo", "tia", "trabalho"],
        "vogal": False,
        "nota": "O T encosta a língua atrás dos dentes e solta o ar.",
    },
    "u": {
        "palavras": ["uva", "unha", "último", "urgente", "universo"],
        "vogal": True,
        "nota": "O U deixa os lábios arredondados e para a frente: uuu.",
    },
    "v": {
        "palavras": ["vaca", "vela", "vida", "verde", "vizinho"],
        "vogal": False,
        "nota": "O V é como o F, mas com voz: os dentes vibram no lábio.",
    },
    "w": {
        "palavras": ["web", "waffle", "windsurf"],
        "vogal": False,
        "nota": "O W aparece em palavras estrangeiras e pode soar como V ou como U.",
    },
    "x": {
        "palavras": ["xícara", "xadrez", "xarope", "xerife", "xale"],
        "vogal": False,
        "nota": "O X pode soar como CH, em xícara, como S, em próximo, ou como KS, em táxi.",
    },
    "y": {
        "palavras": ["yoga", "yakisoba", "yen"],
        "vogal": False,
        "nota": "O Y aparece em palavras estrangeiras e pode soar como I.",
    },
    "z": {
        "palavras": ["zebra", "zíper", "zero", "zoológico", "zumbido"],
        "vogal": False,
        "nota": "O Z vibra como uma abelha: zzzz.",
    },
}

ALFABETO = "abcdefghijklmnopqrstuvwxyz"
VOGAIS = "aeiou"
CONSOANTES = "bcdfghjklmnpqrstvwxyz"


def _letras() -> list[Item]:
    itens: list[Item] = []
    for letra in ALFABETO:
        dado = LETRAS[letra]
        palavras = dado["palavras"]
        assert isinstance(palavras, list)
        vogal = bool(dado["vogal"])
        nota = str(dado["nota"])
        exemplo = ", ".join(palavras)
        primeira = palavras[0]
        tipo = "vogal" if vogal else "consoante"
        texto_explicacao = (
            f"A letra {letra.upper()} é uma {tipo}. {nota} "
            "Reconhecer o som e o desenho da letra é o primeiro passo para ler."
        )
        itens.append((
            f"alfa-letra-{letra}",
            f"A letra {letra.upper()}",
            f"{'Vogal' if vogal else 'Consoante'} {letra.upper()} — som e escrita.",
            "Começo",
            0 if vogal else 1,
            8,
            letra in "aeioubcdf",
            [
                ("explanation", f"O som de {letra.upper()}", texto_explicacao),
                ("example", "Palavras com essa letra",
                 f"Leia devagar, em voz alta: {exemplo}. Aponte a letra {letra.upper()} em cada palavra."),
                ("practice", "Escreva e fale",
                 f"Escreva a letra {letra.upper()} cinco vezes em letra de forma. "
                 f"Depois copie a palavra “{primeira}” e circule a letra {letra.upper()}."),
                ("check", "Verificação",
                 f"Sem olhar no exemplo, escreva uma palavra que tenha a letra {letra.upper()}. "
                 "Confira: o desenho da letra ficou igual ao modelo? O som combina?"),
                ("next", "Próximo passo",
                 f"Você já reconhece a letra {letra.upper()} no meio de palavras. "
                 "Leia a lista mais uma vez e siga para a próxima letra."),
            ],
        ))
    return itens


# ── Famílias silábicas ───────────────────────────────────────────────────
FAMILIAS: dict[str, list[str]] = {
    "b": ["bola", "bala", "banana", "bebê", "bicicleta", "boca", "bule"],
    "c": ["casa", "cavalo", "cebola", "cinema", "coração", "cueca"],
    "d": ["dado", "dedo", "dinheiro", "dólar", "dupla"],
    "f": ["faca", "feijão", "figo", "fogo", "futebol"],
    "g": ["gato", "gema", "girafa", "gola", "guloseima"],
    "h": ["hora", "hoje", "hálito", "hotel", "humilde"],
    "j": ["jaca", "janela", "jiló", "jogo", "julho"],
    "k": ["kiwi", "kart", "karaokê"],
    "l": ["lápis", "leite", "lima", "lousa", "lua"],
    "m": ["mala", "mel", "milho", "moeda", "muleta"],
    "n": ["nada", "neve", "ninho", "noite", "nuvem"],
    "p": ["pato", "pé", "pilha", "pote", "pulo"],
    "q": ["quadro", "queijo", "quilo", "quinta", "quatro"],
    "r": ["rato", "remédio", "rica", "rosa", "rua"],
    "s": ["sapo", "senha", "sítio", "sopa", "suco"],
    "t": ["tatu", "tenda", "tigre", "tomate", "tubo"],
    "v": ["vaca", "vela", "vila", "volta", "vulcão"],
    "w": ["waffle", "web", "windsurf"],
    "x": ["xale", "xícara", "xadrez", "xerife", "xilofone"],
    "y": ["yoga", "yakisoba", "yen"],
    "z": ["zebra", "zíper", "zero", "zoológico", "zumbido"],
}


def _familias() -> list[Item]:
    itens: list[Item] = []
    for consoante in CONSOANTES:
        silabas = " ".join(f"{consoante.upper()}{v.upper()}" for v in VOGAIS)
        palavras = FAMILIAS[consoante]
        exemplo = ", ".join(palavras)
        nota = ""
        if consoante == "h":
            nota = " O H não tem som: HO, HO, HO soa apenas como O."
        elif consoante in "kwy":
            nota = f" O {consoante.upper()} aparece sobretudo em palavras estrangeiras."
        elif consoante == "q":
            nota = " O Q sempre vem com U antes da vogal: QUA, QUE, QUI, QUO."
        itens.append((
            f"alfa-silaba-{consoante}",
            f"Família silábica do {consoante.upper()}",
            silabas,
            "Essencial",
            2,
            12,
            consoante in "bcdfm",
            [
                ("explanation", "Como formar",
                 f"Junte o {consoante.upper()} com cada vogal e você tem a família: {silabas}. "
                 f"Cada pedaço é uma sílaba, e toda sílaba precisa de uma vogal.{nota}"),
                ("example", "Palavras reais",
                 f"Palavras da família do {consoante.upper()}: {exemplo}. "
                 "Leia cada uma batendo uma palma por sílaba."),
                ("practice", "Complete",
                 f"Copie as sílabas {silabas} e leia cada uma em voz alta. "
                 f"Depois escreva de novo a palavra “{palavras[0]}” separando as sílabas."),
                ("check", "Ditado",
                 f"Peça a alguém para ditar duas palavras desta lista: {exemplo}. "
                 "Escreva o que ouviu e confira com o exemplo."),
                ("next", "Avançar",
                 f"Família do {consoante.upper()} dominada! "
                 "Leia a lista uma última vez e siga para a próxima família."),
            ],
        ))
    return itens


# ── Temas de vocabulário ─────────────────────────────────────────────────
TEMAS: list[tuple[str, str, str, list[str]]] = [
    ("corpo", "Palavras do corpo humano", "corpo humano",
     ["mão", "pé", "olho", "boca", "cabeça", "braço"]),
    ("casa", "Palavras da casa", "a casa",
     ["porta", "mesa", "cama", "janela", "cozinha", "telhado"]),
    ("comida", "Palavras da comida", "a comida",
     ["arroz", "feijão", "pão", "café", "leite", "fruta"]),
    ("familia", "Palavras da família", "a família",
     ["mãe", "pai", "filho", "filha", "avó", "irmão"]),
    ("rua", "Palavras da rua", "a rua",
     ["ônibus", "escola", "mercado", "praça", "calçada", "semáforo"]),
    ("cores", "Palavras das cores", "as cores",
     ["vermelho", "azul", "amarelo", "verde", "preto", "branco"]),
    ("dias", "Dias, meses e datas", "o calendário",
     ["segunda", "terça", "janeiro", "dezembro", "semana", "hoje"]),
    ("animais", "Palavras dos animais", "os animais",
     ["cachorro", "gato", "pássaro", "vaca", "peixe", "formiga"]),
    ("trabalho", "Palavras do trabalho", "o trabalho",
     ["emprego", "salário", "contrato", "carteira", "horário", "chefe"]),
    ("saude", "Palavras da saúde", "a saúde",
     ["médico", "remédio", "consulta", "posto", "exame", "vacina"]),
    ("documentos", "Palavras dos documentos", "os documentos",
     ["CPF", "RG", "certidão", "comprovante", "assinatura", "cadastro"]),
    ("natureza", "Palavras da natureza", "a natureza",
     ["sol", "chuva", "rio", "árvore", "folha", "vento"]),
    ("emocoes", "Palavras das emoções", "as emoções",
     ["alegria", "tristeza", "medo", "saudade", "raiva", "carinho"]),
    ("compras", "Palavras das compras", "as compras",
     ["preço", "troco", "nota fiscal", "desconto", "caixa", "carrinho"]),
    ("transporte", "Palavras do transporte", "o transporte",
     ["ônibus", "metrô", "bicicleta", "carro", "passagem", "parada"]),
    ("escola", "Palavras da escola", "a escola",
     ["aula", "caderno", "professor", "lápis", "prova", "recreio"]),
    ("dinheiro", "Palavras do dinheiro", "o dinheiro",
     ["real", "centavo", "poupança", "conta", "salário", "pagamento"]),
    ("tempo", "Palavras do tempo", "o tempo",
     ["hoje", "amanhã", "ontem", "semana", "mês", "ano"]),
    ("tecnologia", "Palavras da tecnologia", "a tecnologia",
     ["celular", "internet", "senha", "tela", "mensagem", "aplicativo"]),
    ("musica", "Palavras da música", "a música",
     ["canção", "ritmo", "violão", "letra", "voz", "festa"]),
    ("esporte", "Palavras do esporte", "o esporte",
     ["futebol", "corrida", "time", "gol", "treino", "bola"]),
    ("cidade", "Palavras da cidade", "a cidade",
     ["praça", "bairro", "prefeitura", "rua", "posto", "mercado"]),
    ("campo", "Palavras do campo", "o campo",
     ["roça", "plantação", "colheita", "enxada", "semente", "terra"]),
    ("mar", "Palavras do mar", "o mar",
     ["praia", "onda", "peixe", "areia", "barco", "sal"]),
]


def _temas() -> list[Item]:
    itens: list[Item] = []
    for i, (tid, titulo, tema, palavras) in enumerate(TEMAS):
        exemplo = ", ".join(palavras[:5])
        itens.append((
            f"alfa-tema-{tid}",
            titulo,
            exemplo,
            "Prática",
            5 + i // 6,
            12,
            i < 3,
            [
                ("explanation", f"Vocabulário de {tema}",
                 f"Estas palavras aparecem quando falamos de {tema}. "
                 "Ler e escrever o nome das coisas do dia a dia dá autonomia para "
                 "preencher formulários, ler avisos e pedir ajuda."),
                ("example", "Leia e repita",
                 f"Leia cada palavra em voz alta, devagar: {exemplo}. "
                 "Aponte ou desenhe o que cada uma nomeia."),
                ("practice", "Escreva",
                 f"Escolha três palavras de {tema}, copie no caderno e separe cada uma em sílabas. "
                 f"Comece por “{palavras[0]}”."),
                ("check", "Ditado",
                 f"Peça a alguém para ditar três palavras de {tema}. "
                 "Escreva e confira com a lista do exemplo."),
                ("next", "Muito bem",
                 f"Seu vocabulário de {tema} cresceu. "
                 "Use uma dessas palavras hoje em uma frase falada."),
            ],
        ))
    return itens


# ── Frases ───────────────────────────────────────────────────────────────
FRASES: list[tuple[str, str, str, str, str, str]] = [
    ("simples", "Minha primeira frase", "Sujeito + verbo.",
     "Toda frase precisa de alguém ou algo que faz a ação (o sujeito) e da ação (o verbo). Em “Eu leio”, “Eu” é o sujeito e “leio” é o verbo.",
     "Eu leio. Ela canta. Ele corre.",
     "Escreva três frases com um sujeito e um verbo: eu ___, ela ___, ele ___."),
    ("complemento", "Frases com complemento", "Sujeito + verbo + objeto.",
     "Muitos verbos pedem um complemento para a frase fazer sentido: quem lê, lê algo. Esse “algo” completa o sentido.",
     "Eu leio um livro. Ela canta uma música. Nós comemos arroz.",
     "Complete: eu leio ___, ela comprou ___, nós comemos ___."),
    ("pergunta", "Fazer perguntas", "Como, quando, onde, por quê.",
     "Perguntas começam com palavra de interrogação e terminam com ponto de interrogação (?). Elas servem para pedir informação.",
     "Como você se chama? Onde você mora? Quando começa a aula?",
     "Escreva três perguntas que você faria em um posto de saúde."),
    ("negativa", "Frases negativas", "Usando NÃO.",
     "Para negar, colocamos NÃO antes do verbo. O sentido da frase muda completamente.",
     "Eu não sei. Ela não veio. Nós não temos troco.",
     "Transforme em negativa: “Eu tenho documento”, “Ele mora aqui”, “A aula começa hoje”."),
    ("bilhete", "Escrever um bilhete", "Comunicar algo simples.",
     "Um bilhete é uma mensagem curta para alguém que convive com você. Precisa de nome do destinatário, recado e assinatura.",
     "Mãe, fui ao mercado. Volto às 5. — Ana",
     "Escreva um bilhete avisando que você saiu e a que horas volta."),
    ("lista", "Escrever uma lista", "Organizar itens.",
     "Listas servem para não esquecer o que comprar ou fazer. Cada item fica em uma linha, numerado ou com um traço.",
     "1. Arroz  2. Feijão  3. Óleo  4. Café",
     "Monte a lista de compras da sua casa com cinco itens."),
    ("recado", "Dar um recado", "Informar alguém.",
     "Um recado registra quem ligou, o que queria e para quem era. Anotar evita esquecer detalhes.",
     "Dona Maria ligou. Pediu para você retornar até as 10h. — Recepção",
     "Anote um recado com nome, horário e pedido."),
    ("convite", "Escrever um convite", "Chamar alguém.",
     "Um convite diz o que vai acontecer, quando e onde. Sem esses três dados, a pessoa não consegue ir.",
     "Venha! Dia 15, às 15h, na casa da vovó. Vai ter bolo.",
     "Escreva um convite para um almoço de domingo na sua casa."),
    ("descricao", "Descrever algo", "Dizer como algo é.",
     "Descrever é contar como uma pessoa, lugar ou objeto é: tamanho, cor, quantidade e detalhes.",
     "Minha casa é pequena. Tem dois quartos e uma cozinha amarela.",
     "Descreva a sua casa ou o seu bairro em três frases."),
    ("opiniao", "Dar sua opinião", "Dizer o que pensa.",
     "Opinião é o que você acha, não um fato. É comum começar com “eu acho que” ou “na minha opinião”.",
     "Eu acho que estudar é importante. Na minha opinião, a praça precisa de mais luz.",
     "Dê sua opinião sobre o transporte do seu bairro em duas frases."),
    ("carta", "Escrever uma carta", "Saudação, mensagem, despedida.",
     "Uma carta tem saudação inicial, mensagem e despedida com assinatura. Hoje é menos comum, mas ainda aparece em documentos e reclamações.",
     "Olá, dona Rosa! Escrevo para contar que estou bem e trabalhando. Um abraço, Pedro.",
     "Escreva uma carta curta para um parente que mora longe."),
    ("email", "Escrever um e-mail", "Assunto, saudação, mensagem.",
     "O e-mail precisa de assunto claro, saudação, mensagem objetiva e despedida. O assunto ajuda quem recebe a entender o pedido.",
     "Assunto: Matrícula. Bom dia, gostaria de saber se ainda há vagas. Obrigado, Ana.",
     "Escreva um e-mail pedindo informação sobre um curso."),
]


def _frases() -> list[Item]:
    itens: list[Item] = []
    for i, (fid, titulo, sub, explicacao, exemplo, pratica) in enumerate(FRASES):
        itens.append((
            f"alfa-frase-{fid}",
            titulo,
            sub,
            "Intermediário",
            8 + i // 3,
            15,
            i < 2,
            [
                ("explanation", "Como montar", explicacao),
                ("example", "Exemplos", exemplo),
                ("practice", "Escreva", pratica),
                ("check", "Revisão",
                 "Releia o que escreveu: faz sentido? Tem ponto final? Começa com letra maiúscula? "
                 "Uma frase por linha já ajuda a conferir."),
                ("next", "Avance",
                 "Sua escrita está evoluindo. Leia em voz alta: se travar, corte a frase em duas."),
            ],
        ))
    return itens


# ── Textos do dia a dia ──────────────────────────────────────────────────
TEXTOS: list[tuple[str, str, str, str, str, str]] = [
    ("receita", "Ler uma receita", "Ingredientes e modo de fazer.",
     "Uma receita tem duas partes: ingredientes (o que usar e quanto) e modo de fazer (a ordem dos passos). Ler a receita inteira antes de começar evita erro.",
     "Bolo de fubá simples — Ingredientes: 2 ovos, 1 xícara de fubá, 1 xícara de açúcar, 1 xícara de leite, 2 colheres de manteiga. Modo de fazer: misture tudo, unte a forma e asse por 35 minutos em forno médio.",
     "Copie os ingredientes da receita e circule as quantidades."),
    ("noticia", "Ler uma notícia", "O que, onde, quando.",
     "Uma notícia responde a quatro perguntas: o que aconteceu, onde, quando e com quem. O primeiro parágrafo costuma trazer o essencial.",
     "Chuva forte fecha escola em Campinas — As aulas foram suspensas na terça-feira por causa da chuva. A escola reabre na quinta. Os alunos devem levar o material na sexta.",
     "Responda: o que aconteceu? Onde? Quando as aulas voltam?"),
    ("formulario", "Preencher um formulário", "Nome, CPF, endereço.",
     "Formulários pedem dados pessoais. Preencha com letra legível e confira o número do documento antes de entregar. Nunca preencha dados em sites desconhecidos.",
     "FORMULÁRIO DE CADASTRO — Nome: Maria da Silva. Data de nascimento: 12/03/1978. CPF: 000.000.000-00. Endereço: Rua das Flores, 45. Telefone: (11) 99999-0000.",
     "Preencha um formulário de mentira com os seus dados, sem usar documentos reais."),
    ("placa", "Ler placas e avisos", "Informações do dia a dia.",
     "Placas usam frases curtas e letras grandes para serem lidas rápido. Palavras como ATENÇÃO, PROIBIDO e ABERTO mudam o que você pode fazer no lugar.",
     "PLACA DE AVISO — ATENÇÃO: PISO MOLHADO. USE A PORTA LATERAL. ATENDIMENTO DAS 8H ÀS 17H.",
     "Anote três placas que você vê no caminho de casa e o que cada uma pede."),
    ("conta", "Ler uma conta de luz", "Valor, vencimento, código.",
     "Na conta de luz, procure o valor total, a data de vencimento e o código de barras. Pagar depois do vencimento gera multa e juros.",
     "CONTA DE LUZ — Concessionária Luz do Vale. Cliente: José Pereira. Valor: R$ 87,40. Vencimento: 10/12. Código de barras: 34191.79001 01043.510047 91020.150008 1 00000008740.",
     "Encontre em uma conta antiga o valor, o vencimento e o código de barras."),
    ("bula", "Ler uma bula", "Dose, horário, efeitos.",
     "A bula explica para que serve o remédio, a dose, o horário e o que fazer se algo passar mal. Na dúvida, pergunte ao farmacêutico ou ao médico.",
     "BULA — Paracetamol 500 mg. Adultos: 1 comprimido a cada 6 horas. Não ultrapasse 3 gramas por dia. Não use com bebida alcoólica. Se a dor continuar por mais de 3 dias, procure um médico.",
     "Localize a dose e o intervalo entre as doses na bula acima."),
    ("contrato", "Entender um contrato", "Partes, obrigações, assinatura.",
     "Um contrato registra quem combina o quê. Antes de assinar, leia o valor, o prazo e o que acontece se uma das partes desistir.",
     "CONTRATO DE ALUGUEL — Locador: Ana Souza. Locatário: Carlos Lima. Imóvel: Rua do Sol, 12, casa 2. Aluguel: R$ 900,00 por mês, vencimento todo dia 5. Prazo: 12 meses. Assinatura das duas partes.",
     "Liste o valor, o vencimento e o prazo do contrato acima."),
    ("cardapio", "Ler um cardápio", "Pratos, preços, pedido.",
     "No cardápio, cada prato vem com o preço ao lado. Some o que você escolheu antes de pedir para saber quanto vai pagar.",
     "CARDÁPIO — Prato do dia: arroz, feijão, bife e salada — R$ 22,00. Suco de laranja: R$ 6,00. Café com leite: R$ 4,00. Sobremesa: pudim — R$ 7,00.",
     "Calcule quanto custa o prato do dia com suco e pudim."),
    ("onibus", "Ler um horário de ônibus", "Linhas, horários, destino.",
     "O quadro de horários informa a linha, o destino e os horários de saída. Confira se o dia é útil, sábado ou domingo, porque os horários mudam.",
     "HORÁRIO DE ÔNIBUS — Linha 410 Centro/Terminal. Saídas: 6h10, 6h50, 7h30, 12h15, 17h40, 18h20. Dias úteis. Sábados: 7h e 13h.",
     "Descubra a que horas passa o ônibus depois das 12h em um dia útil."),
    ("instrucoes", "Seguir instruções", "Passo a passo de uma tarefa.",
     "Instruções vêm em passos numerados. Siga na ordem e não pule etapas: cada passo depende do anterior.",
     "COMO PAGAR UMA CONTA NO APLICATIVO — 1. Abra o aplicativo do banco. 2. Toque em Pagar. 3. Escolha Conta de consumo. 4. Digite ou fotografe o código de barras. 5. Confira o valor e confirme com sua senha.",
     "Escreva em cinco passos como você faz para pagar uma conta."),
]


def _textos() -> list[Item]:
    itens: list[Item] = []
    for i, (tid, titulo, sub, explicacao, exemplo, pratica) in enumerate(TEXTOS):
        itens.append((
            f"alfa-texto-{tid}",
            titulo,
            sub,
            "Avançado",
            12 + i // 3,
            20,
            i < 2,
            [
                ("explanation", "O que é", explicacao),
                ("example", "Exemplo real", exemplo),
                ("practice", "Faça você", pratica),
                ("check", "Compreensão",
                 "O que você entendeu? Quais informações do texto são mais importantes para a sua vida? "
                 "Releia só a parte que responde a essa pergunta."),
                ("next", "Parabéns",
                 "Você acabou de ler um texto real. Guarde o exemplo: na próxima vez que encontrar um igual, já sabe onde olhar."),
            ],
        ))
    return itens


ALFABETIZACAO: list[Item] = _letras() + _familias() + _temas() + _frases() + _textos()

assert len(ALFABETIZACAO) == 93, f"esperados 93 módulos, encontrados {len(ALFABETIZACAO)}"
assert len({item[0] for item in ALFABETIZACAO}) == 93, "ids duplicados na trilha"
for item in ALFABETIZACAO:
    assert len(item[7]) == 5, f"{item[0]} sem cinco etapas"
    for tipo, _titulo, texto in item[7]:
        assert len(texto.strip()) >= 20, f"{item[0]}/{tipo} curto demais"
