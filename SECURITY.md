# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities via email to belentani7pedro@gmail.com.

## Code Scanning

This project uses GitHub CodeQL for automated security scanning. All security issues detected by CodeQL will be addressed with priority.

## Dependabot

Dependabot alerts security vulnerabilities in dependencies. Dependabot security updates will be accepted via Pull Request.

## Secret Protection

GitHub Secret Protection scans for hardcoded secrets. Do not commit API keys, tokens, or passwords to this repository.

## Advanced Security

Enable GitHub Advanced Security for:

- Dependabot alerts
- CodeQL analysis
- Secret scanning
- Push protection

## Modelo de privacidade

O campus é **local por padrão**: progresso, favoritos e histórico ficam no
`localStorage` do aparelho. O backend só entra em cena quando alguém escolhe
sincronizar.

### Identidade

- `POST /api/session` cria uma **sessão anônima**. Nenhum nome, e-mail, telefone
  ou documento é solicitado, coletado ou registrado.
- O servidor guarda apenas o **hash SHA-256** do token da sessão. Um vazamento
  do SQLite não permite reconstruir tokens nem se passar por alguém.
- A identidade de progresso, favoritos, estatísticas, exportação e importação
  vem **exclusivamente** de `Depends(get_session)`. Os schemas usam
  `extra="forbid"`: enviar `user_id` no corpo devolve 422; `?user_id=` na query
  é ignorado.
- `tests/test_privacy.py` cobre acesso cruzado, token inválido, ausência de
  sessão e tentativa de ler o progresso de outra pessoa.

### Dados de menores

O produto não pede idade, nome nem e-mail, o que reduz a superfície de dados de
crianças e adolescentes. Se no futuro houver conta com dados pessoais, será
necessário consentimento de responsável e revisão de LGPD antes de habilitar.

### Tutor LLM

- Desligado por padrão: exige `LLM_ENABLED=1` **e** credenciais no backend.
- Limites: timeout de 12 s, 2 requisições simultâneas, teto diário de
  caracteres, limite por IP e contexto truncado ao módulo consultado.
- Nenhum identificador de estudante, token ou dado pessoal é enviado no payload
  (`tests/test_tutor_limits.py` verifica exatamente isso).
- Falha do provedor cai no motor local; a interface marca a origem da resposta.

### Service worker

`client/public/sw.js` ignora `/api/` e qualquer requisição com cabeçalho
`Authorization`. Nada de progresso sincronizado fica em cache do navegador.

## Checklist antes de expor o backend publicamente

1. `APRENDE_CORS_ORIGINS` com a lista explícita dos domínios (nunca `*`).
2. HTTPS obrigatório (o token de sessão viaja no cabeçalho `Authorization`).
3. `LLM_ENABLED` só com autorização de quem paga a conta do provedor.
4. Rodar `pytest tests/test_privacy.py tests/test_tutor_limits.py`.
5. Se houver múltiplas instâncias, trocar o limitador em processo por um
   distribuído (Redis) — o atual protege uma instância só.
