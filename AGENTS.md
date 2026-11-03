# AGENTS.md — belentani7/aprende-brasil

Instrucciones para agentes de código (Cursor, Claude Code, Codex, Gemini CLI).

## Stacks: python, node

## Ciclo de verificación

- `python -m unittest discover`
- `npm test`
- `npm run build`

## Reglas

- Evidence over claims: ejecuta la verificación antes de declarar éxito.
- Cambios mínimos y reversibles; un fix llega con su test.
- Nunca commitear secrets ni `.env`.

Ver estándares completos en `.cursor/rules/project.mdc`.
