# cdz_audit

Auditor local, só leitura, do mapa CDZ. Compara cada skill contra `reference.json` e gera um relatório HTML navegável.

## Uso

```
python cdz_audit.py caminho/do/mapa.w3x
```

Gera:
- `saida/audit_report.html` — relatório navegável, com filtro por personagem, filtro "só com erro/atenção", e botão para copiar o resultado filtrado como texto (pra colar direto no chat).
- `saida/audit_errors.txt` — lista de tudo que não é OK, já em formato de texto.

## O que é checado, por skill

| Campo | Severidade se estiver errado |
|---|---|
| `anam` | ERRO |
| `atp1` (todos os níveis até o maior nível com dado real) | ERRO se não contém o nome esperado, ATENÇÃO se vazio |
| `hotkey` (extraído de `atp1`) | ERRO se não bate com o esperado |
| `alev` vs nível real com dado | ATENÇÃO se não bate |
| `aub1` (todos os níveis) | ATENÇÃO se vazio |
| `arut`, `aret` | ATENÇÃO (heurística: primeira palavra do nome esperado não aparece no texto) |

## Arquivos

- `cdz_audit.py` — script principal (`comparar()`, `gerar_html()`, `gerar_txt()`)
- `parser_w3a.py` — extrai dados do `.w3a` de dentro do `.w3x`, busca estrita por código exato (mesmo método usado durante toda a auditoria manual — nunca aceita match ambíguo por base nativa compartilhada)
- `reference.json` — tabela de referência, 48 skills do Lote 1
- `templates/report.html` — template do relatório
- `stormtool` — binário usado pra extrair arquivos de dentro do `.w3x` (StormLib)

## Limitações conhecidas

- `reference.json` só cobre o Lote 1 (48 códigos). Precisa ser expandido com Lote 2 e Lote 3 pra cobrir o mapa inteiro.
- A checagem de `arut`/`aret` é uma heurística simples (procura a primeira palavra do nome esperado no texto) — pode dar falso "ATENÇÃO" em nomes compostos ou falso "OK" por coincidência. Serve como triagem, não veredito final.
- Não verifica `acdn`/`amcs` (cooldown/mana) contra valores esperados — o `reference.json` atual não inclui números de referência pra isso.
- É só leitura. Não corrige nada.
