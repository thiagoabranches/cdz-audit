# 🎯 ACHADO CRÍTICO — LOTE 4 (aub1/atp1 contaminado por termos nativos)

**Data:** 2026-09-24
**Fonte:** `audit_termos.py` rodado sobre `X_Hero_Reborn_TESTE_TODOS_HEROIS.w3x`
**Ferramenta:** dicionário `termos_nativos.json` com 47 termos Blizzard
**Escopo:** varredura de `aub1` e `atp1` em 860 skills

## Números

- **191 ERROS** (termo de personagem) — todos reais
- **73 ATENÇÕES** (outras categorias: unidade invocada, objeto, frase)
- **253 skills contaminadas** de ~860 (30%)

## Distribuição por herói (ERROS)

| Herói | Erros | Termos principais |
|---|---|---|
| Hyoga | 22 | Lich King |
| Shina | 20 | Mev |
| Milo | 20 | Nevermore |
| Shiryu | 20 | Slardar |
| Mu | 18 | paladin |
| Seiya | 16 | marine |
| Shura | 15 | Blademaster |
| Afrodite | 14 | Vaisha/Vaishi |
| Saga | 10 | Demon Hunter |
| Aioros | 9 | Sylvanas |
| Aioria | 7 | Lightning Queen |
| Shun | 7 | Storm |
| Aldebaran | 5 | Tarsus |
| DeathMask | 4 | dreadlord, knight |
| Shion | 3 | Nome King |
| Siegfried | 1 | (resíduo) |
| **Total** | **191** | |


## Termos nativos mais frequentes

| Termo | Substituto CDZ | Herói |
|---|---|---|
| paladin | Mu | Mu |
| Nevermore | Milo | Milo |
| Mev | Shina | Shina |
| Slardar | Shiryu | Shiryu |
| marine | Seiya | Seiya |
| Vaisha / Vaishi | Afrodite | Afrodite |
| Blademaster | Shura | Shura |
| Demon Hunter | Saga | Saga |
| Lich King | Hyoga | Hyoga |
| Sylvanas | Aioros | Aioros |
| Tarsus | Aldebaran | Aldebaran |
| Lightning Queen | Aioria | Aioria |
| Nome King | Shion | Shion |
| dreadlord | DeathMask | DeathMask |

## Causa raiz

O Claude fez substituição por herói, mas **o mesmo termo nativo apareceu em múltiplos códigos** que ele não mapeou:

- `A00A` (Mu, paladin) — no C1
- `A06G` (Mu, paladin) — no C1
- `A097` (Mu, paladin) — no C1
- `A07V`, `A07W` (Milo, Nevermore) — **FORA DO C1**

Ou seja: o C1 listou 129 skills, mas as skills **legítimas dos heróis CDZ são mais de 150**. Toda skill fora do C1 ficou contaminada silenciosamente.

## Ferramenta

`audit_termos.py` — standalone, detecta termos nativos em aub1+atp1.
Dicionário: `termos_nativos.json` — 47 termos, com whitelist de códigos não-CDS.

## Próximo passo

Mandar pro Claude:
1. Lista completa de códigos contaminados
2. Para cada um: termo atual + substituto correto
3. Pedir: corrigir `aub1` E `atp1` em todos os 191 casos
