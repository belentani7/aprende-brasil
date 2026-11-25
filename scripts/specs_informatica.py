"""Atividades de Informática (40 módulos) — campus digital.

Cada módulo pede uma decisão concreta (clicar, configurar, desconfiar, conferir),
não memorização de nomes de botões. Os laboratórios interativos da interface
usam estas mesmas situações: teclado, senha, planilha, HTML e fraude.
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
    "info-ligar",
    ["Ligar e desligar o computador com segurança.", "Reconhecer o risco de desligar na tomada."],
    [
        multiple_choice(
            "info-ligar-desligar",
            "Qual é a forma correta de desligar o computador?",
            [
                "Pelo menu do sistema (Iniciar → Desligar).",
                "Tirando o cabo da tomada.",
                "Segurando o botão por 10 segundos sempre.",
                "Fechando a tampa sem salvar.",
            ],
            "Pelo menu do sistema (Iniciar → Desligar).",
            "O menu permite que o sistema feche os programas e grave os arquivos. Na "
            "tomada, os arquivos abertos podem corromper.",
        ),
        true_false(
            "info-ligar-tomada",
            "Puxar a tomada com o computador ligado é uma forma segura de desligar.",
            False,
            "Além do risco de perder arquivos, isso desgasta componentes. Use sempre o "
            "menu; o botão físico por alguns segundos é só para travamentos.",
        ),
    ],
)

add(
    "info-mouse",
    ["Usar clique, duplo clique e arrastar.", "Diferenciar botão esquerdo e direito."],
    [
        matching(
            "info-mouse-acoes",
            "Ligue cada ação ao resultado:",
            [
                ("um clique", "selecionar o arquivo"),
                ("dois cliques", "abrir o arquivo"),
                ("botão direito", "ver opções do item"),
                ("arrastar", "mover o item para outra pasta"),
            ],
            "Cada gesto do mouse tem uma função fixa. Confundir selecionar com abrir é o "
            "erro mais comum de quem está começando.",
        ),
        multiple_choice(
            "info-mouse-seta",
            "A seta do mouse não se move. O que verificar primeiro?",
            [
                "Se o cabo ou o adaptador está bem encaixado / bateria carregada",
                "Reinstalar o sistema",
                "Comprar outro computador",
                "Apagar arquivos",
            ],
            "Se o cabo ou o adaptador está bem encaixado / bateria carregada",
            "Antes de qualquer coisa, verifique a conexão física. É a causa mais frequente.",
        ),
    ],
)

add(
    "info-teclado",
    ["Reconhecer teclas de ação.", "Usar atalhos de edição básicos."],
    [
        matching(
            "info-teclado-teclas",
            "Ligue cada tecla à sua função:",
            [
                ("Enter", "confirmar"),
                ("Backspace", "apagar à esquerda"),
                ("Shift", "escrever maiúscula"),
                ("Barra de espaço", "separar palavras"),
            ],
            "As teclas de ação fazem o trabalho aparecer no lugar de ler letra por letra.",
        ),
        multiple_choice(
            "info-teclado-caps",
            "Você escreve e sai tudo em MAIÚSCULA sem querer. Qual tecla está ligada?",
            ["Caps Lock", "Shift", "Ctrl", "Alt"],
            "Caps Lock",
            "Caps Lock trava o teclado em maiúsculas. Aperte uma vez para desligar — o "
            "indicador luminoso apaga.",
        ),
        fill_blank(
            "info-teclado-atalho",
            "Para copiar um texto selecionado usa-se Ctrl + ___.",
            ["C"],
            "Ctrl + C copia, Ctrl + V cola e Ctrl + X recorta. São os três atalhos mais "
            "usados no dia a dia.",
        ),
    ],
)

add(
    "info-celular",
    ["Navegar por toque, deslize e pinça.", "Voltar à tela inicial e fechar apps."],
    [
        multiple_choice(
            "info-celular-pinca",
            "Para aumentar o zoom de uma foto no celular, você:",
            [
                "Afasta dois dedos sobre a tela (pinça para fora).",
                "Toca uma vez.",
                "Desliga e liga o aparelho.",
                "Gira o aparelho.",
            ],
            "Afasta dois dedos sobre a tela (pinça para fora).",
            "Pinça para fora aproxima (zoom); pinça para dentro afasta. É o mesmo gesto em "
            "mapas e fotos.",
        ),
        true_false(
            "info-celular-travou",
            "Se um aplicativo trava, reiniciar o aparelho resolve a maioria dos casos.",
            True,
            "Reiniciar libera memória e fecha processos travados. Se continuar, atualize "
            "ou desinstale o aplicativo.",
        ),
    ],
)

add(
    "info-internet",
    ["Explicar o que é a internet.", "Identificar o cadeado de conexão segura."],
    [
        multiple_choice(
            "info-internet-cadeado",
            "O cadeado ao lado do endereço do site indica que:",
            [
                "A conexão é criptografada (HTTPS).",
                "O site é oficial do governo.",
                "O conteúdo foi revisado.",
                "O site é gratuito.",
            ],
            "A conexão é criptografada (HTTPS).",
            "Cadeado significa conexão segura, não site confiável. Um golpe também pode "
            "ter cadeado: confira sempre o endereço.",
        ),
        true_false(
            "info-internet-wifi",
            "Sem conexão com a internet, nenhuma página nova carrega.",
            True,
            "A página precisa ser baixada do servidor. Sem conexão, só o que já está "
            "salvo no aparelho aparece.",
        ),
    ],
)

add(
    "info-busca",
    ["Escrever buscas específicas.", "Escolher palavras-chave melhores."],
    [
        multiple_choice(
            "info-busca-especifica",
            "Qual busca tende a trazer resultado mais útil?",
            [
                "como ler conta de luz vencimento",
                "conta",
                "luz",
                "coisas de banco",
            ],
            "como ler conta de luz vencimento",
            "Quanto mais específicas as palavras, melhor o resultado. Palavras soltas "
            "trazem milhares de páginas irrelevantes.",
        ),
        true_false(
            "info-busca-aspas",
            "Colocar uma expressão entre aspas faz o buscador procurar exatamente aquelas "
            "palavras juntas.",
            True,
            "As aspas restringem a busca à expressão exata — útil para nomes e leis. "
            "Aspas viram obrigatórias no resultado.",
        ),
    ],
)

add(
    "info-email",
    ["Preencher destinatário, assunto e corpo.", "Reconhecer um e-mail suspeito."],
    [
        ordering(
            "info-email-ordem",
            "Ordene as etapas para enviar um e-mail:",
            [
                "Escrever o endereço em Para",
                "Preencher o Assunto",
                "Escrever a mensagem",
                "Clicar em Enviar",
            ],
        ),
        multiple_choice(
            "info-email-suspeito",
            "Qual sinal indica que um e-mail pode ser golpe?",
            [
                "Urgência para clicar em um link e pedir dados",
                "Ter o seu nome no texto",
                "Ter assunto claro",
                "Vir de um colega de trabalho",
            ],
            "Urgência para clicar em um link e pedir dados",
            "Pressa + pedido de dados + link desconhecido é a combinação clássica de "
            "golpe. Confira o endereço real de quem enviou.",
        ),
        fill_blank(
            "info-email-arroba",
            "No endereço nome@provedor.com, o símbolo que separa nome e provedor é o ___.",
            ["@", "arroba"],
            "O @ (arroba) separa o nome da pessoa do domínio do provedor.",
        ),
    ],
)

add(
    "info-senha",
    ["Criar senhas longas e memoráveis.", "Reconhecer senhas fracas."],
    [
        multiple_choice(
            "info-senha-melhor",
            "Qual destas senhas é mais segura?",
            [
                "Cafe-com-Leite#72",
                "123456",
                "maria1978",
                "senha123",
            ],
            "Cafe-com-Leite#72",
            "Comprimento + variedade + palavras que só você associa: fácil de lembrar, "
            "difícil de adivinhar. Datas e sequências são as primeiras testadas.",
        ),
        true_false(
            "info-senha-mesma",
            "Usar a mesma senha em todos os sites é seguro se ela for longa.",
            False,
            "Se um site vazar a senha, todas as outras contas ficam expostas. Use senhas "
            "diferentes, ao menos para banco e e-mail.",
        ),
        fill_blank(
            "info-senha-dois-fatores",
            "Além da senha, o código enviado por SMS ou aplicativo é a verificação em ___ "
            "etapas.",
            ["duas", "2"],
            "Verificação em duas etapas (2FA) exige senha + código. Mesmo que alguém "
            "descubra a senha, não consegue entrar.",
        ),
    ],
)

add(
    "info-pix",
    ["Enviar e receber Pix com conferência.", "Reconhecer pedido de Pix fraudulento."],
    [
        ordering(
            "info-pix-ordem",
            "Ordene o envio de um Pix:",
            [
                "Abrir o aplicativo do banco",
                "Informar a chave do destinatário",
                "Conferir o nome de quem recebe",
                "Confirmar com a senha",
            ],
        ),
        multiple_choice(
            "info-pix-golpe",
            "Alguém liga dizendo ser do banco e pede um Pix para “cancelar uma compra”. O "
            "que fazer?",
            [
                "Desligar e ligar para o número do cartão.",
                "Fazer o Pix para resolver rápido.",
                "Passar a senha por telefone.",
                "Enviar o código por SMS.",
            ],
            "Desligar e ligar para o número do cartão.",
            "Banco não pede Pix para cancelar compra nem pede senha por telefone. Desligue "
            "e procure o canal oficial.",
        ),
    ],
)

add(
    "info-curriculo",
    ["Montar currículo de duas páginas no máximo.", "Ordenar informação por relevância."],
    [
        ordering(
            "info-curriculo-ordem",
            "Ordene as seções de um currículo simples:",
            [
                "Nome e contato",
                "Experiência profissional",
                "Formação",
                "Habilidades",
            ],
        ),
        true_false(
            "info-curriculo-foto",
            "Colocar foto, CPF e estado civil é obrigatório em qualquer currículo no "
            "Brasil.",
            False,
            "Não é obrigatório e pode até expor dados desnecessários. Foque em "
            "experiência, formação e habilidades.",
        ),
    ],
)

add(
    "info-arquivos",
    ["Criar pastas e nomear arquivos.", "Encontrar um arquivo pela busca."],
    [
        multiple_choice(
            "info-arquivos-nome",
            "Qual nome de arquivo é mais fácil de encontrar depois?",
            [
                "2026-03-conta-luz.pdf",
                "conta.pdf",
                "documento1.pdf",
                "aaaa.pdf",
            ],
            "2026-03-conta-luz.pdf",
            "Data + assunto no nome permite ordenar e buscar. Nomes genéricos viram "
            "dezenas de arquivos iguais.",
        ),
        matching(
            "info-arquivos-pastas",
            "Ligue cada pasta ao que guardar dentro dela:",
            [
                ("Contas", "conta de luz e de água"),
                ("Saúde", "receitas e exames"),
                ("Trabalho", "contrato e holerites"),
            ],
            "Separar por assunto é mais rápido do que guardar tudo em uma pasta única.",
        ),
    ],
)

add(
    "info-fotos",
    ["Organizar fotos em pastas.", "Liberar espaço apagando duplicadas."],
    [
        multiple_choice(
            "info-fotos-organizar",
            "Qual organização facilita achar uma foto depois?",
            [
                "Pastas por assunto (Família, Viagens, Documentos)",
                "Todas em uma pasta única",
                "Apagar as mais antigas",
                "Renomear todas com números",
            ],
            "Pastas por assunto (Família, Viagens, Documentos)",
            "Pastas temáticas reduzem a rolagem infinita. Nomes de pastas que você entende "
            "valem mais que qualquer sistema automático.",
        ),
        true_false(
            "info-fotos-espaco",
            "Fotos ocupam pouco espaço no celular.",
            False,
            "Fotos e vídeos são os arquivos que mais ocupam espaço. Apagar duplicadas e "
            "tremidas libera memória rapidamente.",
        ),
    ],
)

add(
    "info-planilha",
    ["Entender linhas, colunas e células.", "Escrever uma fórmula de soma."],
    [
        multiple_choice(
            "info-planilha-celula",
            "A célula B3 fica:",
            [
                "Na coluna B, linha 3.",
                "Na linha B, coluna 3.",
                "Na terceira planilha, coluna B.",
                "Fora da planilha.",
            ],
            "Na coluna B, linha 3.",
            "Primeiro a letra (coluna), depois o número (linha): B3. A fórmula começa "
            "sempre com =.",
        ),
        fill_blank(
            "info-planilha-formula",
            "Para somar de B2 até B10, a fórmula é =___ (B2:B10).",
            ["SOMA"],
            "=SOMA(B2:B10) soma o intervalo inteiro. Toda fórmula começa com sinal de "
            "igual.",
        ),
    ],
)

add(
    "info-golpes",
    ["Reconhecer sinais de golpe.", "Adotar hábito de verificação antes de clicar."],
    [
        multiple_choice(
            "info-golpes-sinal",
            "Qual é o sinal mais típico de golpe online?",
            [
                "Urgência + pedido de dados ou dinheiro",
                "Texto com boa formatação",
                "Mensagem curta",
                "Uso de imagem",
            ],
            "Urgência + pedido de dados ou dinheiro",
            "Pressa para decidir é a ferramenta do golpe: impede que você confira. "
            "Desconfie de prêmio que expira, boleto urgente e bloqueio de conta.",
        ),
        true_false(
            "info-golpes-banco",
            "O banco pode pedir sua senha por mensagem para desbloquear a conta.",
            False,
            "Banco nunca pede senha por mensagem, telefone ou e-mail. Quem pede é golpista.",
        ),
        matching(
            "info-golpes-sinais",
            "Ligue cada situação à atitude correta:",
            [
                ("Link de prêmio desconhecido", "não clicar"),
                ("Boleto com valor estranho", "conferir no site oficial"),
                ("Ligação pedindo senha", "desligar"),
            ],
            "Conferir pelo canal oficial é sempre mais seguro que responder à mensagem "
            "recebida.",
        ),
    ],
)

add(
    "info-whatsapp",
    ["Enviar mensagens, áudio e foto.", "Entender os tiques de confirmação."],
    [
        multiple_choice(
            "info-whatsapp-tiques",
            "Dois tiques azuis significam que a mensagem foi:",
            ["Lida", "Enviada", "Entregue", "Apagada"],
            "Lida",
            "Um tique: enviada. Dois: entregue. Dois azuis: lida (se a pessoa não "
            "desativou a confirmação).",
        ),
        true_false(
            "info-whatsapp-audio",
            "Para cancelar um áudio antes de enviar, arrasta-se o dedo para o lado.",
            True,
            "Arrastar para o lado cancela o áudio gravado. Soltar o dedo envia.",
        ),
    ],
)

add(
    "info-docs",
    ["Escrever, formatar e salvar documento.", "Reconhecer o risco de não salvar."],
    [
        multiple_choice(
            "info-docs-salvar",
            "Você escreveu um texto e fechou o programa sem salvar. O que acontece?",
            [
                "O texto se perde.",
                "O programa salva sozinho sempre.",
                "O texto vai para a lixeira.",
                "O texto fica no teclado.",
            ],
            "O texto se perde.",
            "Sem salvar (Ctrl + S) ou salvamento automático ativo, o conteúdo fica só na "
            "memória e se perde ao fechar.",
        ),
        fill_blank(
            "info-docs-negrito",
            "O atalho Ctrl + ___ deixa o texto em negrito.",
            ["B"],
            "Ctrl + B (bold) aplica negrito; Ctrl + I, itálico; Ctrl + U, sublinhado.",
        ),
    ],
)

add(
    "info-compras",
    ["Comprar online com segurança.", "Conferir loja, preço e forma de pagamento."],
    [
        multiple_choice(
            "info-compras-antebraco",
            "Antes de comprar em uma loja desconhecida, o mais seguro é:",
            [
                "Procurar reclamações e CNPJ da loja.",
                "Pagar por Pix para ganhar desconto.",
                "Confiar no preço baixo.",
                "Enviar documentos por mensagem.",
            ],
            "Procurar reclamações e CNPJ da loja.",
            "Preço muito abaixo do mercado e pressa para pagar por Pix são sinais de "
            "fraude. Confira o CNPJ e a reputação antes.",
        ),
        true_false(
            "info-compras-boleto",
            "Boleto enviado por WhatsApp de uma loja deve ser pago sem conferir.",
            False,
            "Boleto falso é comum. Confira sempre o beneficiário no app do banco antes de "
            "pagar.",
        ),
    ],
)

add(
    "info-videochamada",
    ["Participar de videochamada.", "Cuidar da privacidade e do áudio."],
    [
        ordering(
            "info-videochamada-ordem",
            "Ordene o preparo para uma videochamada:",
            [
                "Testar câmera e microfone",
                "Verificar a conexão de internet",
                "Silenciar o microfone quando não estiver falando",
                "Entrar na sala no horário",
            ],
        ),
        true_false(
            "info-videochamada-fundo",
            "Mostrar documentos na câmera durante uma chamada é sempre seguro.",
            False,
            "Documentos expõem dados pessoais para todos na chamada e para quem gravar. "
            "Combine antes o que será mostrado.",
        ),
    ],
)

add(
    "info-nuvem",
    ["Entender armazenamento em nuvem.", "Escolher o que sincronizar."],
    [
        multiple_choice(
            "info-nuvem-vantagem",
            "Qual é a principal vantagem de guardar arquivos na nuvem?",
            [
                "Acessar de qualquer aparelho e recuperar se o aparelho quebrar.",
                "Deixar o arquivo mais rápido.",
                "Ocupar espaço no celular.",
                "Evitar a necessidade de senha.",
            ],
            "Acessar de qualquer aparelho e recuperar se o aparelho quebrar.",
            "A nuvem é cópia em outro lugar: serve como backup e acesso remoto. Não "
            "dispensa senha forte.",
        ),
        true_false(
            "info-nuvem-privacidade",
            "Qualquer pessoa com o link de um arquivo na nuvem pode ver o conteúdo, mesmo "
            "sem permissão.",
            False,
            "Só quem tem permissão ou o link compartilhado (quando habilitado) acessa. "
            "Compartilhar link público é uma escolha sua.",
        ),
    ],
)

add(
    "info-impressora",
    ["Preparar e enviar documento para impressão.", "Resolver fila de impressão travada."],
    [
        ordering(
            "info-impressora-ordem",
            "Ordene o processo de impressão:",
            [
                "Abrir o documento",
                "Usar Ctrl + P",
                "Escolher a impressora e as páginas",
                "Confirmar a impressão",
            ],
        ),
        multiple_choice(
            "info-impressora-fila",
            "O documento não sai e há outros na fila. O que fazer?",
            [
                "Cancelar os trabalhos travados na fila e imprimir de novo.",
                "Desligar a impressora da tomada.",
                "Trocar o computador.",
                "Imprimir várias vezes.",
            ],
            "Cancelar os trabalhos travados na fila e imprimir de novo.",
            "Um trabalho travado bloqueia os seguintes. Cancelar a fila é a solução mais "
            "rápida.",
        ),
    ],
)

add(
    "info-mapa",
    ["Usar GPS e traçar rota.", "Escolher meio de transporte no app."],
    [
        multiple_choice(
            "info-mapa-rota",
            "Para ir a pé até um endereço próximo, no app de mapas você:",
            [
                "Digita o endereço e escolhe o modo a pé.",
                "Escolhe o modo carro sempre.",
                "Desliga o GPS.",
                "Digita só o nome da cidade.",
            ],
            "Digita o endereço e escolhe o modo a pé.",
            "O modo define a rota: a pé pode usar passagens que carro não usa. Escolher "
            "certo evita caminhada desnecessária.",
        ),
        true_false(
            "info-mapa-offline",
            "Sem internet, o app de mapas não consegue mostrar nenhum mapa.",
            False,
            "É possível baixar mapas de uma região para uso offline. O cálculo de rota "
            "fica limitado, mas o mapa aparece.",
        ),
    ],
)

add(
    "info-banco",
    ["Consultar saldo e extrato.", "Pagar conta com código de barras."],
    [
        ordering(
            "info-banco-pagar",
            "Ordene o pagamento de uma conta no app do banco:",
            [
                "Abrir o aplicativo do banco",
                "Escolher Pagar",
                "Ler o código de barras com a câmera",
                "Conferir valor e confirmar",
            ],
        ),
        multiple_choice(
            "info-banco-seguranca",
            "Qual cuidado protege mais o acesso ao app do banco?",
            [
                "Verificação em duas etapas e senha diferente das outras contas",
                "Anotar a senha no celular",
                "Usar a mesma senha de tudo",
                "Compartilhar a senha com um parente",
            ],
            "Verificação em duas etapas e senha diferente das outras contas",
            "A conta bancária merece a senha exclusiva e mais forte. Duas etapas impedem "
            "acesso mesmo se a senha vazar.",
        ),
    ],
)

add(
    "info-sus",
    ["Acessar serviços públicos digitais.", "Identificar dados necessários no gov.br."],
    [
        multiple_choice(
            "info-sus-acesso",
            "Para agendar consulta e ver o cartão de vacinação no aplicativo do SUS, "
            "normalmente é preciso:",
            [
                "Conta gov.br (CPF e senha).",
                "Apenas o nome completo.",
                "Um e-mail de qualquer provedor.",
                "Número do cartão de crédito.",
            ],
            "Conta gov.br (CPF e senha).",
            "A conta gov.br identifica você nos serviços federais. Nunca peça ajuda a "
            "terceiros para criar sua senha.",
        ),
        true_false(
            "info-sus-golpe",
            "Um site que cobra taxa para “liberar” o cartão de vacinação no SUS é oficial.",
            False,
            "Serviços do SUS são gratuitos. Cobrança para liberar documento público é "
            "golpe.",
        ),
    ],
)

add(
    "info-usb",
    ["Conectar e ejetar pendrive com segurança.", "Reconhecer risco de perda de dados."],
    [
        ordering(
            "info-usb-ordem",
            "Ordene o uso seguro de um pendrive:",
            [
                "Conectar o pendrive na porta USB",
                "Abrir a pasta do pendrive",
                "Copiar o arquivo até terminar",
                "Ejetar com segurança antes de retirar",
            ],
        ),
        true_false(
            "info-usb-ejetar",
            "Retirar o pendrive durante a cópia pode corromper o arquivo.",
            True,
            "A cópia precisa terminar. Ejetar com segurança avisa o sistema para concluir "
            "as gravações pendentes.",
        ),
    ],
)

add(
    "info-wifi",
    ["Conectar a uma rede Wi-Fi.", "Diferenciar rede aberta de rede protegida."],
    [
        multiple_choice(
            "info-wifi-cadeado",
            "Uma rede Wi-Fi com cadeado ao lado do nome:",
            [
                "Exige senha.",
                "É sempre grátis.",
                "É do governo.",
                "Não tem internet.",
            ],
            "Exige senha.",
            "O cadeado indica rede protegida com senha. Rede aberta não pede senha e é "
            "menos segura para dados sensíveis.",
        ),
        true_false(
            "info-wifi-aberta",
            "É seguro entrar no app do banco usando Wi-Fi aberto de uma praça.",
            False,
            "Rede aberta pode ser monitorada. Para banco, prefira os dados móveis do "
            "celular.",
        ),
    ],
)

add(
    "info-bateria",
    ["Cuidar da vida útil da bateria.", "Reconhecer hábitos que desgastam."],
    [
        multiple_choice(
            "info-bateria-faixa",
            "Qual faixa de carga ajuda a preservar baterias de lítio?",
            ["Entre 20% e 80%", "Sempre em 0%", "Sempre em 100%", "Só carregar à noite"],
            "Entre 20% e 80%",
            "Ficar entre 20% e 80% reduz o desgaste. Deixar chegar a 0% toda hora também "
            "encurta a vida útil.",
        ),
        true_false(
            "info-bateria-calor",
            "Calor é um dos maiores inimigos da bateria.",
            True,
            "Calor acelera a degradação. Evite carregar o celular no sol ou dentro do carro "
            "quente.",
        ),
    ],
)

add(
    "info-backup",
    ["Entender a regra da cópia em dois lugares.", "Definir o que salvar primeiro."],
    [
        multiple_choice(
            "info-backup-dois-lugares",
            "Qual backup protege melhor contra furto do celular?",
            [
                "Cópia na nuvem além da cópia no aparelho.",
                "Só a cópia no pendrive guardado na mesma mochila.",
                "Só a cópia no computador da mesma casa.",
                "Nenhuma: o celular não quebra.",
            ],
            "Cópia na nuvem além da cópia no aparelho.",
            "Cópia em dois lugares protege de falha, roubo e incêndio. Um único local é "
            "ponto único de falha.",
        ),
        true_false(
            "info-backup-fotos",
            "Fotos e documentos são as primeiras coisas a salvar no backup.",
            True,
            "São insubstituíveis. Aplicativos e músicas podem ser baixados de novo; fotos "
            "de família e documentos, não.",
        ),
    ],
)

add(
    "info-formatar",
    ["Aplicar negrito, itálico e alinhamento.", "Usar atalhos de formatação."],
    [
        matching(
            "info-formatar-atalhos",
            "Ligue o atalho ao efeito:",
            [
                ("Ctrl + B", "negrito"),
                ("Ctrl + I", "itálico"),
                ("Ctrl + U", "sublinhado"),
            ],
            "Memorizar três atalhos economiza dezenas de cliques por dia.",
        ),
        true_false(
            "info-formatar-excesso",
            "Usar negrito em um parágrafo inteiro destaca a informação principal.",
            False,
            "Se tudo está em destaque, nada está. Negrito funciona em palavras e frases "
            "curtas.",
        ),
    ],
)

add(
    "info-senhas-gestor",
    ["Entender o gerenciador de senhas.", "Criar uma senha mestra forte."],
    [
        multiple_choice(
            "info-senhas-gestor-mestra",
            "No gerenciador de senhas, você precisa memorizar:",
            [
                "Só a senha mestra.",
                "Todas as senhas de todos os sites.",
                "Nenhuma senha.",
                "Apenas os códigos de recuperação.",
            ],
            "Só a senha mestra.",
            "O gerenciador guarda as demais. A senha mestra deve ser longa e única — é a "
            "única que você precisa lembrar.",
        ),
        true_false(
            "info-senhas-gestor-papel",
            "Anotar senhas em papel na carteira é mais seguro que usar um gerenciador.",
            False,
            "Papel se perde, é fotografado e não tem backup. O gerenciador criptografa e "
            "sincroniza com segurança.",
        ),
    ],
)

add(
    "info-qrcode",
    ["Ler QR Code com a câmera.", "Conferir destino antes de confirmar."],
    [
        multiple_choice(
            "info-qrcode-confirmar",
            "Ao ler um QR Code de pagamento, o que conferir antes de confirmar?",
            [
                "Valor e nome de quem recebe.",
                "A cor do código.",
                "O tamanho da tela.",
                "O horário da leitura.",
            ],
            "Valor e nome de quem recebe.",
            "QR Code é um link. Antes de confirmar, veja destino, valor e beneficiário — "
            "adesivo falso em máquina de estacionamento é comum.",
        ),
        true_false(
            "info-qrcode-foto",
            "Um QR Code colado por cima de outro em uma placa pode levar a um site falso.",
            True,
            "Adesivos sobrepostos são um golpe conhecido. Confira se o QR Code parece "
            "original e veja o destino antes de pagar.",
        ),
    ],
)

add(
    "info-acessibilidade",
    ["Conhecer recursos de acessibilidade.", "Ativar zoom e leitor de tela."],
    [
        matching(
            "info-acessibilidade-recursos",
            "Ligue o recurso ao que ele resolve:",
            [
                ("leitor de tela", "fala o conteúdo para quem não vê"),
                ("alto contraste", "facilita leitura com baixa visão"),
                ("legendas", "traduz o áudio em texto"),
            ],
            "Recursos de acessibilidade beneficiam também quem está em ambiente barulhento "
            "ou com tela no sol.",
        ),
        true_false(
            "info-acessibilidade-so-alguns",
            "Recursos de acessibilidade servem apenas para pessoas com deficiência "
            "permanente.",
            False,
            "Zoom, legenda e contraste ajudam idosos, pessoas com tela quebrada e quem "
            "está em ambiente claro. Acessibilidade é para todos.",
        ),
    ],
)

add(
    "info-pdf",
    ["Abrir e preencher PDF.", "Reconhecer a assinatura digital oficial."],
    [
        multiple_choice(
            "info-pdf-assinatura",
            "A assinatura digital com validade legal no Brasil é emitida por:",
            [
                "gov.br ou autoridade certificadora credenciada.",
                "Qualquer editor de imagem.",
                "Um site que gera imagem de assinatura.",
                "Um aplicativo de mensagens.",
            ],
            "gov.br ou autoridade certificadora credenciada.",
            "Assinatura digital usa certificado. Foto de assinatura não tem validade "
            "jurídica como assinatura digital.",
        ),
        true_false(
            "info-pdf-formato",
            "Um PDF mantém a aparência do documento em qualquer aparelho.",
            True,
            "PDF foi criado para preservar a formatação — por isso é usado em contratos, "
            "formulários e documentos finais.",
        ),
    ],
)

add(
    "info-etiqueta",
    ["Aplicar boa convivência online.", "Escrever mensagens claras e respeitosas."],
    [
        multiple_choice(
            "info-etiqueta-maiusculas",
            "Escrever uma mensagem inteira em MAIÚSCULAS é interpretado como:",
            ["Grito", "Elegância", "Urgência oficial", "Formalidade"],
            "Grito",
            "Maiúsculas equivalem a falar alto. Em recados, prefira negrito para destacar "
            "uma palavra.",
        ),
        true_false(
            "info-etiqueta-audio",
            "Enviar áudios longos sem avisar se a pessoa pode ouvir é boa prática.",
            False,
            "Pergunte antes. Quem está no trabalho ou no transporte não consegue ouvir e "
            "fica sem a informação.",
        ),
    ],
)

add(
    "info-scratch",
    ["Montar sequência de instruções em blocos.", "Entender repetição e ordem."],
    [
        ordering(
            "info-scratch-ordem",
            "Ordene os blocos para o personagem andar:",
            [
                "Quando bandeira clicada",
                "Repita 10 vezes",
                "Mova 10 passos",
            ],
        ),
        true_false(
            "info-scratch-logica",
            "Programar em blocos usa a mesma lógica de programar escrevendo código.",
            True,
            "A diferença é a interface. Sequência, repetição e condição são as mesmas "
            "ideias em qualquer linguagem.",
        ),
    ],
)

add(
    "info-acessivel",
    ["Escrever texto alternativo em imagens.", "Escolher contraste adequado."],
    [
        multiple_choice(
            "info-acessivel-alt",
            "Qual texto alternativo descreve melhor um gráfico de vendas?",
            [
                "Gráfico de barras com as vendas de janeiro a junho",
                "imagem1.png",
                "gráfico",
                "foto",
            ],
            "Gráfico de barras com as vendas de janeiro a junho",
            "O texto alternativo diz o que a imagem informa. “imagem1.png” não informa nada "
            "para quem usa leitor de tela.",
        ),
        true_false(
            "info-acessivel-contraste",
            "Texto cinza claro sobre fundo branco é mais fácil de ler que texto escuro "
            "sobre fundo branco.",
            False,
            "Contraste baixo dificulta a leitura, sobretudo no sol e para baixa visão. "
            "Texto escuro sobre fundo claro tem mais contraste.",
        ),
    ],
)

add(
    "info-dados",
    ["Ler dados em tabela e gráfico.", "Tomar decisão a partir de dados."],
    [
        numeric_checked(
            "info-dados-maior",
            "Gastos do mês: mercado 420, transporte 180, energia 95. Qual é o maior gasto?",
            "420",
            "Mercado, com 420 — mais que o dobro do transporte. Ver os números juntos "
            "revela padrões que o extrato solto esconde.",
            tolerance=0,
        ),
        multiple_choice(
            "info-dados-grafico",
            "Um gráfico de linhas é mais adequado para mostrar:",
            [
                "Como algo muda ao longo do tempo",
                "Quantidades de categorias diferentes",
                "Um único valor",
                "Textos longos",
            ],
            "Como algo muda ao longo do tempo",
            "Linha mostra evolução; barras comparam categorias. Escolher o gráfico errado "
            "distorce a leitura.",
        ),
    ],
)

add(
    "info-codigo",
    ["Entender o que é algoritmo.", "Reconhecer ordem de passos."],
    [
    ordering(
            "info-codigo-algoritmo",
            "Ordene o algoritmo de fazer café:",
            [
                "Ferver a água",
                "Colocar o pó no filtro",
                "Despejar a água quente",
                "Esperar coar",
            ],
        ),
        true_false(
            "info-codigo-ordem",
            "Em um algoritmo, a ordem dos passos não altera o resultado.",
            False,
            "Ordem é essencial: despejar a água antes de pôr o pó produz outra coisa. "
            "Programa com passos fora de ordem não funciona.",
        ),
    ],
)

add(
    "info-privacidade",
    ["Decidir o que compartilhar.", "Reconhecer riscos de exposição de dados."],
    [
        multiple_choice(
            "info-privacidade-post",
            "Qual informação NÃO deve ser publicada em rede social?",
            [
                "Foto de documento com CPF",
                "Uma paisagem",
                "Uma receita de bolo",
                "Um livro que você leu",
            ],
            "Foto de documento com CPF",
            "Documento expõe você a fraude e não pode ser “despublicado” de fato: alguém "
            "já pode ter salvado.",
        ),
        true_false(
            "info-privacidade-viagem",
            "Anunciar nas redes que está viajando por duas semanas pode facilitar um "
            "roubo.",
            True,
            "Informar que a casa está vazia é convite. Publique fotos da viagem depois de "
            "voltar.",
        ),
    ],
)

add(
    "info-html",
    ["Reconhecer tags básicas de HTML.", "Distinguir estrutura de estilo."],
    [
        matching(
            "info-html-tags",
            "Ligue a tag ao que ela cria:",
            [
                ("<h1>", "título principal"),
                ("<p>", "parágrafo"),
                ("<img>", "imagem"),
                ("<a>", "link"),
            ],
            "HTML é estrutura: cada tag diz o que aquela parte é. A aparência fica com o "
            "CSS.",
        ),
        multiple_choice(
            "info-html-titulo",
            "Qual trecho cria o título principal da página?",
            ["<h1>Meu site</h1>", "<p>Meu site</p>", "<img src='foto.jpg'>", "Meu site"],
            "<h1>Meu site</h1>",
            "h1 é o título de maior nível. Usar h1 uma vez por página ajuda também leitores "
            "de tela.",
        ),
    ],
)

add(
    "info-ia",
    ["Usar assistentes de IA com revisão.", "Reconhecer limites e erros."],
    [
        multiple_choice(
            "info-ia-revisar",
            "Um assistente de IA respondeu uma dúvida jurídica. O que fazer antes de usar a "
            "informação?",
            [
                "Conferir em uma fonte oficial.",
                "Usar direto, porque IA não erra.",
                "Publicar como verdade.",
                "Pedir a mesma resposta de novo e confiar.",
            ],
            "Conferir em uma fonte oficial.",
            "IA pode inventar dados com aparência de verdade. Para saúde, direito e "
            "dinheiro, confirme em fonte oficial.",
        ),
        true_false(
            "info-ia-identidade",
            "Um assistente de IA é uma pessoa respondendo do outro lado.",
            False,
            "É um sistema estatístico de linguagem. Não tem emoções, memória pessoal nem "
            "responsabilidade — e a revisão continua sendo sua.",
        ),
    ],
)


def build() -> dict:
    return SPECS
