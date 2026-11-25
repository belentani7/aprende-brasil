"""Atividades de Idiomas (32 módulos) — inglês, espanhol e português.

Os objetivos são descritos em termos de **o que a pessoa consegue fazer**
(pedir preço, descrever a família, escrever e-mail), não em níveis de
certificação. Não há equivalência acreditada com o MCER: níveis A1/A2 são usados
apenas como referência interna de sequência.
"""

from __future__ import annotations

from scripts.activity_spec import (
    fill_blank,
    matching,
    multiple_choice,
    ordering,
    spec,
    true_false,
)

SPECS: dict = {}


def add(module_id: str, objectives: list[str], activities: list[dict]) -> None:
    SPECS[module_id] = spec(objectives, activities)


# ── Inglês ───────────────────────────────────────────────────────────────
add(
    "idio-cumprimentos-en",
    ["Cumprimentar conforme a hora do dia.", "Despedir-se e responder a um cumprimento."],
    [
        multiple_choice(
            "idio-cumprimentos-en-hora",
            "São 20h. Qual cumprimento é o mais adequado?",
            ["Good evening", "Good morning", "Good afternoon", "Good night"],
            "Good evening",
            "Good evening é a chegada à noite. Good night é despedida usada ao ir dormir.",
        ),
        matching(
            "idio-cumprimentos-en-pares",
            "Ligue cada expressão à tradução:",
            [
                ("Good morning", "bom dia"),
                ("Good afternoon", "boa tarde"),
                ("Good evening", "boa noite (chegando)"),
                ("Goodbye", "até logo"),
            ],
            "Cumprimento de chegada e despedida são expressões diferentes — o erro comum é "
            "usar good night ao chegar.",
        ),
        fill_blank(
            "idio-cumprimentos-en-resposta",
            "How are you? — I'm fine, ___ you.",
            ["thank"],
            "A resposta padrão é “I'm fine, thank you”. Com “thank you” você agradece e "
            "devolve a pergunta.",
        ),
    ],
)

add(
    "idio-apresentar-en",
    ["Apresentar-se com nome, origem e idade.", "Usar I am corretamente."],
    [
        ordering(
            "idio-apresentar-en-frase",
            "Monte a frase de apresentação:",
            ["My", "name", "is", "Pedro"],
        ),
        multiple_choice(
            "idio-apresentar-en-idade",
            "Como se diz “tenho 30 anos” em inglês?",
            [
                "I am 30 years old.",
                "I have 30 years.",
                "I have 30 years old.",
                "My age is 30 years have.",
            ],
            "I am 30 years old.",
            "Em inglês a idade usa o verbo to be: I am 30 years old. “I have 30 years” é "
            "erro típico de quem traduz do português.",
        ),
        fill_blank(
            "idio-apresentar-en-origem",
            "I am ___ Brazil.",
            ["from"],
            "“I am from Brazil” — from indica origem. Sem from, a frase fica sem sentido.",
        ),
    ],
)

add(
    "idio-numeros-en",
    ["Contar de 1 a 20 em inglês.", "Diferenciar -teen de -ty."],
    [
        matching(
            "idio-numeros-en-pares",
            "Ligue o número ao nome em inglês:",
            [("13", "thirteen"), ("30", "thirty"), ("15", "fifteen"), ("50", "fifty")],
            "A terminação -teen marca 13 a 19; -ty marca as dezenas. É a confusão mais "
            "comum em preços e idades.",
        ),
        multiple_choice(
            "idio-numeros-en-dezena",
            "Qual é o número 40 em inglês?",
            ["forty", "fourty", "fourteen", "fourtteen"],
            "forty",
            "40 é forty, sem o “u” de four. A grafia irregular é um dos erros mais comuns.",
        ),
        fill_blank(
            "idio-numeros-en-teen",
            "Complete a sequência: thirteen, fourteen, ___, sixteen.",
            ["fifteen"],
            "Fifteen é 15. Depois de fourteen vem fifteen — o “five” vira “fif”.",
        ),
    ],
)

add(
    "idio-comida-en",
    ["Nomear alimentos básicos em inglês.", "Pedir comida com educação."],
    [
        matching(
            "idio-comida-en-pares",
            "Ligue o alimento ao nome em inglês:",
            [
                ("arroz", "rice"),
                ("feijão", "beans"),
                ("pão", "bread"),
                ("água", "water"),
            ],
            "São os itens que mais aparecem em cardápios e conversas do dia a dia.",
        ),
        multiple_choice(
            "idio-comida-en-pedido",
            "Qual frase é a forma mais educada de pedir água?",
            [
                "I would like a glass of water, please.",
                "Give me water.",
                "Water!",
                "I want water now.",
            ],
            "I would like a glass of water, please.",
            "“I would like...” é o pedido educado padrão. “Give me” soa como ordem.",
        ),
    ],
)

add(
    "idio-cores-en",
    ["Nomear cores básicas.", "Colocar a cor antes do objeto."],
    [
        multiple_choice(
            "idio-cores-en-ordem",
            "Qual é a ordem correta em inglês?",
            ["a red car", "a car red", "red a car", "car a red"],
            "a red car",
            "Em inglês o adjetivo vem antes do substantivo: red car. A ordem portuguesa "
            "invertida é o erro mais frequente.",
        ),
        matching(
            "idio-cores-en-pares",
            "Ligue a cor ao nome:",
            [("vermelho", "red"), ("azul", "blue"), ("verde", "green"), ("branco", "white")],
            "Cores aparecem em roupas, semáforos e rótulos — vocabulário de uso imediato.",
        ),
    ],
)

add(
    "idio-dias-en",
    ["Nomear os dias da semana.", "Usar maiúscula nos dias e meses."],
    [
        ordering(
            "idio-dias-en-ordem",
            "Ordene a semana em inglês, começando por Monday:",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        ),
        true_false(
            "idio-dias-en-maiuscula",
            "Em inglês, os dias da semana se escrevem com letra maiúscula.",
            True,
            "Diferente do português, Monday, Tuesday e January vão sempre com maiúscula.",
        ),
        fill_blank(
            "idio-dias-en-quarta",
            "Complete: Monday, Tuesday, ___, Thursday.",
            ["Wednesday"],
            "Wednesday é quarta-feira. A pronúncia é “uénz-dei”, com o primeiro “d” quase "
            "mudo.",
        ),
    ],
)

add(
    "idio-familia-en",
    ["Nomear parentes próximos.", "Usar my corretamente."],
    [
        matching(
            "idio-familia-en-pares",
            "Ligue o parente ao nome em inglês:",
            [
                ("mãe", "mother"),
                ("pai", "father"),
                ("irmã", "sister"),
                ("irmão", "brother"),
            ],
            "Depois desses, son (filho) e daughter (filha) completam a família próxima.",
        ),
        multiple_choice(
            "idio-familia-en-possessivo",
            "Qual frase está correta?",
            ["This is my mother.", "This is the my mother.", "This is mother my.", "This is my the mother."],
            "This is my mother.",
            "Com possessivo não se usa artigo: my mother. “The my mother” é o erro mais "
            "comum de quem fala português.",
        ),
    ],
)

add(
    "idio-mercado-en",
    ["Perguntar preços no singular e no plural.", "Pedir itens em uma loja."],
    [
        multiple_choice(
            "idio-mercado-en-plural",
            "Para perguntar o preço de VÁRIOS itens, você diz:",
            [
                "How much are these?",
                "How much is these?",
                "How much this is?",
                "How many is this?",
            ],
            "How much are these?",
            "Plural pede are: how much are these? How much is this? é para um item só.",
        ),
        fill_blank(
            "idio-mercado-en-pedido",
            "I ___ like three apples, please.",
            ["would"],
            "“I would like” é o pedido educado. A forma contraída é I'd like.",
        ),
    ],
)

add(
    "idio-onibus-en",
    ["Perguntar onde fica um lugar.", "Usar nomes de transporte."],
    [
        multiple_choice(
            "idio-onibus-en-pergunta",
            "Como perguntar onde fica a parada de ônibus?",
            [
                "Where is the bus stop?",
                "What is the bus stop?",
                "Who is the bus stop?",
                "When is the bus stop?",
            ],
            "Where is the bus stop?",
            "Where pergunta lugar. What, who e when perguntam outra coisa.",
        ),
        matching(
            "idio-onibus-en-transporte",
            "Ligue o transporte:",
            [("bus", "ônibus"), ("train", "trem"), ("subway", "metrô"), ("taxi", "táxi")],
            "Esses nomes aparecem em placas de estação e aeroporto.",
        ),
    ],
)

add(
    "idio-medico-en",
    ["Descrever sintomas em inglês.", "Pedir ajuda médica."],
    [
        multiple_choice(
            "idio-medico-en-sintoma",
            "“I have a headache” significa:",
            ["Estou com dor de cabeça", "Estou com febre", "Estou com dor de barriga", "Estou resfriado"],
            "Estou com dor de cabeça",
            "headache é dor de cabeça; fever é febre; stomachache é dor de barriga.",
        ),
        fill_blank(
            "idio-medico-en-ajuda",
            "I need a ___, please.",
            ["doctor"],
            "“I need a doctor, please” é a frase de emergência mais útil em viagem.",
        ),
    ],
)

add(
    "idio-trabalho-en",
    ["Fazer pedidos educados no trabalho.", "Pedir para repetir."],
    [
        multiple_choice(
            "idio-trabalho-en-educado",
            "Qual frase é um pedido educado?",
            [
                "Can you help me with this report?",
                "Give me the report.",
                "You help me now.",
                "Report!",
            ],
            "Can you help me with this report?",
            "Can you...? e Could you...? são as fórmulas educadas de pedido.",
        ),
        fill_blank(
            "idio-trabalho-en-repetir",
            "Sorry, can you ___ that, please?",
            ["repeat"],
            "“Can you repeat, please?” resolve a maior parte dos mal-entendidos por "
            "telefone ou em reunião.",
        ),
    ],
)

add(
    "idio-viagem-en",
    ["Perguntar direções e horários.", "Fazer check-in em hotel."],
    [
        multiple_choice(
            "idio-viagem-en-hotel",
            "Para perguntar onde fica o hotel, diga:",
            ["Where is the hotel?", "How is the hotel?", "Who is the hotel?", "When is the hotel?"],
            "Where is the hotel?",
            "Where pergunta lugar. Combine com “excuse me” para começar com educação.",
        ),
        true_false(
            "idio-viagem-en-reserva",
            "“I have a reservation” é a frase usada para dizer que você tem reserva.",
            True,
            "É a frase-chave no balcão do hotel: reservation = reserva.",
        ),
    ],
)

add(
    "idio-leitura-en",
    ["Achar a ideia principal de um texto curto.", "Evitar tradução palavra por palavra."],
    [
        multiple_choice(
            "idio-leitura-en-ideia",
            "Em “The bus leaves at eight. It stops downtown.”, qual é a informação "
            "principal?",
            [
                "O ônibus sai às oito.",
                "O ônibus para no centro.",
                "O ônibus está atrasado.",
                "O ônibus é novo.",
            ],
            "O ônibus sai às oito.",
            "A primeira frase de um parágrafo curto costuma trazer a ideia principal; o "
            "resto detalha.",
        ),
        true_false(
            "idio-leitura-en-traduzir",
            "Para entender um texto em inglês é preciso traduzir cada palavra.",
            False,
            "Entender o sentido geral chega primeiro. Traduzir palavra por palavra trava a "
            "leitura e cansa.",
        ),
    ],
)

add(
    "idio-escuta-en",
    ["Identificar palavras-chave ao ouvir.", "Deduzir pelo contexto."],
    [
        multiple_choice(
            "idio-escuta-en-palavras",
            "Em “The train to London leaves at nine”, quais são as palavras-chave?",
            [
                "train, London, nine",
                "the, to, at",
                "leaves, the, to",
                "nine, the, and",
            ],
            "train, London, nine",
            "Quem, o que, quando e onde carregam a informação. Preposições e artigos ficam "
            "em segundo plano.",
        ),
        true_false(
            "idio-escuta-en-tudo",
            "Ao ouvir inglês, é necessário entender 100% das palavras.",
            False,
            "Pegar as palavras-chave já permite entender a situação. O resto se deduz pelo "
            "contexto.",
        ),
    ],
)

add(
    "idio-pronuncia-en",
    ["Produzir o som “th”.", "Reconhecer sons que não existem em português."],
    [
        multiple_choice(
            "idio-pronuncia-en-th",
            "No som “th” de think, a língua:",
            [
                "Toca de leve os dentes de cima.",
                "Fica no céu da boca.",
                "Fica atrás dos dentes de baixo.",
                "Não se move.",
            ],
            "Toca de leve os dentes de cima.",
            "A língua entre os dentes, com sopro de ar. Trocar por “t” ou “s” é o erro "
            "típico de quem fala português.",
        ),
        true_false(
            "idio-pronuncia-en-red",
            "O “r” de red é igual ao “r” de rato em português.",
            False,
            "O “r” inglês é mais suave, com a língua sem tocar o céu da boca. O “r” "
            "brasileiro é mais vibrante.",
        ),
    ],
)

# ── Espanhol ─────────────────────────────────────────────────────────────
add(
    "idio-cumprimentos-es",
    ["Cumprimentar conforme a hora.", "Despedir-se em espanhol."],
    [
        multiple_choice(
            "idio-cumprimentos-es-tarde",
            "Às 15h, o cumprimento correto é:",
            ["Buenas tardes", "Buenos días", "Buenas noches", "Buenos tardes"],
            "Buenas tardes",
            "Tardes é feminino, então buenas tardes. O erro comum é usar buenos com tarde.",
        ),
        matching(
            "idio-cumprimentos-es-pares",
            "Ligue cada expressão à tradução:",
            [
                ("Buenos días", "bom dia"),
                ("Buenas noches", "boa noite"),
                ("Hasta luego", "até logo"),
                ("¿Cómo estás?", "como você está?"),
            ],
            "Buenas noches serve para chegar e para se despedir à noite.",
        ),
    ],
)

add(
    "idio-apresentar-es",
    ["Apresentar-se com nome, origem e idade.", "Usar Tengo para idade."],
    [
        ordering(
            "idio-apresentar-es-frase",
            "Monte a apresentação:",
            ["Me", "llamo", "Pedro"],
        ),
        fill_blank(
            "idio-apresentar-es-idade",
            "___ treinta años.",
            ["Tengo"],
            "Em espanhol a idade usa tener: tengo 30 años. Em português também usamos ter — "
            "é o inglês que usa o verbo to be.",
        ),
    ],
)

add(
    "idio-numeros-es",
    ["Contar de 1 a 20 em espanhol.", "Formar as dezenas em -enta."],
    [
        matching(
            "idio-numeros-es-pares",
            "Ligue o número ao nome:",
            [("16", "dieciséis"), ("20", "veinte"), ("30", "treinta"), ("50", "cincuenta")],
            "Do 16 ao 19 os números são compostos; as dezenas terminam em -enta.",
        ),
        fill_blank(
            "idio-numeros-es-dezena",
            "Complete a sequência: veinte, treinta, ___, cincuenta.",
            ["cuarenta"],
            "Cuarenta é 40 (sem o “u” depois do “c” inicial).",
        ),
    ],
)

add(
    "idio-comida-es",
    ["Nomear alimentos em espanhol.", "Pedir comida educadamente."],
    [
        matching(
            "idio-comida-es-pares",
            "Ligue o alimento:",
            [
                ("arroz", "arroz"),
                ("feijão", "frijoles"),
                ("pão", "pan"),
                ("água", "agua"),
            ],
            "Atenção aos falsos amigos: “arroz” é igual, “frijoles” é feijão.",
        ),
        fill_blank(
            "idio-comida-es-pedido",
            "___ un vaso de agua, por favor.",
            ["Quisiera"],
            "Quisiera = “eu gostaria”. É a fórmula educada de pedido, equivalente ao “I "
            "would like” do inglês.",
        ),
    ],
)

add(
    "idio-falsos-amigos",
    ["Reconhecer falsos amigos PT-ES.", "Evitar mal-entendidos por semelhança."],
    [
        matching(
            "idio-falsos-amigos-pares",
            "Ligue a palavra espanhola ao seu significado real:",
            [
                ("exquisito", "delicioso"),
                ("largo", "comprido"),
                ("oficina", "escritório"),
                ("rato", "momento"),
            ],
            "Parecidas com palavras do português, mas com outro sentido. “Largo” em "
            "espanhol é comprimento, não largura.",
        ),
        multiple_choice(
            "idio-falsos-amigos-escolha",
            "Você pede uma “sopa exquisita” em um restaurante. O garçom entende que a sopa "
            "é:",
            ["Deliciosa", "Estranha", "Cara", "Fria"],
            "Deliciosa",
            "Exquisito em espanhol é elogio: delicioso. Em português, “esquisito” é "
            "estranho — o oposto.",
        ),
    ],
)

add(
    "idio-mercado-es",
    ["Perguntar preços em espanhol.", "Pedir em uma loja."],
    [
        multiple_choice(
            "idio-mercado-es-plural",
            "Para perguntar o preço de vários itens:",
            ["¿Cuánto cuestan?", "¿Cuánto cuesta?", "¿Cuánto es?", "¿Qué cuesta?"],
            "¿Cuánto cuestan?",
            "Plural pede cuestan; singular, cuesta. É o mesmo padrão de is/are do inglês.",
        ),
        fill_blank(
            "idio-mercado-es-cuesta",
            "¿Cuánto ___ este pan?",
            ["cuesta"],
            "Um único item pede cuesta. Com “estos panes”, seria cuestan.",
        ),
    ],
)

add(
    "idio-viagem-es",
    ["Perguntar direções em espanhol.", "Perguntar horários."],
    [
        multiple_choice(
            "idio-viagem-es-hotel",
            "Para perguntar onde fica o hotel:",
            [
                "¿Dónde está el hotel?",
                "¿Cómo está el hotel?",
                "¿Quién está el hotel?",
                "¿Cuándo está el hotel?",
            ],
            "¿Dónde está el hotel?",
            "Dónde pergunta lugar; cuándo pergunta tempo.",
        ),
        fill_blank(
            "idio-viagem-es-hora",
            "¿A qué ___ sale el tren?",
            ["hora"],
            "“¿A qué hora...?” é a fórmula para perguntar horário.",
        ),
    ],
)

add(
    "idio-medico-es",
    ["Descrever dor em espanhol.", "Pedir ajuda médica."],
    [
        multiple_choice(
            "idio-medico-es-dor",
            "“Me duele la cabeza” significa:",
            ["Estou com dor de cabeça", "Estou com febre", "Estou com dor de barriga", "Estou tonto"],
            "Estou com dor de cabeça",
            "“Me duele + parte do corpo” é a estrutura da dor localizada.",
        ),
        matching(
            "idio-medico-es-partes",
            "Ligue a parte do corpo:",
            [("cabeza", "cabeça"), ("estómago", "estômago"), ("garganta", "garganta")],
            "Essas três aparecem nas queixas mais comuns em consulta.",
        ),
    ],
)

add(
    "idio-pronuncia-es",
    ["Reconhecer sons regulares do espanhol.", "Diferenciar o “j” do português."],
    [
        multiple_choice(
            "idio-pronuncia-es-j",
            "O “j” de jardín soa como:",
            [
                "Um sopro forte, parecido com o “r” forte do português.",
                "O “j” de janela.",
                "O “g” de gato.",
                "Um “s”.",
            ],
            "Um sopro forte, parecido com o “r” forte do português.",
            "O “j” espanhol é aspirado. Já o “ll” de llave varia entre “i” e “lh” conforme "
            "o país.",
        ),
        true_false(
            "idio-pronuncia-es-regular",
            "O espanhol tem pronúncia mais regular que o português: cada letra tem som "
            "bastante fixo.",
            True,
            "Com poucas exceções, o espanhol pronuncia o que escreve — o que ajuda muito "
            "quem está começando.",
        ),
    ],
)

# ── Português ────────────────────────────────────────────────────────────
add(
    "idio-pt-estrangeiros",
    ["Reconhecer traços do português brasileiro.", "Apresentar-se em português."],
    [
        ordering(
            "idio-pt-estrangeiros-frase",
            "Monte a apresentação em português:",
            ["Meu", "nome", "é", "Ana"],
        ),
        multiple_choice(
            "idio-pt-estrangeiros-saudacao",
            "Qual saudação é típica do português brasileiro?",
            ["Bom dia! Tudo bem?", "Good morning", "Buenos días", "Bonjour"],
            "Bom dia! Tudo bem?",
            "O “tudo bem?” no início da conversa é marca do português do Brasil.",
        ),
    ],
)

add(
    "idio-entrevista-pt",
    ["Responder perguntas comuns de entrevista.", "Estruturar respostas curtas e concretas."],
    [
        multiple_choice(
            "idio-entrevista-pt-pontos",
            "Ao responder “fale sobre você” em uma entrevista, o melhor é:",
            [
                "Contar experiência concreta e o que você sabe fazer.",
                "Contar a história da família desde o início.",
                "Dizer que não sabe falar de si.",
                "Falar só dos defeitos.",
            ],
            "Contar experiência concreta e o que você sabe fazer.",
            "Respostas curtas com exemplos concretos funcionam melhor do que discurso "
            "genérico.",
        ),
        true_false(
            "idio-entrevista-pt-silencio",
            "Se não entender uma pergunta, o melhor é pedir que a repitam.",
            True,
            "“Pode repetir, por favor?” é aceito e evita responder algo fora do assunto.",
        ),
    ],
)

add(
    "idio-telefone-pt",
    ["Atender e identificar-se ao telefone.", "Pedir para repetir."],
    [
        ordering(
            "idio-telefone-pt-ordem",
            "Ordene o início de uma ligação:",
            ["Alô!", "Aqui é o Pedro.", "Com quem falo?", "Pode repetir, por favor?"],
        ),
        multiple_choice(
            "idio-telefone-pt-atender",
            "Ao atender uma ligação de trabalho, comece com:",
            ["Alô! Bom dia.", "Quem é?", "Fala logo.", "(silêncio)"],
            "Alô! Bom dia.",
            "Cumprimentar e se identificar evita constrangimento e deixa a conversa mais "
            "clara.",
        ),
    ],
)

add(
    "idio-email-pt",
    ["Escrever e-mail profissional.", "Escolher assunto claro."],
    [
        multiple_choice(
            "idio-email-pt-assunto",
            "Qual assunto é mais adequado para um e-mail profissional?",
            [
                "Solicitação de orçamento — reforma da cozinha",
                "oi",
                "urgente!!!",
                "sem assunto",
            ],
            "Solicitação de orçamento — reforma da cozinha",
            "Assunto específico e curto: quem recebe entende e responde mais rápido.",
        ),
        fill_blank(
            "idio-email-pt-saudacao",
            "Em um e-mail para alguém desconhecido, use “Prezado(a) ___”.",
            ["Senhor", "Senhora"],
            "“Prezado(a) Senhor(a)” é a saudação formal padrão quando não há nome.",
        ),
    ],
)

add(
    "idio-apresentacao-pt",
    ["Estruturar uma apresentação.", "Usar abertura, três pontos e conclusão."],
    [
        ordering(
            "idio-apresentacao-pt-ordem",
            "Ordene a estrutura de uma apresentação:",
            [
                "Dizer o que vai falar",
                "Apresentar os três pontos principais",
                "Resumir o que foi dito",
                "Abrir para perguntas",
            ],
        ),
        true_false(
            "idio-apresentacao-pt-ler",
            "Ler slides inteiros em voz alta é uma boa forma de apresentar.",
            False,
            "Quem lê slides perde contato com a plateia. O slide traz poucas palavras; a "
            "fala completa a ideia.",
        ),
    ],
)

add(
    "idio-reuniao-pt",
    ["Pedir a palavra em reunião.", "Concordar e discordar com respeito."],
    [
        multiple_choice(
            "idio-reuniao-pt-palavra",
            "Qual frase serve para pedir a palavra em uma reunião?",
            [
                "Posso complementar?",
                "Cala a boca.",
                "Você está errado.",
                "Depois eu falo.",
            ],
            "Posso complementar?",
            "“Posso complementar?” entra na conversa sem interromper de forma agressiva.",
        ),
        matching(
            "idio-reuniao-pt-pares",
            "Ligue a intenção à frase:",
            [
                ("concordar", "Concordo com a Ana."),
                ("discordar com respeito", "Entendo, mas vejo de outra forma."),
                ("pedir tempo", "Posso pensar e responder amanhã?"),
            ],
            "Frases prontas evitam que a discordância pareça ataque pessoal.",
        ),
    ],
)

add(
    "idio-escrita-pt",
    ["Escrever frases curtas e diretas.", "Preferir voz ativa."],
    [
        multiple_choice(
            "idio-escrita-pt-voz-ativa",
            "Qual versão é mais clara?",
            [
                "A equipe prorrogou o prazo.",
                "Foi decidido pela equipe que o prazo seria prorrogado.",
                "O prazo, por decisão, foi prorrogado pela equipe.",
                "Prorrogou-se, pela equipe, o prazo.",
            ],
            "A equipe prorrogou o prazo.",
            "Voz ativa, ordem direta e uma ideia por frase: quem lê entende na primeira "
            "leitura.",
        ),
        true_false(
            "idio-escrita-pt-frase-longa",
            "Frases longas com várias ideias são mais claras que frases curtas.",
            False,
            "Cada ideia em uma frase reduz a chance de o leitor se perder no meio do "
            "período.",
        ),
    ],
)

add(
    "idio-cultura-br",
    ["Reconhecer festas e comidas por região.", "Entender expressões culturais."],
    [
        matching(
            "idio-cultura-br-pares",
            "Ligue a região à festa ou comida:",
            [
                ("Nordeste", "forró e acarajé"),
                ("Sul", "festa da uva e chimarrão"),
                ("Norte", "açaí e Círio de Nazaré"),
            ],
            "Cada região tem repertório próprio, e isso aparece nas músicas, nas piadas e "
            "na comida.",
        ),
        true_false(
            "idio-cultura-br-sotaques",
            "O Brasil tem sotaques diferentes dentro do mesmo país.",
            True,
            "As cinco regiões têm sotaques, vocabulário e entonação próprios. Não existe um "
            "único “português brasileiro” falado igual em todo lugar.",
        ),
    ],
)


def build() -> dict:
    return SPECS
