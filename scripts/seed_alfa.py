"""Seed alfabetização modules."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from api.database import engine, Base, SessionLocal
from api.models import Track, Module, ModuleStep

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Tracks
for t in [
    ("alfabetizacao", "Alfabetização", "Ler e escrever", "Primeiros passos na leitura e escrita.", "orange", "BookOpen", 200),
    ("informatica", "Informática", "Pensamento digital", "Do primeiro clique à criação digital.", "blue", "Code2", 680),
    ("matematica", "Matemática", "Raciocínio aplicado", "Números, formas e decisões reais.", "violet", "BarChart3", 720),
    ("idiomas", "Idiomas", "Comunicação global", "Inglês, espanhol e português no seu ritmo.", "green", "Languages", 600),
]:
    db.merge(Track(id=t[0], label=t[1], eyebrow=t[2], description=t[3], color=t[4], icon=t[5], target_modules=t[6]))
db.commit()


def add(mid, tid, title, sub, lvl, lo, dur, feat, steps_data):
    if db.get(Module, mid):
        return
    colors = {"alfabetizacao": "orange", "informatica": "blue", "matematica": "violet", "idiomas": "green"}
    icons = {"alfabetizacao": "BookOpen", "informatica": "Code2", "matematica": "BarChart3", "idiomas": "Languages"}
    db.add(Module(id=mid, track_id=tid, title=title, subtitle=sub, level=lvl, level_order=lo,
                  duration_min=dur, featured=feat, accent=colors[tid], icon=icons[tid]))
    db.flush()
    for i, (tp, tt, tx) in enumerate(steps_data, 1):
        db.add(ModuleStep(module_id=mid, order=i, step_type=tp, title=tt,
                          content_json=json.dumps({"text": tx}, ensure_ascii=False)))


T = "alfabetizacao"

# ── Nivel 1: Letras (7 módulos) ────────────────────────
add("a-vogais", T, "As cinco vogais", "A, E, I, O, U — os sons que abrem todas as palavras.", "Começo", 0, 8, True, [
    ("explanation", "O que são vogais", "As vogais são os sons mais abertos da fala. Em português temos cinco: A, E, I, O, U. Cada palavra precisa de pelo menos uma vogal."),
    ("example", "Vogais no dia a dia", "A de água, E de escola, I de igreja, O de ônibus, U de uva. Repita cada som em voz alta."),
    ("practice", "Encontre as vogais", "Olhe para estas palavras: CASA, MESA, LIVRO. Quais vogais aparecem em cada uma?"),
    ("check", "Verificação", "Escreva as cinco vogais em ordem. Depois escreva uma palavra que comece com cada vogal."),
    ("next", "Próximo passo", "Você conhece as cinco vogais! Agora vamos aprender as consoantes.")])

add("a-nome", T, "Escrever meu nome", "A primeira palavra que é só sua.", "Começo", 0, 8, True, [
    ("explanation", "Seu nome é especial", "Seu nome é a palavra mais importante que você vai aprender a escrever. Ele começa com letra maiúscula."),
    ("example", "Como funciona", "Se seu nome é ANA: A-N-A. Três letras, duas vogais e uma consoante."),
    ("practice", "Escreva o seu", "Pegue um papel. Escreva seu nome letra por letra. Repita três vezes."),
    ("check", "Confira", "Seu nome tem quantas letras? Quantas são vogais? Quantas são consoantes?"),
    ("next", "Parabéns", "Você escreveu seu nome! Agora pode assinar documentos.")])

cons_groups = [
    ("1", "B, C, D, F", "Bola, Casa, Dado, Faca"),
    ("2", "G, H, J, L", "Gato, Hospital, Janela, Lua"),
    ("3", "M, N, P, Q", "Mãe, Navio, Pão, Queijo"),
    ("4", "R, S, T, V", "Rio, Sol, Terra, Vida"),
    ("5", "X, Z, K, W, Y", "Xícara, Zebra, Kilo, Wilson, Yoga"),
]
for c, letras, palavras in cons_groups:
    add(f"a-cons-{c}", T, f"Consoantes: {letras}", f"Sons que formam sílabas: {palavras}.", "Começo", 1, 10, False, [
        ("explanation", "O som de cada letra", f"Vamos aprender o som das letras {letras}. Cada uma precisa de uma vogal para formar sílaba."),
        ("example", "Palavras com essas letras", f"Observe: {palavras}. Encontre a consoante que estamos estudando."),
        ("practice", "Forme palavras", f"Junte cada consoante ({letras}) com a vogal A. Que sílabas formou? Tente com E, I, O, U."),
        ("check", "Ditado", "Alguém diz uma palavra da lista e você escreve a primeira letra."),
        ("next", "Avance", "Mais consoantes dominadas! Continue.")])

# ── Nivel 2: Sílabas (10 módulos) ──────────────────────
sil_modules = [
    ("simples", "Sílabas simples: BA, CA, DA", "Consoante + vogal = sílaba.", True,
     "BA de bala, CA de casa, DA de dado, FA de faca, GA de gato.",
     "Escreva todas as sílabas de B com cada vogal: BA, BE, BI, BO, BU."),
    ("complexas", "Sílabas com encontro: BRA, CRI", "Duas consoantes antes da vogal.", False,
     "BRA de Brasil, CRI de criança, FLO de flor, PRA de praia.",
     "Forme sílabas: BR+A, CR+I, FL+O. Que palavras você conhece?"),
    ("nasais", "Sílabas nasais: AN, EM, IN", "Sons que vibram no nariz.", False,
     "AN de antes, EM de tempo, IN de índio, ON de onda.",
     "Tape o nariz e tente falar AN. Sentiu a diferença?"),
    ("fechadas", "Sílabas fechadas: AR, ES, IS", "Vogal antes da consoante.", False,
     "AR de arco, ES de escola, IS de isto, OR de ordem.",
     "Divida: ESCOLA = ES-CO-LA. Quais sílabas são fechadas?"),
    ("ditongo", "Ditongos: AI, EI, OU", "Duas vogais na mesma sílaba.", False,
     "AI de pai, EI de leite, OU de ouro, AU de aula.",
     "PAI, MÃE, CÉU — quais vogais ficam juntas?"),
    ("divisao", "Dividir palavras em sílabas", "Separar para ler melhor.", True,
     "CA-SA (2), ES-CO-LA (3), COM-PU-TA-DOR (4).",
     "Divida: BANANA, CADERNO, COMPUTADOR, FELICIDADE."),
    ("tonicas", "Sílaba tônica", "A sílaba mais forte.", False,
     "caFÉ, EScola, caDERno. A sílaba forte é a tônica.",
     "Fale JANELA em voz alta. Qual sílaba é mais forte?"),
    ("acento", "Quando usar acento", "O acento marca sons especiais.", False,
     "café (aguda), lápis (paroxítona), médico (proparoxítona).",
     "Leia: AVIÃO, CAFÉ, SAÚDE. Onde está o acento?"),
    ("cedilha", "Ç e sons especiais", "Quando C vira Ç.", False,
     "Ç antes de A, O, U: açaí, coração, açúcar.",
     "Complete: cora___ão, a___úcar, a___aí. Use C ou Ç."),
    ("familia", "Famílias silábicas", "Todas as sílabas de uma letra.", False,
     "Família do B: BA, BE, BI, BO, BU. Família do M: MA, ME, MI, MO, MU.",
     "Escreva a família completa da letra P e da letra D."),
]
for i, (sid, title, sub, feat, ex, pract) in enumerate(sil_modules):
    add(f"a-sil-{sid}", T, title, sub, "Essencial", 2 + i // 2, 12, feat, [
        ("explanation", "Entender", f"Vamos aprender: {sub}"),
        ("example", "Exemplos", ex),
        ("practice", "Praticar", pract),
        ("check", "Verificar", "Escreva 5 palavras que usem o que aprendeu. Divida em sílabas."),
        ("next", "Próximo", "Ótimo trabalho com as sílabas!")])

# ── Nivel 3: Palavras (15 módulos) ─────────────────────
pal_modules = [
    ("corpo", "Palavras do corpo", "Mão, pé, olho, boca.", True,
     "mão, pé, olho, boca, nariz, orelha, dedo, braço, perna, cabeça",
     "Aponte para cada parte do corpo e diga o nome."),
    ("casa", "Palavras da casa", "Porta, mesa, cama, janela.", False,
     "porta, mesa, cama, janela, cadeira, fogão, geladeira, sofá",
     "Olhe ao redor. Aponte para cada objeto e diga o nome."),
    ("comida", "Palavras da comida", "Arroz, feijão, pão, café.", True,
     "arroz, feijão, pão, café, água, leite, carne, fruta, sal, açúcar",
     "Monte uma lista de compras com 5 itens."),
    ("familia", "Palavras da família", "Mãe, pai, filho, avó.", False,
     "mãe, pai, filho, filha, irmão, irmã, avô, avó, tio, tia",
     "Escreva o nome de cada pessoa da sua família."),
    ("rua", "Palavras da rua", "Ônibus, escola, mercado.", False,
     "ônibus, escola, mercado, hospital, farmácia, banco, igreja, praça",
     "Pense no caminho de casa ao mercado. Que lugares você passa?"),
    ("numeros", "Números por extenso", "Um, dois, três até vinte.", False,
     "um, dois, três, quatro, cinco, seis, sete, oito, nove, dez",
     "Escreva os números de 1 a 20 por extenso."),
    ("cores", "Palavras das cores", "Vermelho, azul, amarelo.", False,
     "vermelho, azul, amarelo, verde, branco, preto, marrom, rosa",
     "De que cor é sua roupa? E a parede? Escreva."),
    ("dias", "Dias e meses", "Segunda, terça... janeiro...", False,
     "segunda, terça, quarta, quinta, sexta, sábado, domingo",
     "Que dia é hoje? Escreva o dia e o mês por extenso."),
    ("animais", "Palavras dos animais", "Cachorro, gato, pássaro.", False,
     "cachorro, gato, pássaro, peixe, cavalo, galinha, vaca, borboleta",
     "Escreva 5 animais que você já viu. Divida em sílabas."),
    ("trabalho", "Palavras do trabalho", "Emprego, salário, contrato.", False,
     "emprego, salário, contrato, horário, carteira, férias, tarefa",
     "Quais dessas palavras você já usou? Escreva uma frase com cada."),
    ("saude", "Palavras da saúde", "Médico, remédio, consulta.", False,
     "médico, remédio, consulta, receita, posto, vacina, dor, febre",
     "Imagine no posto de saúde. Que palavras precisa saber?"),
    ("documentos", "Palavras de documentos", "CPF, RG, certidão.", True,
     "CPF, RG, certidão, identidade, assinatura, endereço, nascimento",
     "Pratique: nome completo, data de nascimento e endereço."),
    ("natureza", "Palavras da natureza", "Sol, chuva, rio, árvore.", False,
     "sol, chuva, rio, árvore, flor, terra, céu, nuvem, mar, montanha",
     "Olhe pela janela. Escreva 5 coisas da natureza."),
    ("emocoes", "Palavras das emoções", "Alegria, tristeza, medo.", False,
     "alegria, tristeza, medo, raiva, amor, saudade, esperança, paz",
     "Como está se sentindo agora? Escreva o nome dessa emoção."),
    ("compras", "Palavras das compras", "Preço, troco, nota fiscal.", False,
     "preço, troco, nota, desconto, caixa, fila, sacola, pagamento",
     "Escreva uma lista de compras com nome e preço de 5 produtos."),
]
for i, (wid, title, sub, feat, words, pract) in enumerate(pal_modules):
    add(f"a-pal-{wid}", T, title, sub, "Prática", 5 + i // 3, 12, feat, [
        ("explanation", "Palavras do tema", f"{title}: palavras que você usa no dia a dia."),
        ("example", "Veja e repita", f"Palavras: {words}. Leia cada uma em voz alta."),
        ("practice", "Escreva", pract),
        ("check", "Ditado", "Peça para alguém ditar 5 palavras do tema. Escreva e confira."),
        ("next", "Muito bem", "Seu vocabulário está crescendo!")])

# ── Nivel 4: Frases (10 módulos) ───────────────────────
fra_modules = [
    ("simples", "Minha primeira frase", "Sujeito + verbo.", True,
     "Eu leio. Ela canta. Ele corre. Nós brincamos."),
    ("completa", "Frases com complemento", "Sujeito + verbo + objeto.", False,
     "Eu leio um livro. Ela canta uma música. Ele corre no parque."),
    ("pergunta", "Fazer perguntas", "Como, quando, onde, por quê.", False,
     "Como você se chama? Onde mora? Quando é seu aniversário?"),
    ("negativa", "Frases negativas", "Usando NÃO.", False,
     "Eu não sei. Ela não veio. Nós não temos."),
    ("bilhete", "Escrever um bilhete", "Comunicar algo simples.", True,
     "Mãe, fui ao mercado. Volto às 5. Beijos, Ana."),
    ("lista", "Escrever uma lista", "Organizar itens.", False,
     "Lista: 1. Arroz 2. Feijão 3. Óleo 4. Sal 5. Café"),
    ("recado", "Dar um recado", "Informar alguém.", False,
     "Dona Maria ligou. Pediu para ligar amanhã às 10h."),
    ("convite", "Escrever um convite", "Chamar alguém.", False,
     "Venha para o aniversário! Dia 15, às 15h, na casa da vovó."),
    ("descricao", "Descrever algo", "Dizer como algo é.", False,
     "Minha casa é pequena. Tem dois quartos e uma cozinha."),
    ("opiniao", "Dar sua opinião", "Dizer o que pensa.", False,
     "Eu acho que estudar é importante. Gosto de aprender."),
]
for i, (fid, title, sub, feat, ex) in enumerate(fra_modules):
    add(f"a-fra-{fid}", T, title, sub, "Intermediário", 8 + i // 2, 15, feat, [
        ("explanation", "Como montar", f"Vamos aprender a {title.lower()}."),
        ("example", "Exemplos", ex),
        ("practice", "Escreva", "Agora escreva 3 frases do mesmo tipo com suas palavras."),
        ("check", "Revisão", "Releia. Faz sentido? Tem ponto final? Começa com maiúscula?"),
        ("next", "Avance", "Sua escrita está evoluindo!")])

# ── Nivel 5: Textos (8 módulos) ────────────────────────
txt_modules = [
    ("receita", "Ler uma receita", "Ingredientes e modo de fazer.", True),
    ("noticia", "Ler uma notícia", "O que, onde, quando.", False),
    ("carta", "Escrever uma carta", "Saudação, mensagem, despedida.", False),
    ("formulario", "Preencher um formulário", "Nome, CPF, endereço.", True),
    ("placa", "Ler placas e avisos", "Informações do dia a dia.", False),
    ("conta", "Ler uma conta de luz", "Valor, vencimento, código.", False),
    ("bula", "Ler uma bula de remédio", "Dose, horário, efeitos.", False),
    ("contrato", "Entender um contrato", "Partes, obrigações, assinatura.", False),
]
for i, (tid2, title, sub, feat) in enumerate(txt_modules):
    add(f"a-txt-{tid2}", T, title, sub, "Avançado", 12 + i // 2, 20, feat, [
        ("explanation", "O que é", f"Vamos aprender a {title.lower()}."),
        ("example", "Exemplo real", f"Veja este exemplo de {sub.lower()}."),
        ("practice", "Faça você", "Pratique com um exemplo real do seu dia a dia."),
        ("check", "Compreensão", "O que entendeu? Quais informações são mais importantes?"),
        ("next", "Parabéns", "Você está lendo e escrevendo textos reais!")])

db.commit()
c = db.query(Module).filter(Module.track_id == "alfabetizacao").count()
print(f"Alfabetização: {c} módulos")
db.close()
