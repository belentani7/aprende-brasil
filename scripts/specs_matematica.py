"""Atividades de Matemática (40 módulos) — laboratório interativo em texto.

Regra de ouro: **todo gabarito numérico é verificado no build** por
``numeric_checked``, que avalia a expressão em Python. Se a conta estiver
errada, o build falha. Nenhum resultado é digitado "a olho".

Cada módulo aponta o erro frequente em vez de só corrigir: quem erra precisa
saber por que errou.
"""

from __future__ import annotations

from scripts.activity_spec import (
    fill_blank,
    matching,
    multiple_choice,
    numeric_checked,
    ordering,
    spec,
    true_false,
)

SPECS: dict = {}


def add(module_id: str, objectives: list[str], activities: list[dict]) -> None:
    SPECS[module_id] = spec(objectives, activities)


add(
    "mat-contar",
    [
        "Contar objetos sem pular nem repetir.",
        "Reconhecer que dez unidades formam uma dezena.",
    ],
    [
        numeric_checked(
            "mat-contar-dezenas",
            "Você contou 3 dezenas de laranjas. Quantas laranjas são?",
            "3 * 10",
            "3 × 10 = 30. Cada dezena vale 10, então três dezenas são 30 unidades.",
            unit="laranjas",
            tolerance=0,
        ),
        numeric_checked(
            "mat-contar-proximo",
            "Depois do 39 vem qual número?",
            "39 + 1",
            "39 + 1 = 40. Ao chegar no 9, a contagem recomeça no 0 e a dezena aumenta.",
            tolerance=0,
        ),
    ],
)

add(
    "mat-soma",
    ["Somar juntando quantidades.", "Somar contando a partir do maior número."],
    [
        numeric_checked(
            "mat-soma-simples",
            "Você tem 2 reais e ganha mais 3. Com quanto fica?",
            "2 + 3",
            "2 + 3 = 5. Começar do 3 e contar mais dois (4, 5) é mais rápido que contar "
            "tudo de novo.",
            unit="reais",
        ),
        numeric_checked(
            "mat-soma-dezena",
            "34 + 25 = ?",
            "34 + 25",
            "34 + 25 = 59. Some dezenas com dezenas (30 + 20 = 50) e unidades com "
            "unidades (4 + 5 = 9).",
            tolerance=0,
        ),
    ],
)

add(
    "mat-subtracao",
    ["Subtrair tirando uma quantidade.", "Conferir a subtração somando de volta."],
    [
        numeric_checked(
            "mat-subtracao-simples",
            "Você tinha 5 e tirou 2. Quantos sobram?",
            "5 - 2",
            "5 − 2 = 3. Para conferir: 3 + 2 = 5, voltou ao início.",
            tolerance=0,
        ),
        multiple_choice(
            "mat-subtracao-erro",
            "Ao conferir “9 − 4 = 5”, qual soma prova que está certo?",
            ["5 + 4 = 9", "9 + 4 = 13", "5 − 4 = 1", "9 − 5 = 4"],
            "5 + 4 = 9",
            "Subtração se confere com a soma inversa: resultado + o que foi tirado deve "
            "dar o número inicial.",
        ),
    ],
)

add(
    "mat-multiplicar",
    ["Entender multiplicação como soma repetida.", "Usar a propriedade comutativa para conferir."],
    [
        numeric_checked(
            "mat-multiplicar-soma",
            "3 × 4 é o mesmo que 4 + 4 + 4. Quanto dá?",
            "3 * 4",
            "3 × 4 = 12. Três grupos de quatro somam 12.",
            tolerance=0,
        ),
        numeric_checked(
            "mat-multiplicar-caixas",
            "Uma caixa tem 6 ovos. Quantos ovos há em 5 caixas iguais?",
            "6 * 5",
            "6 × 5 = 30. Multiplicar evita somar 6 cinco vezes seguidas.",
            unit="ovos",
            tolerance=0,
        ),
    ],
)

add(
    "mat-dividir",
    ["Repartir em partes iguais.", "Interpretar o resto de uma divisão."],
    [
        numeric_checked(
            "mat-dividir-balas",
            "12 balas para 3 pessoas, em partes iguais. Quantas para cada uma?",
            "12 / 3",
            "12 ÷ 3 = 4. Conferindo: 4 × 3 = 12.",
            unit="balas",
            tolerance=0,
        ),
        multiple_choice(
            "mat-dividir-resto",
            "7 balas para 2 pessoas. Você come 3 e sobra 1. O que é esse 1?",
            ["O resto da divisão", "O divisor", "O quociente", "Um erro de conta"],
            "O resto da divisão",
            "7 ÷ 2 = 3 e sobra 1. O resto é o que não dá para repartir igualmente.",
        ),
    ],
)

add(
    "mat-dinheiro",
    ["Somar moedas e notas do real.", "Converter centavos em reais."],
    [
        numeric_checked(
            "mat-dinheiro-moedas",
            "Quatro moedas de 25 centavos somam quantos centavos?",
            "4 * 25",
            "4 × 25 = 100 centavos, que é R$ 1,00. Quatro moedas de 25 formam um real.",
            unit="centavos",
            tolerance=0,
        ),
        numeric_checked(
            "mat-dinheiro-notas",
            "Duas notas de R$ 50 mais uma de R$ 10. Qual é o total?",
            "2 * 50 + 10",
            "50 + 50 + 10 = R$ 110,00. Agrupar notas iguais antes de somar reduz erro.",
            unit="reais",
        ),
    ],
)

add(
    "mat-troco",
    ["Calcular troco por subtração.", "Conferir o troco somando ao preço."],
    [
        numeric_checked(
            "mat-troco-pao",
            "O pão custa R$ 6,00 e você paga com R$ 10,00. Qual é o troco?",
            "10 - 6",
            "10 − 6 = R$ 4,00. Troco + preço deve dar exatamente o valor pago.",
            unit="reais",
        ),
        numeric_checked(
            "mat-troco-centavos",
            "Compra de R$ 7,50 paga com R$ 10,00. Troco?",
            "10 - 7.50",
            "10,00 − 7,50 = R$ 2,50. Com centavos, alinhe a vírgula antes de subtrair.",
            unit="reais",
        ),
    ],
)

add(
    "mat-formas",
    ["Reconhecer lados e cantos das formas planas.", "Relacionar forma a objeto do cotidiano."],
    [
        matching(
            "mat-formas-relacionar",
            "Ligue cada forma ao objeto que tem essa forma:",
            [
                ("quadrado", "azulejo da parede"),
                ("círculo", "tampa do pote"),
                ("triângulo", "telhado de duas águas"),
                ("retângulo", "porta"),
            ],
            "Cada objeto do dia a dia repete uma forma geométrica simples.",
        ),
        numeric_checked(
            "mat-formas-lados",
            "Um quadrado e um triângulo juntos têm quantos lados no total?",
            "4 + 3",
            "4 + 3 = 7 lados. O círculo não entra na conta porque não tem lados retos.",
            unit="lados",
            tolerance=0,
        ),
    ],
)

add(
    "mat-fracoes",
    [
        "Ler o numerador e o denominador de uma fração.",
        "Comparar frações com o mesmo denominador.",
    ],
    [
        multiple_choice(
            "mat-fracoes-numero",
            "Na fração 3/4, o número de baixo (4) indica o quê?",
            [
                "Em quantas partes iguais o todo foi dividido",
                "Quantas partes foram tomadas",
                "O valor total da pizza",
                "A quantidade de pessoas",
            ],
            "Em quantas partes iguais o todo foi dividido",
            "O denominador (embaixo) diz em quantas partes o todo foi cortado; o "
            "numerador (em cima) diz quantas você pegou.",
        ),
        true_false(
            "mat-fracoes-comparar",
            "3/8 é maior que 5/8.",
            False,
            "Com o mesmo denominador, é maior quem tem o numerador maior: 5/8 > 3/8. "
            "O erro comum é olhar o número de baixo primeiro.",
        ),
    ],
)

add(
    "mat-medidas",
    ["Converter metro em centímetro.", "Medir e comparar comprimentos."],
    [
        numeric_checked(
            "mat-medidas-metro",
            "Uma mesa tem 1,20 m. Quantos centímetros são?",
            "1.20 * 100",
            "1,20 × 100 = 120 cm. Metro para centímetro: multiplica por 100.",
            unit="cm",
            tolerance=0,
        ),
        numeric_checked(
            "mat-medidas-soma",
            "Uma parede de 2 m mais uma de 150 cm. Total em centímetros?",
            "2 * 100 + 150",
            "200 + 150 = 350 cm. Antes de somar, coloque tudo na mesma unidade.",
            unit="cm",
            tolerance=0,
        ),
    ],
)

add(
    "mat-peso",
    ["Converter quilo em gramas.", "Somar pesos de produtos."],
    [
        numeric_checked(
            "mat-peso-pacote",
            "Um pacote de 1 kg tem quantas gramas?",
            "1 * 1000",
            "1 kg = 1000 g. Quilo para grama: multiplica por 1000.",
            unit="g",
            tolerance=0,
        ),
        numeric_checked(
            "mat-peso-soma",
            "500 g de queijo mais 750 g de presunto. Total em gramas?",
            "500 + 750",
            "500 + 750 = 1250 g, ou 1,25 kg. Passar de 1000 g já é mais de um quilo.",
            unit="g",
            tolerance=0,
        ),
    ],
)

add(
    "mat-horas",
    ["Ler horas em relógio analógico e digital.", "Somar horas e minutos."],
    [
        multiple_choice(
            "mat-horas-poeiro",
            "No relógio de ponteiros, às 3h30, onde está o ponteiro longo?",
            ["No 6", "No 12", "No 3", "No 9"],
            "No 6",
            "O ponteiro longo marca os minutos: cada número vale 5 minutos, então o 6 são "
            "30 minutos.",
        ),
        numeric_checked(
            "mat-horas-minutos",
            "Duas horas e meia têm quantos minutos?",
            "2 * 60 + 30",
            "2 × 60 = 120, mais 30 = 150 minutos.",
            unit="minutos",
            tolerance=0,
        ),
    ],
)

add(
    "mat-calendario",
    ["Usar semanas e meses.", "Calcular dias entre datas próximas."],
    [
        numeric_checked(
            "mat-calendario-semana",
            "Quantos dias têm 3 semanas?",
            "3 * 7",
            "3 × 7 = 21 dias.",
            unit="dias",
            tolerance=0,
        ),
        multiple_choice(
            "mat-calendario-fevereiro",
            "Quantos dias tem fevereiro em um ano comum (não bissexto)?",
            ["28", "29", "30", "31"],
            "28",
            "Fevereiro tem 28 dias nos anos comuns e 29 nos bissextos, a cada quatro anos.",
        ),
    ],
)

add(
    "mat-receita",
    ["Dobrar e reduzir receitas por proporção.", "Dividir quantidades fracionadas."],
    [
        numeric_checked(
            "mat-receita-dobrar",
            "A receita pede 3 ovos para 4 pessoas. Para 8 pessoas, quantos ovos?",
            "3 * 2",
            "Dobrar as pessoas dobra os ingredientes: 3 × 2 = 6 ovos.",
            unit="ovos",
            tolerance=0,
        ),
        numeric_checked(
            "mat-receita-metade",
            "A receita pede 2 xícaras de farinha. Fazendo metade, quantas xícaras?",
            "2 / 2",
            "Metade de 2 xícaras é 1 xícara. Reduzir à metade é dividir tudo por 2.",
            unit="xícaras",
            tolerance=0,
        ),
    ],
)

add(
    "mat-grafico",
    ["Ler valores em um gráfico de barras.", "Comparar quantidades entre categorias."],
    [
        multiple_choice(
            "mat-grafico-comparar",
            "Num gráfico de barras, a barra de segunda-feira tem 12 e a de terça tem 8. "
            "Qual dia teve mais?",
            ["Segunda-feira", "Terça-feira", "Empate", "Não dá para saber"],
            "Segunda-feira",
            "Barra mais alta = valor maior. 12 > 8, então segunda teve mais.",
        ),
        numeric_checked(
            "mat-grafico-diferenca",
            "As vendas foram 12 na segunda e 8 na terça. Qual é a diferença?",
            "12 - 8",
            "12 − 8 = 4. A diferença entre as barras é a distância entre os valores.",
            tolerance=0,
        ),
    ],
)

add(
    "mat-porcentagem",
    ["Calcular porcentagem de um valor.", "Aplicar porcentagem em descontos e juros."],
    [
        numeric_checked(
            "mat-porcentagem-vinte",
            "20% de R$ 150,00 é quanto?",
            "150 * 20 / 100",
            "150 × 20 ÷ 100 = R$ 30,00. Vinte por cento é 20 de cada 100.",
            unit="reais",
        ),
        numeric_checked(
            "mat-porcentagem-dez",
            "10% de 80 é quanto?",
            "80 * 10 / 100",
            "80 × 10 ÷ 100 = 8. Para 10%, basta andar uma casa decimal: 80 → 8.",
            tolerance=0,
        ),
    ],
)

add(
    "mat-equacao",
    ["Resolver equação de um passo.", "Aplicar a operação inversa nos dois lados."],
    [
        numeric_checked(
            "mat-equacao-soma",
            "Resolva: x + 5 = 12. Qual é o valor de x?",
            "12 - 5",
            "x = 12 − 5 = 7. A operação inversa da soma é a subtração, aplicada nos dois "
            "lados.",
            tolerance=0,
        ),
        numeric_checked(
            "mat-equacao-multiplicar",
            "Resolva: 3x = 21. Qual é o valor de x?",
            "21 / 3",
            "x = 21 ÷ 3 = 7. Dividir os dois lados por 3 isola o x.",
            tolerance=0,
        ),
    ],
)

add(
    "mat-estatistica",
    ["Calcular média aritmética.", "Encontrar a mediana de um conjunto de dados."],
    [
        numeric_checked(
            "mat-estatistica-media",
            "Média de 4, 6 e 8.",
            "(4 + 6 + 8) / 3",
            "(4 + 6 + 8) ÷ 3 = 18 ÷ 3 = 6. A média soma tudo e divide pela quantidade.",
            tolerance=0,
        ),
        multiple_choice(
            "mat-estatistica-mediana",
            "Qual é a mediana de 3, 7, 9, 12, 15?",
            ["9", "7", "12", "9,2"],
            "9",
            "Com os dados em ordem e em quantidade ímpar, a mediana é o valor do meio: 9.",
        ),
    ],
)

add(
    "mat-negativos",
    ["Ler números negativos em temperatura e saldo.", "Somar e subtrair com negativos."],
    [
        numeric_checked(
            "mat-negativos-temperatura",
            "Estava −2 °C e subiu 5 graus. Qual é a temperatura agora?",
            "-2 + 5",
            "−2 + 5 = 3 °C. Subir na reta numérica é somar.",
            unit="°C",
            tolerance=0,
        ),
        multiple_choice(
            "mat-negativos-divida",
            "O saldo está em −R$ 50,00. O que isso significa?",
            [
                "Você deve R$ 50,00 ao banco.",
                "Você tem R$ 50,00 guardados.",
                "O saldo é zero.",
                "A conta foi encerrada.",
            ],
            "Você deve R$ 50,00 ao banco.",
            "Saldo negativo é dívida: o valor que falta para chegar a zero.",
        ),
    ],
)

add(
    "mat-probabilidade",
    ["Calcular probabilidade simples.", "Entender que a chance fica entre 0 e 1."],
    [
        numeric_checked(
            "mat-probabilidade-moeda",
            "Ao jogar uma moeda honesta, a probabilidade de sair cara é 1 em 2. Em "
            "porcentagem, quanto é?",
            "100 * 1 / 2",
            "1 ÷ 2 = 0,5 = 50%. Probabilidade também se escreve em porcentagem.",
            unit="%",
            tolerance=0,
        ),
        numeric_checked(
            "mat-probabilidade-dado",
            "Um dado tem 6 faces. Qual é a chance de sair o número 3, em porcentagem "
            "(uma casa decimal)?",
            "100 / 6",
            "100 ÷ 6 ≈ 16,7%. Um caso favorável em seis possíveis.",
            unit="%",
            tolerance=0.05,
        ),
    ],
)

add(
    "mat-regra3",
    ["Montar regra de três simples.", "Multiplicar em cruz para achar o valor desconhecido."],
    [
        numeric_checked(
            "mat-regra3-pao",
            "Se 2 pães custam R$ 6,00, quanto custam 5 pães?",
            "6 * 5 / 2",
            "6 × 5 ÷ 2 = R$ 15,00. Multiplica em cruz e divide pelo que sobra.",
            unit="reais",
        ),
        numeric_checked(
            "mat-regra3-km",
            "Se 3 litros rendem 30 km, quantos km rendem 7 litros?",
            "30 * 7 / 3",
            "30 × 7 ÷ 3 = 70 km. Mesma proporção, quantidades diferentes.",
            unit="km",
            tolerance=0,
        ),
    ],
)

add(
    "mat-sequencias",
    ["Descobrir a regra de uma sequência.", "Continuar uma sequência numérica."],
    [
        numeric_checked(
            "mat-sequencias-soma",
            "Na sequência 4, 7, 10, 13..., qual é o próximo número?",
            "13 + 3",
            "O padrão soma 3 a cada passo: 13 + 3 = 16.",
            tolerance=0,
        ),
        multiple_choice(
            "mat-sequencias-dobro",
            "Qual é a regra da sequência 2, 4, 8, 16?",
            [
                "Multiplicar por 2 a cada passo",
                "Somar 2 a cada passo",
                "Somar 4 e depois 8",
                "Não tem regra",
            ],
            "Multiplicar por 2 a cada passo",
            "2 → 4 → 8 → 16: cada número é o dobro do anterior. O próximo seria 32.",
        ),
    ],
)

add(
    "mat-area",
    ["Calcular perímetro somando lados.", "Calcular área de retângulo."],
    [
        numeric_checked(
            "mat-area-perimetro",
            "Um retângulo tem 5 m de comprimento e 3 m de largura. Qual é o perímetro?",
            "2 * (5 + 3)",
            "2 × (5 + 3) = 16 m. Perímetro é o contorno: dois comprimentos e duas "
            "larguras.",
            unit="m",
            tolerance=0,
        ),
        numeric_checked(
            "mat-area-area",
            "Esse mesmo retângulo (5 m × 3 m) tem qual área?",
            "5 * 3",
            "5 × 3 = 15 m². Área é o espaço de dentro: comprimento vezes largura.",
            unit="m²",
            tolerance=0,
        ),
    ],
)

add(
    "mat-angulos",
    ["Identificar ângulo reto, agudo e obtuso.", "Reconhecer 90 graus no cotidiano."],
    [
        multiple_choice(
            "mat-angulos-reto",
            "O canto de uma folha de papel sulfite tem qual ângulo?",
            ["90 graus (reto)", "45 graus (agudo)", "180 graus (raso)", "0 grau"],
            "90 graus (reto)",
            "O canto de folha, de porta e de livro é um ângulo reto, de 90 graus.",
        ),
        true_false(
            "mat-angulos-agudo",
            "Um ângulo de 30 graus é maior que um ângulo reto.",
            False,
            "30 graus é menor que 90: é um ângulo agudo. Reto é exatamente 90; obtuso, "
            "maior que 90.",
        ),
    ],
)

add(
    "mat-tempo",
    ["Calcular duração entre horários.", "Converter minutos em horas e minutos."],
    [
        numeric_checked(
            "mat-tempo-duracao",
            "De 8h20 a 9h05, quantos minutos se passaram?",
            "(9 * 60 + 5) - (8 * 60 + 20)",
            "De 8h20 até 9h00 são 40 minutos; mais 5 = 45 minutos. Converter tudo para "
            "minutos evita erro na conta.",
            unit="minutos",
            tolerance=0,
        ),
        numeric_checked(
            "mat-tempo-horas",
            "100 minutos equivalem a quantas horas e quantos minutos? Responda só o "
            "resto em minutos.",
            "100 % 60",
            "100 ÷ 60 = 1 hora e sobram 40 minutos. O resto da divisão por 60 são os "
            "minutos.",
            unit="minutos",
            tolerance=0,
        ),
    ],
)

add(
    "mat-capacidade",
    ["Converter litros em mililitros.", "Calcular quantos copos cabem em um litro."],
    [
        numeric_checked(
            "mat-capacidade-litros",
            "2 litros têm quantos mililitros?",
            "2 * 1000",
            "2 × 1000 = 2000 mL. Litro para mililitro: multiplica por 1000.",
            unit="mL",
            tolerance=0,
        ),
        numeric_checked(
            "mat-capacidade-copos",
            "Quantos copos de 200 mL cabem em 1 litro?",
            "1000 / 200",
            "1000 ÷ 200 = 5 copos. Um litro tem 1000 mL.",
            unit="copos",
            tolerance=0,
        ),
    ],
)

add(
    "mat-numeros-romanos",
    ["Ler símbolos romanos até 1000.", "Aplicar a regra da subtração."],
    [
        multiple_choice(
            "mat-romanos-ler",
            "Quanto vale XIV?",
            ["14", "16", "15", "4"],
            "14",
            "X = 10, IV = 4, então XIV = 14. O menor antes do maior subtrai.",
        ),
        fill_blank(
            "mat-romanos-escrever",
            "Escreva 40 em números romanos.",
            ["XL"],
            "XL = 50 − 10 = 40. Nunca se escreve XXXX.",
        ),
    ],
)

add(
    "mat-pares",
    ["Distinguir pares de ímpares pelo último algarismo.", "Aplicar a regra em números grandes."],
    [
        multiple_choice(
            "mat-pares-regra",
            "Qual destes números é ímpar?",
            ["37", "84", "50", "126"],
            "37",
            "Termina em 7, então é ímpar. Números terminados em 0, 2, 4, 6 ou 8 são pares.",
        ),
        true_false(
            "mat-pares-par",
            "Todo número terminado em 0 é par.",
            True,
            "Zero é divisível por 2, então qualquer número terminado em 0 é par.",
        ),
    ],
)

add(
    "mat-primos",
    ["Reconhecer números primos até 30.", "Testar divisores para classificar um número."],
    [
        multiple_choice(
            "mat-primos-lista",
            "Qual destes números é primo?",
            ["17", "21", "9", "15"],
            "17",
            "17 só divide por 1 e por 17. 21 = 3 × 7, 9 = 3 × 3 e 15 = 3 × 5.",
        ),
        true_false(
            "mat-primos-um",
            "O número 1 é primo.",
            False,
            "Primo precisa ter exatamente dois divisores. O 1 tem apenas um (ele mesmo), "
            "por isso não é primo.",
        ),
    ],
)

add(
    "mat-mdc",
    ["Calcular MDC e MMC de dois números.", "Reconhecer limites do MDC e do MMC."],
    [
        numeric_checked(
            "mat-mdc-dois",
            "Qual é o MDC de 12 e 18?",
            "6",
            "6 divide os dois e é o maior possível. Conferindo: 12 ÷ 6 = 2, 18 ÷ 6 = 3.",
            tolerance=0,
        ),
        numeric_checked(
            "mat-mmc-dois",
            "Qual é o MMC de 8 e 12?",
            "24",
            "24 é o menor número que 8 e 12 dividem: 24 ÷ 8 = 3, 24 ÷ 12 = 2.",
            tolerance=0,
        ),
    ],
)

add(
    "mat-potencias",
    ["Calcular potências de expoente pequeno.", "Calcular raízes quadradas exatas."],
    [
        numeric_checked(
            "mat-potencias-quadrado",
            "Quanto é 5²?",
            "5 ** 2",
            "5² = 5 × 5 = 25. O expoente 2 manda multiplicar o número por ele mesmo.",
            tolerance=0,
        ),
        numeric_checked(
            "mat-potencias-raiz",
            "Quanto é √49?",
            "49 ** 0.5",
            "√49 = 7, porque 7 × 7 = 49. Conferir elevando ao quadrado é o caminho "
            "inverso.",
            tolerance=0.001,
        ),
    ],
)

add(
    "mat-desconto",
    ["Calcular preço final com desconto.", "Comparar descontos de valores diferentes."],
    [
        numeric_checked(
            "mat-desconto-tenis",
            "Um tênis de R$ 200,00 com 30% de desconto sai por quanto?",
            "200 - 200 * 30 / 100",
            "30% de 200 = 60; 200 − 60 = R$ 140,00.",
            unit="reais",
        ),
        true_false(
            "mat-desconto-comparar",
            "50% de R$ 100,00 é mais dinheiro que 30% de R$ 200,00.",
            False,
            "50% de 100 = R$ 50,00; 30% de 200 = R$ 60,00. A porcentagem maior pode "
            "valer menos: o valor da base importa.",
        ),
    ],
)

add(
    "mat-planilha",
    ["Escrever fórmulas simples de planilha.", "Conferir resultado de fórmula na mão."],
    [
        multiple_choice(
            "mat-planilha-soma",
            "Para somar A1 até A10, qual fórmula usar?",
            ["=SOMA(A1:A10)", "=A1+A10", "=SOMA(A1;A10)", "SOMA A1 A10"],
            "=SOMA(A1:A10)",
            "A fórmula começa com = e usa dois-pontos para indicar um intervalo.",
        ),
        numeric_checked(
            "mat-planilha-conferir",
            "A coluna B tem 12, 18 e 25. Qual é o total que =SOMA(B1:B3) devolve?",
            "12 + 18 + 25",
            "12 + 18 + 25 = 55. Conferir na mão é a forma de detectar fórmula errada.",
            tolerance=0,
        ),
    ],
)

add(
    "mat-conversao",
    ["Converter unidades do sistema métrico.", "Escolher multiplicar ou dividir pela potência de dez."],
    [
        numeric_checked(
            "mat-conversao-km",
            "1500 m equivalem a quantos quilômetros?",
            "1500 / 1000",
            "1500 ÷ 1000 = 1,5 km. Para unidade maior, o número diminui.",
            unit="km",
        ),
        multiple_choice(
            "mat-conversao-direcao",
            "Ao converter 3 m para centímetros, o número:",
            ["Aumenta (×100)", "Diminui (÷100)", "Fica igual", "Depende do dia"],
            "Aumenta (×100)",
            "Unidade menor = mais pedaços = número maior: 3 m = 300 cm.",
        ),
    ],
)

add(
    "mat-escala",
    ["Interpretar escala de planta.", "Converter medida do desenho em medida real."],
    [
        numeric_checked(
            "mat-escala-real",
            "Na escala 1:50, uma parede desenhada com 4 cm corresponde a quantos metros "
            "reais?",
            "4 * 50 / 100",
            "4 × 50 = 200 cm = 2 m. Depois de multiplicar pela escala, converta para "
            "metro.",
            unit="m",
        ),
        multiple_choice(
            "mat-escala-significado",
            "Na escala 1:100, 1 cm no papel representa quanto na realidade?",
            ["1 metro", "100 metros", "10 centímetros", "1 centímetro"],
            "1 metro",
            "1 cm × 100 = 100 cm = 1 m. Escala é multiplicação, não soma.",
        ),
    ],
)

add(
    "mat-orcamento",
    ["Somar receitas e despesas.", "Calcular saldo do mês."],
    [
        numeric_checked(
            "mat-orcamento-saldo",
            "Receita de R$ 2.400,00 e despesas de R$ 2.150,00. Qual é o saldo?",
            "2400 - 2150",
            "2400 − 2150 = R$ 250,00 de sobra no mês.",
            unit="reais",
        ),
        true_false(
            "mat-orcamento-negativo",
            "Se as despesas passam da receita, o saldo do mês é negativo.",
            True,
            "Despesa maior que receita gera saldo negativo — dívida que precisa ser "
            "coberta no mês seguinte.",
        ),
    ],
)

add(
    "mat-juros",
    ["Calcular juros simples.", "Diferenciar juros de valor principal."],
    [
        numeric_checked(
            "mat-juros-simples",
            "R$ 1.000,00 a 2% ao mês por 3 meses, em juros simples. Quanto de juros?",
            "1000 * 0.02 * 3",
            "1000 × 0,02 × 3 = R$ 60,00 de juros. Nos juros simples a base não muda.",
            unit="reais",
        ),
        numeric_checked(
            "mat-juros-total",
            "Ainda no caso anterior, quanto se paga no total (principal + juros)?",
            "1000 + 1000 * 0.02 * 3",
            "1000 + 60 = R$ 1.060,00. O total é o valor emprestado mais os juros.",
            unit="reais",
        ),
    ],
)

add(
    "mat-tabela",
    ["Localizar dados em tabela.", "Cruzar linha e coluna corretamente."],
    [
        multiple_choice(
            "mat-tabela-cruzar",
            "Numa tabela de preços com produtos nas linhas e lojas nas colunas, para saber "
            "o preço do arroz na loja B você:",
            [
                "Segue a linha do arroz até a coluna B.",
                "Segue a coluna do arroz até a linha B.",
                "Soma a linha com a coluna.",
                "Procura o maior número da tabela.",
            ],
            "Segue a linha do arroz até a coluna B.",
            "O cruzamento linha × coluna é a célula certa. Trocar linha e coluna é o erro "
            "mais comum na leitura de tabelas.",
        ),
        numeric_checked(
            "mat-tabela-total",
            "Na coluna de gastos: mercado 240, transporte 90 e luz 110. Qual é o total?",
            "240 + 90 + 110",
            "240 + 90 + 110 = 440. Somar a coluna inteira dá o total do mês.",
            tolerance=0,
        ),
    ],
)

add(
    "mat-simetria",
    ["Identificar eixos de simetria.", "Reconhecer simetria em letras e objetos."],
    [
        multiple_choice(
            "mat-simetria-letra",
            "Qual letra tem simetria vertical?",
            ["A", "B", "F", "G"],
            "A",
            "A letra A, dobrada ao meio na vertical, coincide. B tem simetria "
            "horizontal; F e G não têm.",
        ),
        true_false(
            "mat-simetria-circulo",
            "O círculo tem infinitos eixos de simetria.",
            True,
            "Qualquer reta que passe pelo centro divide o círculo em duas metades iguais.",
        ),
    ],
)

add(
    "mat-nota-fiscal",
    ["Conferir subtotais em nota fiscal.", "Somar itens e comparar com o total impresso."],
    [
        numeric_checked(
            "mat-nota-subtotal",
            "3 unidades de um produto a R$ 4,50 cada. Qual é o subtotal?",
            "3 * 4.50",
            "3 × 4,50 = R$ 13,50. Subtotal = quantidade × preço unitário.",
            unit="reais",
        ),
        numeric_checked(
            "mat-nota-total",
            "Itens de R$ 13,50 e R$ 26,50. Qual é o total da compra?",
            "13.50 + 26.50",
            "13,50 + 26,50 = R$ 40,00. Se o total impresso for diferente, há erro na nota.",
            unit="reais",
        ),
    ],
)


def build() -> dict:
    return SPECS
