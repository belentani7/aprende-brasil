import { MODULES, trackLabel } from "./curriculum";
import type { ModuleWithSteps, StepData, TutorReply } from "./types";

/**
 * Motor local do tutor Nilo.
 *
 * Sem LLM: classifica a intenção da mensagem, recupera os módulos do currículo
 * mais relevantes por sobreposição de termos e compõe uma resposta ampla e
 * pedagógica (conceito -> exemplo -> prática -> conferência -> próximo passo),
 * citando sempre conteúdo real dos 205 módulos.
 */

const STOPWORDS = new Set([
  "que", "qual", "quais", "como", "quando", "onde", "porque", "por", "para",
  "com", "sem", "dos", "das", "uma", "um", "umas", "uns", "este", "esta",
  "isso", "aquilo", "ele", "ela", "voce", "voces", "meu", "minha", "seu",
  "sua", "nos", "nas", "no", "na", "de", "da", "do", "os", "as", "ao", "aos",
  "em", "e", "ou", "mas", "se", "ja", "nao", "sim", "muito", "mais", "menos",
  "tem", "ter", "esta", "estao", "ser", "sou", "sao", "foi", "era", "quero",
  "queria", "gostaria", "preciso", "posso", "pode", "poderia", "favor",
  "ajuda", "ajudar", "explica", "explicar", "ensina", "ensinar", "mostra",
  "mostrar", "conta", "contar", "sobre", "tudo", "nada", "algo", "algum",
  "alguma", "coisa", "bem", "mal", "aqui", "ali", "me", "te", "lhe", "essa",
  "esse", "aquele", "aquela", "tambem", "ainda", "depois", "antes", "agora",
]);

type Intent =
  | "saudacao"
  | "explicar"
  | "exercicio"
  | "revisao"
  | "dificuldade"
  | "como"
  | "geral";

type Indexed = {
  module: ModuleWithSteps;
  title: string;
  subtitle: string;
  body: string;
  tokens: Set<string>;
};

function normalize(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function tokenize(text: string): string[] {
  return normalize(text)
    .split(" ")
    .filter((t) => t.length > 2 && !STOPWORDS.has(t));
}

let INDEX: Indexed[] | null = null;

function buildIndex(): Indexed[] {
  if (INDEX) return INDEX;
  INDEX = MODULES.map((module) => {
    const title = normalize(module.title);
    const subtitle = normalize(module.subtitle ?? "");
    const body = normalize(
      module.steps.map((s) => `${s.title} ${s.content?.text ?? ""}`).join(" "),
    );
    const tokens = new Set([
      ...tokenize(module.title),
      ...tokenize(module.subtitle ?? ""),
      ...tokenize(body),
    ]);
    return { module, title, subtitle, body, tokens };
  });
  return INDEX;
}

function search(message: string, subject: string, limit = 3): ModuleWithSteps[] {
  const terms = tokenize(message);
  if (!terms.length) return [];

  return buildIndex()
    .map((entry) => {
      let score = 0;
      for (const term of terms) {
        if (entry.title.includes(term)) score += 5;
        else if (entry.subtitle.includes(term)) score += 3;
        else if (entry.tokens.has(term)) score += 2;
        else if (entry.body.includes(term)) score += 1;
      }
      if (entry.module.track_id === subject) score += 1.5;
      return { module: entry.module, score };
    })
    .filter((r) => r.score >= 3)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((r) => r.module);
}

function detectIntent(message: string): Intent {
  const m = normalize(message);
  if (/^(oi|ola|opa|e ai|bom dia|boa tarde|boa noite)\b/.test(m) && m.length < 32)
    return "saudacao";
  if (/(exercicio|exercicios|praticar|pratica|teste|treinar|desafio)/.test(m))
    return "exercicio";
  if (/(resumo|revisao|revisar|resumir|recapitular|relembrar)/.test(m))
    return "revisao";
  if (/(nao entendi|nao entendi nada|dificil|confuso|complicado|nao consigo|travei|erra sempre)/.test(m))
    return "dificuldade";
  if (/(passo a passo|como faco|como fazer|como se|de que forma|como usar|como calcular)/.test(m))
    return "como";
  if (/(o que e|oque e|significa|para que serve|explica|explicar|por que|porque|diferenca)/.test(m))
    return "explicar";
  return "geral";
}

function stepOf(module: ModuleWithSteps, type: string): StepData | undefined {
  return module.steps.find((s) => s.type === type);
}

function textOf(module: ModuleWithSteps, type: string): string {
  return stepOf(module, type)?.content?.text?.trim() ?? "";
}

function firstSentence(text: string): string {
  const cut = text.split(/(?<=[.!?])\s/)[0];
  return (cut || text).trim();
}

function topicLabel(module: ModuleWithSteps): string {
  return module.title;
}

function relatedLine(hits: ModuleWithSteps[], skip: ModuleWithSteps): string {
  const others = hits.filter((m) => m.id !== skip.id);
  if (!others.length) return "";
  const names = others.map((m) => `“${m.title}”`).join(" e ");
  return `\n\nSe quiser ir além, procure também ${names} no catálogo.`;
}

function saudacao(subject: string): string {
  const label = trackLabel(subject);
  const inTrack = MODULES.filter((m) => m.track_id === subject);
  const sample = inTrack.slice(0, 3).map((m) => `“${m.title}”`).join(", ");
  return [
    `Oi! Que bom te ver por aqui. Sou o Nilo e acompanho você em ${label}.`,
    "",
    "Posso fazer três coisas com você:",
    "• explicar um conceito do zero, com exemplo e prática;",
    "• montar um exercício sob medida e conferir com você;",
    "• revisar um tema que você já viu, resumindo o essencial.",
    "",
    sample
      ? `Se não souber por onde começar, temos ${sample} — todos com cinco etapas curtas.`
      : "Me diga o que você quer aprender hoje e eu organizo o caminho.",
    "",
    "Sobre o que você quer falar?",
  ].join("\n");
}

function semResultado(message: string, subject: string): string {
  const label = trackLabel(subject);
  const inTrack = MODULES.filter((m) => m.track_id === subject).slice(0, 4);
  const list = inTrack.map((m) => `• ${m.title} — ${m.subtitle}`).join("\n");
  return [
    `Boa pergunta! Não achei um módulo exato sobre “${message.trim()}” em ${label}, mas dá para chegar lá por perto.`,
    "",
    `Em ${label} temos, por exemplo:`,
    list,
    "",
    "Duas saídas:",
    "1. me diga com outras palavras o que você quer entender — eu procuro de novo;",
    "2. escolha um desses módulos e faça a primeira etapa; em 3 minutos você já sai do lugar.",
    "",
    "Qual dos dois você prefere?",
  ].join("\n");
}

/** Sem módulo exato, mas com intenção clara: resposta genérica porém útil. */
function genericoPorIntencao(intent: Intent, subject: string): string {
  const label = trackLabel(subject);
  const inTrack = MODULES.filter((m) => m.track_id === subject).slice(0, 4);
  const list = inTrack.map((m) => `• ${m.title} — ${m.subtitle}`).join("\n");

  if (intent === "dificuldade") {
    return [
      "Calma, travar faz parte — e quase sempre significa que faltou um pedaço menor antes.",
      "",
      `Me conte o ponto exato de ${label} que emperrou, com suas palavras. Enquanto isso, uma saída que quase sempre funciona:`,
      "",
      "1. Volte um passo e procure o exemplo mais simples que existir.",
      "2. Resolva esse exemplo três vezes, bem devagar.",
      "3. Só depois avance para o próximo.",
      "",
      `Em ${label} temos estes para recomeçar:`,
      list,
      "",
      "Qual deles você quer abrir? Eu quebro em pedaços menores.",
    ].join("\n");
  }

  if (intent === "exercicio") {
    return [
      `Vamos treinar ${label} — mesmo sem saber ainda o tema exato, este roteiro funciona.`,
      "",
      "Exercício",
      "1. Escolha um dos módulos abaixo.",
      "2. Leia a etapa de exemplo e explique em voz alta, com suas palavras.",
      "3. Feche o módulo e repita de memória.",
      "4. Só então confira o que esqueceu.",
      "",
      "Módulos para escolher:",
      list,
      "",
      "Me diga qual escolheu e eu monto exercícios específicos sobre ele.",
    ].join("\n");
  }

  if (intent === "revisao") {
    return [
      `Revisão de ${label}: o jeito mais eficaz é reconstruir, não reler.`,
      "",
      "Faça assim, em 10 minutos:",
      "1. Escolha um módulo abaixo.",
      "2. Feche os olhos e tente repetir as cinco etapas em voz alta.",
      "3. Abra e veja o que faltou — o esquecimento mostra onde voltar.",
      "4. Refaça só a etapa que falhou.",
      "",
      "Módulos para revisar:",
      list,
      "",
      "Qual você quer revisar primeiro?",
    ].join("\n");
  }

  return "";
}

function explicar(main: ModuleWithSteps, hits: ModuleWithSteps[]): string {
  const conceito = textOf(main, "explanation");
  const exemplo = textOf(main, "example");
  const pratica = textOf(main, "practice");
  const proximo = textOf(main, "next");

  const parts = [
    `Vamos destrinchar ${topicLabel(main)} com calma — ${main.subtitle}`,
    "",
    "1) O conceito",
    conceito || firstSentence(main.subtitle),
    "",
    "2) Um exemplo concreto",
    exemplo || `Um caso do dia a dia que mostra ${topicLabel(main)} funcionando na prática.`,
    "",
    "3) Para praticar agora",
    pratica || "Releia o conceito e tente explicá-lo em voz alta com suas palavras.",
  ];

  if (proximo) {
    parts.push("", "4) Como saber que você entendeu", proximo);
  }

  parts.push(
    "",
    "Dica de estudo: não leia tudo de uma vez. Faça a prática, erre, e só depois volte ao conceito — é assim que fixa.",
    relatedLine(hits, main),
    "",
    "Quer que eu detalhe alguma dessas partes ou monte um exercício só seu?",
  );

  return parts.join("\n");
}

function como(main: ModuleWithSteps, hits: ModuleWithSteps[]): string {
  const pratica = textOf(main, "practice");
  const exemplo = textOf(main, "example");
  const check = textOf(main, "check");

  return [
    `Passo a passo de ${topicLabel(main)}.`,
    "",
    "Antes de começar, o essencial:",
    textOf(main, "explanation") || main.subtitle,
    "",
    "O caminho:",
    `1. Leia o exemplo e entenda o padrão — ${exemplo || "veja um caso resolvido."}`,
    `2. Faça junto, devagar — ${pratica || "repita o exemplo trocando os números."}`,
    `3. Confira você mesmo — ${check || "refaça sem olhar e compare com o exemplo."}`,
    "",
    "Se travar em algum passo, me diga qual — eu quebro ele em pedaços menores.",
    relatedLine(hits, main),
  ].join("\n");
}

function exercicio(main: ModuleWithSteps, hits: ModuleWithSteps[]): string {
  const pratica = textOf(main, "practice");
  const check = textOf(main, "check");
  const conceito = textOf(main, "explanation");

  return [
    `Boa! Vamos treinar ${topicLabel(main)} agora.`,
    "",
    "Lembrete rápido antes do exercício:",
    firstSentence(conceito) || main.subtitle,
    "",
    "Exercício",
    pratica || "Reescreva o conceito com um exemplo seu, do seu dia a dia.",
    "",
    "Como conferir",
    check || "Refaça sem consultar. Se acertar de novo, você aprendeu.",
    "",
    "Faça no papel primeiro — escrever devagar ajuda a memória. Quando terminar, me conte o que achou fácil e o que ficou difícil; eu ajusto o próximo exercício.",
    relatedLine(hits, main),
  ].join("\n");
}

function revisao(main: ModuleWithSteps, hits: ModuleWithSteps[]): string {
  const linhas = main.steps
    .map((s, i) => `${i + 1}. ${s.title} — ${firstSentence(s.content?.text ?? "")}`)
    .join("\n");

  return [
    `Revisão rápida de ${topicLabel(main)}.`,
    "",
    "As cinco etapas, em uma linha cada:",
    linhas,
    "",
    `Em resumo: ${firstSentence(textOf(main, "explanation")) || main.subtitle}`,
    "",
    "Para fixar de verdade, feche os olhos e tente repetir essas cinco etapas em voz alta. Depois abra o módulo e veja o que você esqueceu — o esquecimento mostra exatamente onde voltar.",
    relatedLine(hits, main),
  ].join("\n");
}

function dificuldade(main: ModuleWithSteps, hits: ModuleWithSteps[]): string {
  const conceito = textOf(main, "explanation");
  const exemplo = textOf(main, "example");

  return [
    "Calma, travar faz parte — e quase sempre significa que faltou um pedaço menor antes.",
    "",
    `Vamos reduzir ${topicLabel(main)} ao mínimo:`,
    "",
    "Só isto, por enquanto:",
    firstSentence(conceito) || main.subtitle,
    "",
    "Agora um único exemplo:",
    exemplo || "Pegue um caso bem pequeno e resolva devagar, sem pressa.",
    "",
    "Não tente entender tudo hoje. Faça só esse exemplo, três vezes. Na terceira, provavelmente já vai parecer óbvio.",
    "",
    "Me diga exatamente onde você para: na leitura, na conta, ou na hora de começar? Assim eu ataco o ponto certo.",
    relatedLine(hits, main),
  ].join("\n");
}

function geral(main: ModuleWithSteps, hits: ModuleWithSteps[]): string {
  const conceito = textOf(main, "explanation");
  const exemplo = textOf(main, "example");
  const pratica = textOf(main, "practice");

  return [
    `Entendi — você quer entender ${topicLabel(main)}. ${main.subtitle}`,
    "",
    "O conceito, sem rodeios:",
    conceito || firstSentence(main.subtitle),
    "",
    "Onde isso aparece na prática:",
    exemplo || "Um exemplo simples do dia a dia mostra o conceito funcionando.",
    "",
    "Seu próximo passo:",
    pratica || "Escolha um caso pequeno e aplique o conceito uma vez.",
    "",
    "Estudar em pedaços curtos rende mais do que ler tudo de uma vez. Faça essa prática agora e volte depois — eu continuo daqui.",
    relatedLine(hits, main),
  ].join("\n");
}

export function answerTutor(message: string, subject: string): TutorReply {
  const intent = detectIntent(message);

  if (intent === "saudacao") {
    return { source: "local", answer: saudacao(subject) };
  }

  const hits = search(message, subject, 3);
  if (!hits.length) {
    const generico = genericoPorIntencao(intent, subject);
    return {
      source: "local",
      answer: generico || semResultado(message, subject),
    };
  }

  const [main] = hits;
  const body =
    intent === "exercicio"
      ? exercicio(main, hits)
      : intent === "revisao"
        ? revisao(main, hits)
        : intent === "dificuldade"
          ? dificuldade(main, hits)
          : intent === "como"
            ? como(main, hits)
            : explicar(main, hits);

  return { source: "local", answer: body };
}

export const TUTOR_SUGGESTIONS = [
  "Explique este tema de um jeito simples",
  "Crie um exercício rápido",
  "Quero revisar o que já vi",
];
