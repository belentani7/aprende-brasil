# Contribuir com a Aprende Brasil

Obrigado pelo interesse. O projeto é educacional, em português brasileiro, e
prefere mudanças pequenas e verificáveis.

## Antes de abrir um PR

```bash
npm install
node scripts/run-python.mjs -m pip install -r requirements-dev.txt   # uma vez

npm run check      # TypeScript
npm test           # Vitest
npm run test:py    # pytest (use .venv se preferir)
npm run build      # build de produção
npm run audit      # contrato dos dados + orçamento de bundle
```

`npm run verify` encadeia tudo. Um PR só é aceito com a suíte verde e sem
aumentar o orçamento de bundle sem justificativa.

## Conteúdo pedagógico

- O texto é escrito para pessoas adultas que estão aprendendo a ler; evite
  infantilizar e evite paredes de texto.
- Cada módulo tem exatamente cinco etapas: `explanation`, `example`,
  `practice`, `check`, `next`.
- Não use placeholders ("Exemplo prático sobre…", "Ótimo! Continue
  praticando…"). A trilha de Alfabetização usa palavras comuns, curadas em
  `scripts/content_alfabetizacao.py`.
- Depois de mudar conteúdo: `node scripts/run-python.mjs -m scripts.build_curriculum`
  e `npm run curriculum`, e rode `npm run test:py`.

### Atividades e objetivos

- Todo módulo precisa de **objetivos** e de **pelo menos duas atividades** em
  `scripts/specs_<trilha>.py`. `check_coverage()` falha o build se faltar.
- Gabarito numérico **nunca** é digitado: use `numeric_checked(...)`, que avalia
  a expressão no build e quebra se a conta estiver errada.
- Múltipla escolha usa `multiple_choice(..., correct=resposta)`: o índice é
  calculado, então é impossível apontar para a opção errada.
- Atividades usam o vocabulário que a etapa já apresentou. Nada de palavra nova
  sem explicação na etapa.
- Escreva para pessoas adultas: exemplos de boleto, receita, crachá, bula e
  ônibus; sem infantilizar.
- Rode `node tools/aprende.mjs validate` — ele checa os seis tipos de atividade,
  ids repetidos, gabaritos inválidos e cobertura por módulo.

## Código

- TypeScript estrito; sem `any` desnecessário.
- Acessibilidade faz parte do critério de pronto: foco visível, rótulos,
  contraste e navegação por teclado.
- Performance tem orçamento medido (`tools/aprende.mjs budget`). Prefira
  carregar sob demanda a engordar o bundle inicial.
- Siga o estilo existente (Prettier: `npm run format`).

## Commits e PRs

Use commits convencionais (`feat:`, `fix:`, `docs:`, `test:`, `perf:`,
`chore:`). No PR, descreva o problema, a solução e como verificou. Inclua
capturas ou medições quando a mudança for visual ou de performance.
