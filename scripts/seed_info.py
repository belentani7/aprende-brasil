"""Seed informática modules."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from api.database import SessionLocal
from api.models import Module, ModuleStep

db = SessionLocal()

def add(mid, title, sub, lvl, lo, dur, feat, steps):
    if db.get(Module, mid): return
    db.add(Module(id=mid, track_id="informatica", title=title, subtitle=sub, level=lvl,
                  level_order=lo, duration_min=dur, featured=feat, accent="blue", icon="Code2"))
    db.flush()
    for i, (tp, tt, tx) in enumerate(steps, 1):
        db.add(ModuleStep(module_id=mid, order=i, step_type=tp, title=tt,
                          content_json=json.dumps({"text": tx}, ensure_ascii=False)))

S = lambda t,e,p: [
    ("explanation", "Entender", t),
    ("example", "Ver na prática", e),
    ("practice", "Fazer", p),
    ("check", "Conferir", "Tente fazer sozinho(a) o que aprendeu. Peça ajuda se precisar."),
    ("next", "Próximo", "Muito bem! Continue para o próximo módulo.")]

# Alfabetização digital (10)
add("i-ligar", "Ligar e desligar", "Botão de energia e tela inicial.", "Começo", 0, 10, True,
    S("O computador ou celular liga quando você aperta o botão de energia. A tela acende e mostra ícones.",
      "No celular: segure o botão lateral por 3 segundos. No computador: aperte o botão maior na frente ou em cima.",
      "Ligue seu aparelho agora. Espere a tela inicial aparecer. Depois desligue e ligue de novo."))
add("i-mouse", "Usar o mouse", "Clicar, arrastar, rolar.", "Começo", 1, 12, False,
    S("O mouse move uma seta na tela. O botão esquerdo clica, o direito abre opções, a rodinha rola a página.",
      "Mova o mouse devagar. Veja a seta se mexer. Clique uma vez em um ícone — ele fica selecionado. Clique duas vezes — ele abre.",
      "Abra a pasta 'Documentos' com dois cliques. Depois use a rodinha para rolar uma página longa."))
add("i-teclado", "Conhecer o teclado", "Letras, números, espaço, enter.", "Começo", 1, 14, True,
    S("O teclado tem letras (A-Z), números (0-9), espaço (barra grande), enter (confirmar) e backspace (apagar).",
      "Abra um programa de texto. Digite seu nome. Aperte espaço. Digite seu sobrenome. Aperte enter para nova linha.",
      "Digite: 'Eu estou aprendendo a usar o computador.' Use maiúscula no início (Shift + letra)."))
add("i-celular", "Navegar no celular", "Tocar, deslizar, abrir apps.", "Começo", 2, 12, False,
    S("No celular, você toca na tela com o dedo. Toque = clicar. Deslizar = rolar. Segurar = opções.",
      "Toque em um app para abrir. Deslize para cima para ver mais. Toque no botão voltar (←) para sair.",
      "Abra 3 aplicativos diferentes. Volte para a tela inicial depois de cada um."))
add("i-wifi", "Conectar ao Wi-Fi", "Internet sem fio.", "Começo", 2, 10, False,
    S("Wi-Fi é internet sem fio. Seu aparelho precisa estar conectado a uma rede para acessar sites e apps.",
      "Vá em Configurações > Wi-Fi. Escolha a rede (pergunte o nome). Digite a senha. Espere conectar.",
      "Conecte ao Wi-Fi da sua casa ou do local onde está. Abra o navegador para testar."))
add("i-tela", "Entender a tela inicial", "Ícones, apps e notificações.", "Começo", 3, 10, False,
    S("A tela inicial mostra ícones (desenhinhos) que representam programas. Toque ou clique para abrir.",
      "No celular: câmera, telefone, mensagens, WhatsApp. No computador: pastas, navegador, lixeira.",
      "Encontre na sua tela: o navegador de internet, a câmera e as configurações."))
add("i-digitar", "Digitar no celular", "Teclado virtual e corretor.", "Começo", 3, 12, False,
    S("O teclado do celular aparece quando você toca em um campo de texto. Toque letra por letra.",
      "Abra o WhatsApp ou Notas. Toque no campo. O teclado aparece. Digite: 'Olá, tudo bem?'",
      "Mande uma mensagem para alguém: 'Estou aprendendo a digitar no celular!'"))
# Internet (8)
add("i-internet", "O que é a internet", "Rede que conecta o mundo.", "Essencial", 4, 15, False,
    S("A internet é uma rede que conecta computadores e celulares do mundo todo. Você acessa sites, manda mensagens e aprende.",
      "Quando você abre o Google, seu celular pede informação a um computador longe daqui. A resposta volta em segundos.",
      "Abra o navegador e digite google.com.br. Pesquise: 'capital do Brasil'. Leia o resultado."))
add("i-busca", "Pesquisar na internet", "Google: encontrar o que precisa.", "Essencial", 4, 14, True,
    S("O Google é um buscador. Você digita uma pergunta e ele mostra páginas com respostas.",
      "Digite 'receita de bolo de milho' no Google. Os primeiros resultados são os mais relevantes.",
      "Pesquise algo que você quer saber. Leia o primeiro resultado. A informação fez sentido?"))
add("i-navegador", "Usar o navegador", "Chrome, Firefox e a barra de endereço.", "Essencial", 5, 14, False,
    S("O navegador é o app que abre sites. Chrome é o mais comum. A barra no topo é onde você digita o endereço.",
      "Abra o Chrome. Na barra de cima, digite: g1.globo.com. Aperte enter. Você abriu um site de notícias.",
      "Abra 3 sites diferentes. Use o botão voltar (←) para retornar. Use abas para ter vários sites abertos."))
add("i-email", "Criar e usar e-mail", "Escrever, enviar e receber.", "Essencial", 5, 18, False,
    S("E-mail é uma carta digital. Você precisa de um endereço (exemplo@gmail.com) para enviar e receber.",
      "Para criar: acesse gmail.com > Criar conta. Escolha um nome, uma senha e pronto.",
      "Envie um e-mail para alguém: clique em 'Escrever', coloque o endereço, o assunto e a mensagem."))
add("i-senha", "Criar uma senha segura", "Proteger suas contas.", "Essencial", 6, 12, True,
    S("Senha é como a chave da sua casa digital. Deve ter letras, números e ser difícil de adivinhar.",
      "Senha fraca: 123456. Senha forte: MinhaFlor2024! Misture maiúsculas, minúsculas, números e símbolos.",
      "Crie uma senha forte agora. Anote em um lugar seguro (papel guardado, não no celular)."))
add("i-download", "Baixar arquivos", "Download seguro.", "Essencial", 6, 12, False,
    S("Download é copiar um arquivo da internet para seu aparelho. Fotos, documentos e apps são baixados assim.",
      "No navegador, quando clica em um link de arquivo, ele pergunta onde salvar. Escolha a pasta 'Downloads'.",
      "Baixe uma imagem do Google: pesquise 'bandeira do Brasil', toque na imagem, escolha 'Salvar imagem'."))
add("i-privacidade", "Privacidade online", "O que compartilhar e o que não.", "Essencial", 7, 14, False,
    S("Na internet, nem tudo deve ser compartilhado. CPF, senha, endereço e fotos íntimas devem ficar privados.",
      "Redes sociais pedem muitas informações. Você não precisa preencher tudo. Quanto menos, mais seguro.",
      "Revise suas configurações de privacidade no WhatsApp: quem vê sua foto? Quem vê seu status?"))
add("i-golpes", "Reconhecer golpes online", "Links falsos e mensagens suspeitas.", "Essencial", 7, 16, True,
    S("Golpistas enviam links falsos por WhatsApp, SMS e e-mail. Prometem prêmios, pedem senhas ou dados bancários.",
      "Mensagem suspeita: 'Parabéns! Você ganhou um iPhone. Clique aqui.' NUNCA clique. Bancos NUNCA pedem senha por mensagem.",
      "Olhe suas últimas mensagens. Tem alguma suspeita? Não clique. Delete. Na dúvida, ligue para a empresa."))
# Produtividade (10)
add("i-whatsapp", "Usar o WhatsApp", "Mensagens, fotos e grupos.", "Prática", 8, 16, False,
    S("WhatsApp é o app de mensagens mais usado no Brasil. Você conversa, envia fotos, áudios e documentos.",
      "Abra o WhatsApp. Toque em um contato. Digite uma mensagem. Toque na seta para enviar. Toque no microfone para áudio.",
      "Envie uma mensagem de texto e um áudio para alguém. Depois envie uma foto da sua câmera."))
add("i-fotos", "Organizar fotos", "Pastas, favoritos e espaço.", "Prática", 8, 14, False,
    S("Seu celular guarda todas as fotos na Galeria. Você pode criar pastas, marcar favoritos e apagar as que não quer.",
      "Abra a Galeria. Toque em uma foto. Toque no coração para favoritar. Toque na lixeira para apagar.",
      "Crie uma pasta chamada 'Família'. Mova 5 fotos para lá. Apague fotos borradas para liberar espaço."))
add("i-pix", "Fazer e receber Pix", "Transferências pelo celular.", "Prática", 9, 15, True,
    S("Pix é uma forma de enviar e receber dinheiro pelo celular, na hora, sem custo para pessoa física.",
      "Abra o app do banco. Escolha Pix. Você pode pagar com chave (CPF, telefone, e-mail) ou QR Code.",
      "Cadastre uma chave Pix no app do seu banco (pode ser seu CPF ou telefone)."))
add("i-maps", "Usar o Google Maps", "Encontrar endereços e rotas.", "Prática", 9, 14, False,
    S("Google Maps mostra mapas e calcula rotas. Você digita o destino e ele mostra como chegar.",
      "Abra o Google Maps. Digite 'hospital mais perto'. Ele mostra no mapa e a distância.",
      "Pesquise o caminho da sua casa até o mercado mais perto. Quanto tempo demora a pé?"))
add("i-youtube", "Assistir vídeos no YouTube", "Buscar, assistir e aprender.", "Prática", 10, 12, False,
    S("YouTube é um site de vídeos. Tem aulas, músicas, receitas, notícias — de tudo.",
      "Abra o YouTube. Pesquise 'como fazer arroz'. Toque no vídeo. Toque em pause para parar.",
      "Pesquise um vídeo sobre algo que quer aprender. Assista até o final."))
add("i-docs", "Usar Google Docs", "Escrever e salvar documentos.", "Prática", 10, 20, False,
    S("Google Docs é um programa de texto online. Você escreve, salva na nuvem e pode acessar de qualquer lugar.",
      "Acesse docs.google.com. Clique em 'Documento em branco'. Digite um texto. Ele salva automaticamente.",
      "Crie um documento e escreva uma carta. Mude o tamanho da letra e coloque o título em negrito."))
add("i-planilha", "Planilha de gastos", "Organizar dinheiro em tabelas.", "Intermediário", 11, 22, False,
    S("Uma planilha organiza informações em linhas e colunas. Perfeita para controlar gastos do mês.",
      "Abra Google Sheets. Coluna A: 'O quê'. Coluna B: 'Valor'. Linha 1: cabeçalho. Linhas 2-10: seus gastos.",
      "Monte sua planilha de gastos do mês. No final, use =SOMA(B2:B10) para somar tudo."))
add("i-curriculo", "Fazer um currículo", "Modelo simples para imprimir.", "Intermediário", 11, 25, True,
    S("O currículo apresenta você para um empregador: nome, contato, experiência e habilidades.",
      "Estrutura: 1) Nome e contato 2) Objetivo 3) Experiência 4) Educação 5) Habilidades.",
      "Abra o Google Docs. Crie seu currículo com seus dados reais. Salve e baixe como PDF."))
add("i-sus", "Agendar no SUS pelo app", "Meu SUS Digital.", "Intermediário", 12, 16, False,
    S("O app Meu SUS Digital permite agendar consultas, ver vacinas e acessar resultados de exames.",
      "Baixe o app 'Meu SUS Digital'. Faça login com o Gov.br. Veja seu cartão de vacinação digital.",
      "Acesse o app e encontre sua carteira de vacinação. Verifique se todas estão em dia."))
add("i-govbr", "Usar o Gov.br", "Serviços do governo pelo celular.", "Intermediário", 12, 18, False,
    S("O Gov.br é a conta do governo federal. Com ela você acessa serviços como INSS, carteira de trabalho digital e SUS.",
      "Acesse gov.br. Crie sua conta com CPF. Suba o nível com reconhecimento facial no app Gov.br.",
      "Faça login no Gov.br e acesse a Carteira de Trabalho Digital. Veja seus dados."))

db.commit()
c = db.query(Module).filter(Module.track_id == "informatica").count()
print(f"Informática: {c} módulos")
db.close()
