# open-data — proveniência dos dados abertos

Esta pasta é **material de referência**, não faz parte das lições. Nenhuma tela
do Aprende Brasil lê esses arquivos ainda; eles existem para consulta e para uma
futura trilha de leitura de dados.

## O que tem aqui

| Arquivo | O que é |
| --- | --- |
| `topics.json` | manifesto: temas, fontes consultadas, estado de cada chamada, data de geração |
| `data/<tema>.json` | registros crus por tema, com a fonte de cada item |
| `index.html` | página estática de consulta gerada a partir dos arquivos acima |

## Origem e data

- Gerado por `enrich_portals.py`, do projeto `edu-open-data`, e copiado para cá.
- Data de geração registrada em `topics.json`: **2026-09-15T14:35:52Z**
  (`generado_utc`). Os arquivos em `data/` são dessa mesma execução.
- Não há chave de API nem credencial envolvida: todas as fontes são públicas.

Para conferir a data de qualquer arquivo:

```bash
python3 -c "import json;print(json.load(open('client/public/open-data/topics.json'))['generado_utc'])"
```

## Fontes e licença — **estado da verificação**

Importante: **a licença de cada item ainda não foi conferida individualmente**
para uso comercial. O que está registrado em `topics.json` é a fonte e o
identificador da consulta; o que está abaixo é o que cada projeto declara de
forma geral, com o link para conferência.

| Fonte | O que foi usado | Licença declarada pela fonte | Conferido? |
| --- | --- | --- | --- |
| IBGE (servicodados) | lista de estados | dados abertos, uso livre com citação | não |
| Wikipedia PT | artigo “História do Brasil” | CC BY-SA | não |
| Wikisource PT | primeiras linhas de obras | domínio público / CC BY-SA conforme a obra | não |
| Project Gutenberg | metadados de *Dom Casmurro* | domínio público nos EUA; obra de Machado de Assis | não |
| GBIF | nomes de espécies | CC0/CC BY conforme o dataset de origem | não |
| OpenAlex | títulos de artigos | CC0 | não |
| Wiktionary (ES) | verbetes de “escola” | CC BY-SA | não |
| REST Countries | países | MPL 2.0 | não |

Enquanto a coluna “Conferido?” estiver em **não**, o uso é apenas interno e de
consulta. Antes de publicar qualquer material derivado:

1. abrir a página de licença da fonte (links em `topics.json`);
2. registrar aqui data da conferência, licença e obrigação de atribuição;
3. guardar a atribuição no próprio conteúdo publicado.

## Pendências conhecidas

- A página `index.html` e os campos dos JSON estão em **espanhol**, herdados do
  projeto gerador. Não é conteúdo do estudante; se esses dados forem usados em
  uma lição, precisam ser reescritos em português brasileiro antes.
- O item de “REST Countries” veio vazio na geração (`sin resultados`) e está
  registrado assim em `topics.json`; não é um dado faltando por erro nosso.
- A chamada ao Tatoeba falhou com HTTP 429 e está marcada `"ok": false`. Nenhum
  dado foi inventado para preencher a lacuna.

## Regra do projeto

Dado de terceiro entra com **origem, data e licença** registradas. Se não houver
licença clara, o dado não entra no conteúdo pedagógico. `tests/test_activities_contract.py`
verifica que este README continua existindo com esses campos.
