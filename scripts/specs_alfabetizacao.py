"""Atividades de Alfabetização (Jovens e Adultos).

Princípios:

- **Nada de infantilização.** Sem "bebê", "dodói", "tchutchuca"; sem emoji no
  texto. Os exemplos falam de receita, ônibus, conta de luz, bula, crachá,
  formulário — coisas que uma pessoa adulta precisa ler de verdade.
- Cada atividade repete apenas palavras que a etapa do módulo já apresentou.
- Gabaritos numéricos passam por ``numeric_checked`` (expressão avaliada).
"""

from __future__ import annotations

from scripts.activity_spec import (
    fill_blank,
    multiple_choice,
    numeric_checked,
    ordering,
    spec,
    true_false,
)

SPECS: dict = {}

# Palavra-âncora de cada letra (a mesma da etapa de exemplo da trilha).
_LETTERS: dict[str, tuple[str, str]] = {
    "a": ("água", "vogal"),
    "b": ("bola", "consoante"),
    "c": ("casa", "consoante"),
    "d": ("dedo", "consoante"),
    "e": ("escola", "vogal"),
    "f": ("faca", "consoante"),
    "g": ("gato", "consoante"),
    "h": ("hoje", "consoante"),
    "i": ("ilha", "vogal"),
    "j": ("janela", "consoante"),
    "k": ("kiwi", "consoante"),
    "l": ("lua", "consoante"),
    "m": ("mãe", "consoante"),
    "n": ("navio", "consoante"),
    "o": ("olho", "vogal"),
    "p": ("pai", "consoante"),
    "q": ("queijo", "consoante"),
    "r": ("rato", "consoante"),
    "s": ("sol", "consoante"),
    "t": ("tatu", "consoante"),
    "u": ("uva", "vogal"),
    "v": ("vaca", "consoante"),
    "w": ("web", "consoante"),
    "x": ("xícara", "consoante"),
    "y": ("yoga", "consoante"),
    "z": ("zebra", "consoante"),
}

VOWELS = "aeiou"


def _distractors(letter: str, from_start: bool) -> list[str]:
    """Duas palavras de outras letras que NÃO servem para esta pergunta.

    A escolha é determinística e verificada: se por descuido uma distratora
    contiver a letra (ou começar com ela), o build falha em vez de publicar uma
    questão com duas respostas certas.
    """
    picks: list[str] = []
    for other in sorted(_LETTERS):
        if other == letter or (_LETTERS[other][1] == _LETTERS[letter][1] and from_start):
            continue
        word = _LETTERS[other][0]
        if from_start and word.startswith(letter):
            continue
        if letter in word:
            continue
        if word in picks:
            continue
        picks.append(word)
        if len(picks) == 2:
            break
    if len(picks) < 2:
        raise AssertionError(f"sem distratoras suficientes para a letra {letter!r}")
    return picks


# ── Letras ───────────────────────────────────────────────────────────────
for _letter, (_word, _kind) in _LETTERS.items():
    _upper = _letter.upper()
    _vogal = _kind == "vogal"

    if _vogal:
        _pergunta = f"Qual palavra começa com a vogal {_upper}, como em “{_word}”?"
        _explicacao = (
            f"“{_word}” começa com a vogal {_upper}. Diga a palavra devagar e prolongue o "
            "primeiro som: ele é a vogal de entrada."
        )
    else:
        _pergunta = f"Qual palavra tem a letra {_upper}, como em “{_word}”?"
        _explicacao = (
            f"“{_word}” é a palavra-âncora da letra {_upper}. Aponte cada letra da palavra "
            "e procure o desenho que você acabou de estudar."
        )

    SPECS[f"alfa-letra-{_letter}"] = spec(
        [
            f"Reconhecer a letra {_upper} no início, no meio e no fim de palavras.",
            f"Associar o desenho da letra {_upper} ao seu som.",
            f"Escrever a letra {_upper} em letra de forma legível.",
        ],
        [
            multiple_choice(
                f"alfa-letra-{_letter}-tipo",
                f"A letra {_upper}, como em “{_word}”, é:",
                ["vogal", "consoante", "número"],
                _kind,
                (
                    f"{_upper} é uma {_kind}. As vogais são A, E, I, O, U; as demais "
                    "letras do alfabeto são consoantes e precisam de uma vogal para "
                    "formar sílaba."
                ),
            ),
            multiple_choice(
                f"alfa-letra-{_letter}-reconhecer",
                _pergunta,
                [_word] + _distractors(_letter, from_start=_vogal),
                _word,
                _explicacao,
            ),
            fill_blank(
                f"alfa-letra-{_letter}-palavra",
                f"Complete com a letra que falta, como no exemplo “{_word}”: __{_word[1:]}",
                [_letter],
                (
                    f"A palavra é “{_word}”, escrita com {_upper} no começo. Em português, "
                    "a primeira letra fica maiúscula no início da frase e minúscula no "
                    "meio dela."
                ),
            ),
        ],
    )

# Letras que aparecem pouco em português precisam de contexto, não de silêncio.
for _letter in ("k", "w", "y"):
    _upper = _letter.upper()
    _word = _LETTERS[_letter][0]
    SPECS[f"alfa-letra-{_letter}"].activities.append(
        true_false(
            f"alfa-letra-{_letter}-estrangeira",
            f"O {_upper} aparece em muitas palavras de origem portuguesa, como “{_word}”.",
            False,
            (
                f"O {_upper} aparece sobretudo em nomes próprios e palavras estrangeiras "
                f"incorporadas ao português, como “{_word}”. Reconhecer isso evita "
                "estranhar a letra em cartazes, marcas e rótulos."
            ),
        )
    )

# ── Famílias silábicas ───────────────────────────────────────────────────
_FAMILIAS = {
    "b": ("bola", "BA", ["BA", "BE", "BI", "BO", "BU"]),
    "c": ("casa", "CA", ["CA", "CO", "CU", "CE", "CI"]),
    "d": ("dado", "DA", ["DE", "DI", "DA", "DO", "DU"]),
    "f": ("faca", "FA", ["FA", "FE", "FI", "FO", "FU"]),
    "g": ("gato", "GA", ["GO", "GA", "GE", "GI", "GU"]),
    "h": ("hora", "HO", ["HA", "HE", "HI", "HO", "HU"]),
    "j": ("jaca", "JA", ["JA", "JE", "JI", "JO", "JU"]),
    "k": ("kiwi", "KI", ["KA", "KE", "KI", "KO", "KU"]),
    "l": ("lápis", "LA", ["LA", "LE", "LI", "LO", "LU"]),
    "m": ("mala", "MA", ["MA", "ME", "MI", "MO", "MU"]),
    "n": ("nada", "NA", ["NA", "NE", "NI", "NO", "NU"]),
    "p": ("pato", "PA", ["PA", "PE", "PI", "PO", "PU"]),
    "q": ("queijo", "QUE", ["QUA", "QUE", "QUI", "QUO"]),
    "r": ("rato", "RA", ["RA", "RE", "RI", "RO", "RU"]),
    "s": ("sapo", "SA", ["SA", "SE", "SI", "SO", "SU"]),
    "t": ("tatu", "TA", ["TA", "TE", "TI", "TO", "TU"]),
    "v": ("vaca", "VA", ["VA", "VE", "VI", "VO", "VU"]),
    "x": ("xícara", "XI", ["XA", "XE", "XI", "XO", "XU"]),
    "z": ("zebra", "ZE", ["ZA", "ZE", "ZI", "ZO", "ZU"]),
}

for _consonant, (_word, _syllable, _family) in _FAMILIAS.items():
    _upper = _consonant.upper()
    _option_set = list(dict.fromkeys(_family + [f"{_upper}I", f"{_upper}O"]))[:5]
    if _syllable not in _option_set:
        _option_set[-1] = _syllable
    SPECS[f"alfa-silaba-{_consonant}"] = spec(
        [
            f"Formar as sílabas da família do {_upper} com cada vogal.",
            f"Separar em sílabas palavras que começam com {_upper}.",
            "Ler palavras novas apoiando-se na família silábica.",
        ],
        [
            multiple_choice(
                f"alfa-silaba-{_consonant}-primeira",
                f"A palavra “{_word}” começa com qual sílaba?",
                _option_set,
                _syllable,
                (
                    f"“{_word}” começa com {_syllable}. Bata uma palma em cada pedaço "
                    "da palavra: cada palma é uma sílaba."
                ),
            ),
            ordering(
                f"alfa-silaba-{_consonant}-familia",
                f"Coloque as sílabas da família do {_upper} na ordem das vogais A, E, I, O, U.",
                [s for s in _family],
            ),
        ],
    )

for _consonant in ("w", "y"):
    SPECS[f"alfa-silaba-{_consonant}"] = spec(
        [
            f"Reconhecer o {_consonant.upper()} em palavras estrangeiras de uso comum.",
            "Perceber que nem toda letra do alfabeto tem família silábica completa em português.",
        ],
        [
            true_false(
                f"alfa-silaba-{_consonant}-raro",
                f"O {_consonant.upper()} tem uma família silábica completa em português, "
                "como WA, WE, WI, WO, WU em todas as palavras.",
                False,
                (
                    f"O {_consonant.upper()} aparece em poucas palavras, quase sempre "
                    "estrangeiras ou nomes próprios. Ele não forma família silábica "
                    "completa como B, C, D ou M."
                ),
            ),
            multiple_choice(
                f"alfa-silaba-{_consonant}-reconhecer",
                f"Qual destas palavras tem o {_consonant.upper()}?",
                [_LETTERS[_consonant][0], "bola", "casa"],
                _LETTERS[_consonant][0],
                (
                    f"“{_LETTERS[_consonant][0]}” é uma das poucas palavras com "
                    f"{_consonant.upper()} que aparecem no dia a dia — em marcas, cardápios "
                    "e cartazes."
                ),
            ),
        ],
    )

# ── Temas de vocabulário ─────────────────────────────────────────────────
_TEMAS = {
    "corpo": ("mão", {"mão": "mão", "pé": "pé", "olho": "olho", "boca": "boca", "cabeça": "cabeça"}),
    "casa": ("porta", {"porta": "porta", "mesa": "mesa", "cama": "cama", "janela": "janela"}),
    "comida": ("arroz", {"arroz": "arroz", "feijão": "feijão", "pão": "pão", "café": "café"}),
    "familia": ("mãe", {"mãe": "mãe", "pai": "pai", "filho": "filho", "avó": "avó"}),
    "rua": ("ônibus", {"ônibus": "ônibus", "praça": "praça", "calçada": "calçada"}),
    "cores": ("vermelho", {"vermelho": "vermelho", "azul": "azul", "verde": "verde"}),
    "dias": ("segunda", {"segunda": "segunda-feira", "janeiro": "janeiro", "semana": "semana"}),
    "animais": ("cachorro", {"cachorro": "cachorro", "gato": "gato", "pássaro": "pássaro"}),
    "trabalho": ("emprego", {"emprego": "emprego", "salário": "salário", "contrato": "contrato"}),
    "saude": ("médico", {"médico": "médico", "remédio": "remédio", "vacina": "vacina"}),
    "documentos": ("CPF", {"CPF": "CPF", "RG": "RG", "certidão": "certidão"}),
    "natureza": ("chuva", {"sol": "sol", "chuva": "chuva", "árvore": "árvore"}),
    "emocoes": ("alegria", {"alegria": "alegria", "tristeza": "tristeza", "saudade": "saudade"}),
    "compras": ("preço", {"preço": "preço", "troco": "troco", "nota fiscal": "nota fiscal"}),
    "transporte": ("ônibus", {"ônibus": "ônibus", "metrô": "metrô", "passagem": "passagem"}),
    "escola": ("aula", {"aula": "aula", "caderno": "caderno", "professor": "professor"}),
    "dinheiro": ("real", {"real": "real", "centavo": "centavo", "poupança": "poupança"}),
    "tempo": ("hoje", {"hoje": "hoje", "amanhã": "amanhã", "ontem": "ontem"}),
    "tecnologia": ("celular", {"celular": "celular", "senha": "senha", "aplicativo": "aplicativo"}),
    "musica": ("canção", {"canção": "canção", "ritmo": "ritmo", "violão": "violão"}),
    "esporte": ("futebol", {"futebol": "futebol", "time": "time", "treino": "treino"}),
    "cidade": ("bairro", {"bairro": "bairro", "prefeitura": "prefeitura", "praça": "praça"}),
    "campo": ("roça", {"roça": "roça", "colheita": "colheita", "semente": "semente"}),
    "mar": ("praia", {"praia": "praia", "onda": "onda", "areia": "areia"}),
}

_TEMA_FRASES = {
    "corpo": ("Lavei a ___ antes de comer.", "mão"),
    "casa": ("Abri a ___ para entrar em casa.", "porta"),
    "comida": ("O ___ está no fogo desde as seis.", "feijão"),
    "familia": ("Minha ___ chegou de viagem ontem.", "mãe"),
    "rua": ("O ___ das seis passa na esquina.", "ônibus"),
    "cores": ("O céu sem nuvens fica ___.", "azul"),
    "dias": ("A feira começa na ___-feira.", "segunda"),
    "animais": ("O ___ latiu para o carteiro.", "cachorro"),
    "trabalho": ("Meu ___ novo começa em março.", "emprego"),
    "saude": ("Marquei consulta com o ___.", "médico"),
    "documentos": ("Levei o ___ ao banco.", "CPF"),
    "natureza": ("A ___ forte alagou a rua.", "chuva"),
    "emocoes": ("Sinto ___ de quem mora longe.", "saudade"),
    "compras": ("Conferi o ___ antes de sair.", "troco"),
    "transporte": ("A ___ do ônibus custa R$ 4,40.", "passagem"),
    "escola": ("Anotei a ___ no caderno.", "aula"),
    "dinheiro": ("Guardo um pouco na ___ todo mês.", "poupança"),
    "tempo": ("___ é terça, o pagamento cai.", "hoje"),
    "tecnologia": ("Esqueci a ___ do celular.", "senha"),
    "musica": ("A banda tocou uma ___ nova.", "canção"),
    "esporte": ("O ___ começou às quatro da tarde.", "futebol"),
    "cidade": ("O ___ tem feira livre aos domingos.", "bairro"),
    "campo": ("A ___ de milho é em julho.", "colheita"),
    "mar": ("A ___ estava cheia de conchas.", "areia"),
}

for _tid, (_anchor, _vocab) in _TEMAS.items():
    _frase, _resposta = _TEMA_FRASES[_tid]
    _termos = list(_vocab)
    _opcoes = _termos[:3] if _termos.index(_resposta) < 3 else [_resposta] + _termos[:2]
    SPECS[f"alfa-tema-{_tid}"] = spec(
        [
            "Ler e reconhecer palavras do vocabulário essencial do dia a dia.",
            "Usar o vocabulário do tema em uma frase completa.",
            "Separar uma palavra do tema em sílabas.",
        ],
        [
            fill_blank(
                f"alfa-tema-{_tid}-frase",
                _frase,
                [_resposta],
                (
                    f"A palavra que completa a frase é “{_resposta}”. Ler a frase inteira "
                    "e perguntar “qual palavra do tema cabe aqui?” é mais eficaz do que "
                    "adivinhar pela primeira letra."
                ),
            ),
            multiple_choice(
                f"alfa-tema-{_tid}-vocabulario",
                f"O que a palavra “{_anchor}” nomeia?",
                [
                    f"algo do tema {_tid}",
                    "um número",
                    "uma ação que não existe",
                ],
                f"algo do tema {_tid}",
                f"“{_anchor}” faz parte do vocabulário de {_tid} e nomeia algo concreto.",
            ),
        ],
    )

# ── Frases ───────────────────────────────────────────────────────────────
SPECS["alfa-frase-simples"] = spec(
    [
        "Identificar sujeito e verbo em uma frase curta.",
        "Escrever frases com sujeito e verbo.",
    ],
    [
        multiple_choice(
            "alfa-frase-simples-sujeito",
            "Em “Ela canta”, quem é o sujeito?",
            ["Ela", "canta", "não tem sujeito"],
            "Ela",
            "“Ela” é o sujeito, ou seja, quem faz a ação. “Canta” é o verbo, a ação. "
            "Toda frase precisa desses dois pedaços para fazer sentido.",
        ),
        ordering(
            "alfa-frase-simples-ordem",
            "Monte a frase na ordem em que se lê:",
            ["Eu", "leio", "um", "livro"],
        ),
    ],
)

SPECS["alfa-frase-complemento"] = spec(
    [
        "Perceber que alguns verbos pedem complemento.",
        "Completar frases com o objeto que faz sentido.",
    ],
    [
        fill_blank(
            "alfa-frase-complemento-lacuna",
            "Complete: “Eu leio um ___.”",
            ["livro", "jornal", "texto"],
            "“Ler” pede aquilo que se lê: um livro, um jornal, um texto. Sem esse "
            "complemento, a frase fica incompleta.",
        ),
        multiple_choice(
            "alfa-frase-complemento-identificar",
            "Qual frase está completa?",
            [
                "Ela comprou leite.",
                "Ela comprou.",
                "Comprou leite ela.",
                "Ela.",
            ],
            "Ela comprou leite.",
            "“Ela comprou leite” tem sujeito, verbo e complemento. “Ela comprou” deixa a "
            "pergunta “comprou o quê?” sem resposta.",
        ),
    ],
)

SPECS["alfa-frase-pergunta"] = spec(
    [
        "Reconhecer palavras de interrogação.",
        "Escrever perguntas com ponto de interrogação.",
    ],
    [
        fill_blank(
            "alfa-frase-pergunta-pontuacao",
            "Complete o sinal: “Onde você mora___”",
            ["?"],
            "Pergunta termina com ponto de interrogação. A entonação da voz também sobe "
            "no fim, e o sinal escrito registra essa subida.",
        ),
        multiple_choice(
            "alfa-frase-pergunta-palavra",
            "Qual palavra NÃO serve para começar uma pergunta?",
            ["Como", "Quando", "Porque", "Portanto"],
            "Portanto",
            "“Portanto” é uma palavra de conclusão, usada para ligar ideias. Como, "
            "quando, onde e por quê abrem perguntas.",
        ),
    ],
)

SPECS["alfa-frase-negativa"] = spec(
    [
        "Transformar frases afirmativas em negativas.",
        "Reconhecer o efeito de sentido do NÃO.",
    ],
    [
        fill_blank(
            "alfa-frase-negativa-transformar",
            "Passe para a negativa: “Eu tenho documento.” → “Eu ___ tenho documento.”",
            ["não"],
            "Basta colocar “não” antes do verbo: “Eu não tenho documento”. O sentido "
            "muda completamente — essa é a diferença entre ter e não ter documento.",
        ),
        true_false(
            "alfa-frase-negativa-sentido",
            "“Nós não temos troco” e “Nós temos troco” significam a mesma coisa.",
            False,
            "O “não” inverte o sentido. Na loja, essa diferença decide se você "
            "consegue pagar com cédula maior.",
        ),
    ],
)

SPECS["alfa-frase-bilhete"] = spec(
    [
        "Escrever um bilhete com destinatário, recado e assinatura.",
        "Conferir se um bilhete contém as três partes.",
    ],
    [
        multiple_choice(
            "alfa-frase-bilhete-partes",
            "O que um bilhete precisa ter para cumprir sua função?",
            [
                "Destinatário, recado e assinatura.",
                "Só o recado.",
                "Data de nascimento e CPF.",
                "Título, sumário e referências.",
            ],
            "Destinatário, recado e assinatura.",
            "Sem destinatário ninguém sabe para quem é; sem assinatura ninguém sabe quem "
            "escreveu. O bilhete é curto, mas completo.",
        ),
        ordering(
            "alfa-frase-bilhete-ordem",
            "Organize o bilhete na ordem em que se lê:",
            ["Mãe,", "fui ao mercado.", "Volto às 5.", "— Ana"],
        ),
    ],
)

SPECS["alfa-frase-lista"] = spec(
    ["Montar uma lista numerada.", "Usar lista para não esquecer tarefas."],
    [
        ordering(
            "alfa-frase-lista-ordem",
            "Organize a lista de compras em ordem alfabética:",
            ["Arroz", "Café", "Feijão", "Óleo"],
        ),
        true_false(
            "alfa-frase-lista-formato",
            "Numa lista, cada item deve ficar em uma linha separada.",
            True,
            "Uma linha por item deixa a lista fácil de conferir no mercado e de riscar "
            "o que já foi comprado.",
        ),
    ],
)

SPECS["alfa-frase-recado"] = spec(
    ["Anotar recado com nome, horário e pedido.", "Reconhecer informação essencial em um recado."],
    [
        fill_blank(
            "alfa-frase-recado-horario",
            "No recado “Dona Maria ligou. Pediu para retornar até as 10h”, a que horas "
            "termina o prazo para retornar?",
            ["10h", "10 horas", "dez horas"],
            "O prazo é até as 10h. Horário é a informação mais perecível de um recado: "
            "sem ele, o retorno perde a utilidade.",
        ),
        multiple_choice(
            "alfa-frase-recado-essencial",
            "Qual dado NÃO pode faltar em um recado?",
            ["Quem ligou", "O time do futebol", "A cor da parede", "O sabor do bolo"],
            "Quem ligou",
            "Um recado precisa de quem ligou, o que queria e para quem. O resto é "
            "detalhe dispensável.",
        ),
    ],
)

SPECS["alfa-frase-convite"] = spec(
    ["Escrever convite com o quê, quando e onde.", "Conferir se os três dados estão presentes."],
    [
        multiple_choice(
            "alfa-frase-convite-dados",
            "Um convite sem o QUANDO causa qual problema?",
            [
                "A pessoa não consegue se organizar para ir.",
                "Ninguém entende o assunto.",
                "Falta a assinatura.",
                "O convite fica longo demais.",
            ],
            "A pessoa não consegue se organizar para ir.",
            "Sem data e hora, o convidado não sabe se pode ir. O quê, quando e onde são "
            "o esqueleto de qualquer convite.",
        ),
        fill_blank(
            "alfa-frase-convite-lacuna",
            "Complete o convite: “Venha! Dia 15, às 15h, ___ casa da vovó.”",
            ["na"],
            "“Na casa da vovó” indica o lugar. O “na” é a preposição que liga a ação ao "
            "lugar.",
        ),
    ],
)

SPECS["alfa-frase-descricao"] = spec(
    ["Descrever com tamanho, cor e detalhes.", "Reconhecer detalhes concretos em uma descrição."],
    [
        multiple_choice(
            "alfa-frase-descricao-detalhe",
            "Qual frase descreve melhor uma casa?",
            [
                "Tem dois quartos e uma cozinha amarela.",
                "É boa.",
                "Existe.",
                "Muito bonita e legal.",
            ],
            "Tem dois quartos e uma cozinha amarela.",
            "Descrever é dar informação concreta: quantidade, cor, tamanho. “É boa” não "
            "ajuda ninguém a imaginar a casa.",
        ),
        true_false(
            "alfa-frase-descricao-fato",
            "“Minha casa é pequena” é uma descrição, não uma opinião.",
            True,
            "Tamanho é uma característica observável. Opinião seria “minha casa é a "
            "melhor do bairro”.",
        ),
    ],
)

SPECS["alfa-frase-opiniao"] = spec(
    ["Diferenciar fato de opinião.", "Expressar opinião com fórmula educada."],
    [
        multiple_choice(
            "alfa-frase-opiniao-fato",
            "Qual destas frases é um FATO, não uma opinião?",
            [
                "A praça tem três bancos.",
                "A praça precisa de mais luz.",
                "Eu acho a praça bonita.",
                "Na minha opinião, a praça é boa.",
            ],
            "A praça tem três bancos.",
            "Dá para contar os bancos e conferir. As outras frases dependem de quem fala "
            "— são opiniões.",
        ),
        fill_blank(
            "alfa-frase-opiniao-formula",
            "Complete com a palavra que abre a fórmula de opinião: “___ minha opinião, "
            "o transporte precisa melhorar.”",
            ["Na"],
            "“Na minha opinião” avisa o leitor que vem um julgamento, não um dado. Isso "
            "evita discussão desnecessária.",
        ),
    ],
)

SPECS["alfa-frase-carta"] = spec(
    ["Reconhecer saudação, mensagem e despedida em uma carta.", "Escrever uma carta curta."],
    [
        ordering(
            "alfa-frase-carta-estrutura",
            "Organize a carta na ordem em que se lê:",
            ["Olá, dona Rosa!", "Escrevo para contar que estou bem.", "Um abraço,", "Pedro"],
        ),
        true_false(
            "alfa-frase-carta-despedida",
            "Uma carta pode terminar sem despedida e sem assinatura.",
            False,
            "A despedida com assinatura mostra quem escreveu e encerra a conversa. Sem "
            "ela, a carta parece inacabada.",
        ),
    ],
)

SPECS["alfa-frase-email"] = spec(
    ["Escrever e-mail com assunto claro.", "Reconhecer a função do campo assunto."],
    [
        multiple_choice(
            "alfa-frase-email-assunto",
            "Você quer saber se ainda há vagas em um curso. Qual assunto é melhor?",
            [
                "Vagas no curso de informática",
                "Oi",
                "URGENTE!!!",
                "(sem assunto)",
            ],
            "Vagas no curso de informática",
            "O assunto diz em poucas palavras o que a mensagem quer. “Oi” e “URGENTE” "
            "não ajudam quem recebe a separar o que é importante.",
        ),
        fill_blank(
            "alfa-frase-email-campo",
            "No e-mail, o campo que resume o tema da mensagem se chama ___.",
            ["assunto"],
            "É o campo “Assunto”. Um bom assunto tem de 3 a 6 palavras e diz exatamente "
            "o que você precisa.",
        ),
    ],
)

# ── Textos do dia a dia ──────────────────────────────────────────────────
SPECS["alfa-texto-onibus"] = spec(
    [
        "Localizar horário de saída em um quadro de ônibus.",
        "Diferenciar horários de dias úteis e de sábado.",
    ],
    [
        multiple_choice(
            "alfa-texto-onibus-horario",
            "No quadro “Saídas: 6h10, 6h50, 7h30, 12h15, 17h40, 18h20 — dias úteis”, "
            "qual é o primeiro ônibus depois das 12h?",
            ["12h15", "17h40", "11h30", "7h30"],
            "12h15",
            "Depois das 12h, o próximo horário da lista é 12h15. Ler a lista em ordem é "
            "mais seguro do que procurar o número mais parecido.",
        ),
        true_false(
            "alfa-texto-onibus-sabado",
            "Aos sábados, o ônibus da linha 410 sai nos mesmos horários dos dias úteis.",
            False,
            "O quadro informa “Dias úteis” e depois “Sábados: 7h e 13h”. Sábado tem "
            "menos horários — chegar no ponto às 6h10 de sábado é esperar em vão.",
        ),
        fill_blank(
            "alfa-texto-onibus-linha",
            "A linha do ônibus do exemplo é a ___.",
            ["410", "linha 410"],
            "A linha é a 410, que vai do Centro ao Terminal. O número da linha é o que "
            "você confere na frente do ônibus antes de entrar.",
        ),
    ],
)

SPECS["alfa-texto-receita"] = spec(
    [
        "Distinguir ingredientes de modo de fazer.",
        "Localizar quantidades em uma receita.",
    ],
    [
        multiple_choice(
            "alfa-texto-receita-parte",
            "Em uma receita, “2 ovos, 1 xícara de fubá” pertence a qual parte?",
            ["Ingredientes", "Modo de fazer", "Tempo de forno", "Dicas"],
            "Ingredientes",
            "Lista de quantidades = ingredientes. A ordem das ações = modo de fazer. "
            "Separar as duas partes evita esquecer um item.",
        ),
        numeric_checked(
            "alfa-texto-receita-minutos",
            "A receita manda assar por 35 minutos. Quantos minutos faltam se já se "
            "passaram 12?",
            "35 - 12",
            "35 − 12 = 23 minutos. Contar o tempo no forno evita bolo cru no meio.",
            unit="minutos",
        ),
    ],
)

SPECS["alfa-texto-formulario"] = spec(
    ["Identificar campos de um formulário.", "Reconhecer quando NÃO preencher dados."],
    [
        multiple_choice(
            "alfa-texto-formulario-perigo",
            "Um site desconhecido pede seu CPF e sua senha do banco por mensagem. O que fazer?",
            [
                "Não preencher e não responder.",
                "Preencher só o CPF.",
                "Responder com a senha se o site parecer bonito.",
                "Ligar para o número da mensagem.",
            ],
            "Não preencher e não responder.",
            "Banco não pede senha por mensagem. Dado enviado não volta atrás: a regra é "
            "não preencher o que você não sabe para que serve.",
        ),
        fill_blank(
            "alfa-texto-formulario-dado",
            "No formulário do exemplo, o número do documento é o ___.",
            ["CPF"],
            "É o CPF, no formato 000.000.000-00. Confira dígito por dígito antes de "
            "entregar: erro de digitação em documento dá trabalho para corrigir.",
        ),
    ],
)

SPECS["alfa-texto-placa"] = spec(
    ["Interpretar placas e avisos curtos.", "Reconhecer palavras de proibição e permissão."],
    [
        multiple_choice(
            "alfa-texto-placa-piso",
            "A placa diz “ATENÇÃO: PISO MOLHADO. USE A PORTA LATERAL”. O que você deve fazer?",
            [
                "Usar a porta lateral com cuidado.",
                "Correr pelo corredor.",
                "Ignorar o aviso.",
                "Esperar alguém limpar e passar pelo piso molhado.",
            ],
            "Usar a porta lateral com cuidado.",
            "A placa junta um alerta (piso molhado) e uma instrução (use a lateral). Ler "
            "as duas partes evita queda.",
        ),
        true_false(
            "alfa-texto-placa-horario",
            "A placa “ATENDIMENTO DAS 8H ÀS 17H” significa que o atendimento começa às 17h.",
            False,
            "“Das 8h às 17h” é o intervalo inteiro: começa às 8h e termina às 17h. "
            "Chegar às 17h05 é chegar depois do fechamento.",
        ),
    ],
)

SPECS["alfa-texto-bula"] = spec(
    ["Localizar dose e intervalo entre doses em uma bula.", "Reconhecer limite diário."],
    [
        numeric_checked(
            "alfa-texto-bula-comprimidos",
            "A bula diz “1 comprimido a cada 6 horas”. Quantos comprimidos no máximo em "
            "24 horas?",
            "24 / 6",
            "24 ÷ 6 = 4 comprimidos por dia. Passar disso é exceder a dose indicada; na "
            "dúvida, pergunte ao farmacêutico.",
            unit="comprimidos",
            tolerance=0,
        ),
        multiple_choice(
            "alfa-texto-bula-duvida",
            "A dor continua há mais de 3 dias. A bula manda procurar um médico. O que "
            "fazer?",
            [
                "Procurar atendimento médico.",
                "Dobrar a dose.",
                "Parar de tomar e não falar com ninguém.",
                "Tomar com bebida alcoólica.",
            ],
            "Procurar atendimento médico.",
            "A bula alerta justamente para isso: dor que passa de 3 dias precisa de "
            "avaliação, não de mais remédio.",
        ),
    ],
)

SPECS["alfa-texto-conta"] = spec(
    ["Localizar valor, vencimento e código de barras em uma conta.", "Entender o efeito do atraso."],
    [
        fill_blank(
            "alfa-texto-conta-valor",
            "Na conta “Valor: R$ 87,40. Vencimento: 10/12”, qual é o dia do vencimento?",
            ["10", "10/12", "dia 10"],
            "O vencimento é o dia 10. O que vem depois da barra é o mês: 12, dezembro.",
        ),
        multiple_choice(
            "alfa-texto-conta-atraso",
            "O que acontece ao pagar a conta depois do vencimento?",
            [
                "Entram multa e juros.",
                "O valor diminui.",
                "Nada muda.",
                "A conta é cancelada.",
            ],
            "Entram multa e juros.",
            "Atraso gera multa e juros sobre o valor. Anotar o vencimento no calendário "
            "sai mais barato do que pagar depois.",
        ),
    ],
)

SPECS["alfa-texto-contrato"] = spec(
    ["Identificar partes, valor, prazo e vencimento em um contrato.", "Reconhecer o que conferir antes de assinar."],
    [
        multiple_choice(
            "alfa-texto-contrato-conferir",
            "Antes de assinar um contrato de aluguel, o que é essencial conferir?",
            [
                "Valor, prazo e o que acontece se uma parte desistir.",
                "A cor do papel.",
                "O nome do bairro vizinho.",
                "Quem digitou o documento.",
            ],
            "Valor, prazo e o que acontece se uma parte desistir.",
            "Esses três pontos definem quanto você paga, por quanto tempo e qual o custo "
            "de sair antes. O resto é secundário.",
        ),
        numeric_checked(
            "alfa-texto-contrato-anual",
            "O contrato tem aluguel de R$ 900,00 por mês e prazo de 12 meses. Quanto se "
            "paga no total do contrato?",
            "900 * 12",
            "900 × 12 = R$ 10.800,00 ao longo do contrato. Saber o total evita surpresa "
            "no orçamento anual.",
            unit="reais",
            tolerance=0.01,
        ),
    ],
)

SPECS["alfa-texto-cardapio"] = spec(
    ["Somar preços de um cardápio antes de pedir.", "Comparar o total com o dinheiro disponível."],
    [
        numeric_checked(
            "alfa-texto-cardapio-total",
            "Prato do dia R$ 22,00 + suco R$ 6,00 + pudim R$ 7,00. Qual é o total?",
            "22 + 6 + 7",
            "22 + 6 + 7 = R$ 35,00. Somar antes de pedir evita passar do dinheiro que "
            "você tem na carteira.",
            unit="reais",
        ),
        true_false(
            "alfa-texto-cardapio-troco",
            "Pedindo o prato do dia e o suco (R$ 28,00) e pagando com R$ 50,00, o troco "
            "é R$ 22,00.",
            True,
            "50 − 28 = 22. Conferir o troco na hora é a última chance de corrigir um erro "
            "de caixa.",
        ),
    ],
)

SPECS["alfa-texto-instrucoes"] = spec(
    ["Seguir instruções numeradas na ordem.", "Perceber a consequência de pular etapas."],
    [
        ordering(
            "alfa-texto-instrucoes-ordem",
            "Ordene os passos de “pagar uma conta no aplicativo”:",
            [
                "Abra o aplicativo do banco.",
                "Toque em Pagar.",
                "Digite ou fotografe o código de barras.",
                "Confira o valor e confirme com sua senha.",
            ],
        ),
        true_false(
            "alfa-texto-instrucoes-pular",
            "Em instruções numeradas, pular uma etapa geralmente não causa problema.",
            False,
            "Cada passo depende do anterior. Pular o passo de conferir o valor, por "
            "exemplo, pode fazer você pagar a conta errada.",
        ),
    ],
)

SPECS["alfa-texto-noticia"] = spec(
    ["Responder o quê, onde, quando de uma notícia.", "Localizar a informação essencial no primeiro parágrafo."],
    [
        multiple_choice(
            "alfa-texto-noticia-onde",
            "“Chuva forte fecha escola em Campinas.” Onde aconteceu o fato?",
            ["Campinas", "São Paulo", "Brasília", "Campinas do Sul"],
            "Campinas",
            "A cidade aparece logo no início da manchete. O primeiro parágrafo costuma "
            "trazer o essencial: o que, onde, quando e com quem.",
        ),
        multiple_choice(
            "alfa-texto-noticia-quando",
            "O texto diz “A escola reabre na quinta” e “levar o material na sexta”. "
            "Quando os alunos voltam a estudar?",
            ["Na quinta-feira", "Na sexta-feira", "Na terça-feira", "Não voltam"],
            "Na quinta-feira",
            "A reabertura é na quinta; sexta é a orientação sobre o material. Separar "
            "as duas datas evita chegar no dia errado.",
        ),
    ],
)


def build() -> dict:
    """Importado por ``scripts/activities_by_module``: devolve as specs prontas."""
    return SPECS
