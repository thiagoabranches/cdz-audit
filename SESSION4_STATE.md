# 📘 ESTADO DA SESSÃO 4 — 2026-09-24

## Mapa

- Arquivo oficial: `C:\Users\thabr\OneDrive\Documentos\Warcraft III\Maps\sacredwar\X_Hero_Reborn_TESTE_TODOS_HEROIS.w3x`
- SHA256: `1b6835929fe9436548cf15f6499189ec39566233f312959bec19f58174513000`
- Tamanho: 4.440.771 bytes
- Wrapper: HM3W (512 bytes) + MPQ
- Tem -h (comando de troca de herói) ✅
- Tem Lotes 1-3 + parte do Lote 4 ✅

## Backups

- `C:\backup_mapa_cdz\X_Hero_Reborn_2026-09-24_1146.w3x` — pré-Lotes (b877fd49...)
- `C:\backup_mapa_cdz\old_em_sacredwar\X_Hero_Reborn_TESTE_TODOS_HEROIS_OLD.w3x` — pré-Lotes
- `C:\backup_mapa_cdz\old_em_sacredwar\X_Hero_Reborn_91f039f3.w3x` — Lotes 1-3 sem -h
- `C:\audit_temp\novo\X_Hero_Reborn_NOVO2.w3x` — cópia de trabalho atual

## Estado da auditoria

### cdz_audit.py (base + nome + texto)
- 774 checagens: **1 erro, 87 atenções**
- Único erro: AHbh (Shion) — anam "Lyra's Harmony", esperado "Energy Shield"

### audit_termos.py (Lote 4 — termos nativos)
- **191 erros** (termo de personagem)
- **73 atenções** (unidade invocada, objeto, frase)
- Distribuição por herói: ver ACHADO_LOTE4_2026-09-24.md

### Ferramentas funcionando
- `cdz_audit.py` — auditoria principal
- `audit_termos.py` — Lote 4 standalone
- `parser_w3a.py` — parser (Python puro + mpyq)
- `verificar_mapa.py` — SHA + tamanho
- `reference.json` — tabela Lote 1 (48 skills)
- `termos_nativos.json` — 47 termos Blizzard
- `codigo_heroi.json` — 141 mapeamentos código→herói

## Pendências abertas (por prioridade)

### 🔴 BLOCO A — Bases de skills erradas (21 confirmadas + 5 a confirmar)
Ver ACHADO_BASES_2026-09-24.md
  ANcl (14 skills) — invoca Lava Spawn em vez do efeito
  ANrc (2 skills) — invoca 2 infernais (Mu A010, Siegfried A00S)
  AUau (2 skills) — invoca carrion beetles
  AEsf/ANdr/AEim/Apoi (4 skills) — efeito oposto ao design

### 🔴 BLOCO A_original — pedido de 8 ao Claude (aguardando)
8 códigos com base nativa errada:
1. Mu A010 (ANrc → invoca 2 infernais)
2. Afrodite A09M (ANdr → não funciona)
3. Afrodite A09R (AEsf → Starfall)
4. Shun AUim (Crypt Lord)
5. Shun AUts (Crypt Lord)
6. Shun AUls (Crypt Lord)
7. Saga A083 (ANcl)
8. Siegfried A00S (ANrc)

### 🔴 BLOCO B — Lote 4 (191 casos contaminados)
Códigos com termo nativo em aub1/atp1. Lista completa em audit_termos.txt.
Distribuição por herói em ACHADO_LOTE4.

### 🔴 BLOCO C — Categoria de herói (upra) ERRADA
Ver ACHADO_CATEGORIA_2026-09-24.md
13 erros / 13 OK
Tipo 1 (herda base errada, nunca setou upra): 10
  Hpal→INT, Hmkg→INT, Edem→INT, Udre→INT, Obla→STR,
  Hjai→INT, Ucrl→INT, Nbst→INT, Hblm→STR, Emoo→INT
Tipo 2 (upra explícito errado): 3
  H009→AGI, Hvsh→INT, Nklj→STR

### 🔴 BLOCO D — Shion (ANALISADO via Gemini CLI)
- Skin: nunca aplicada — umdl é Archmage.mdl (código real é Hmkg, dossiê S2 errado)
- AHbh: contaminada com texto do Orpheu (Lyra's Harmony + Musical Notes)
- Base do AHbh: None (não tem nem base)
- Próximo: reimplementar com base ANms + texto CDZ

### 🟡 BLOCO E — reference.json
- Só cobre Lote 1 (48 skills)
- Falta Lote 2, C1 completo, C2

## Regras ativas

1. **Ferramenta > in-game** — só testar in-game quando a ferramenta não resolver
2. **Sem cru, não valida** — Claude não pode responder com "confirmei"
3. **Dado cru sempre** — table, não resumo
4. **Fatiar mensagens** — focar em 1 bloco por vez
5. **Backup antes de sobrescrever** — sempre

## Próximo passo

Quando Claude voltar (16:50):
1. Colar mensagem do BLOCO A (bases erradas — 8 códigos)
2. Depois BLOCO B (Lote 4 — 191 casos)
3. Depois BLOCO C (categoria herói)

## Atualizações pós-auditoria (sessão 4, contínuo)

### reference.json expandido
- Antes: 48 códigos (Lote 1)
- Depois: 144 códigos (48 originais + 96 do C1 do Claude)
- Os 96 novos têm personagem + campos null (a preencher com design)
- Backup: reference.json.bak

### cdz_audit.py patcheado
- Função comparar() atualizada
- Regra: pula checagens quando esperado=None
- Só valida campos com referência preenchida
- Backup: cdz_audit.py.bak3
- Resultado: 753 checagens / 1 erro / 87 atenções

### Ferramentas ativas
- cdz_audit.py (patched) — 1 erro
- audit_termos.py — 191 erros Lote 4
- audit_bases.py — 21+5 bases erradas
- audit_categoria.py — 13 categorias erradas
- decrypt_mpq.py — decripta w3u/w3h/w3q/w3t
- parser_w3u.py — lê w3u decriptado
- check_coerencia.py — cruza aub1 x base

## 🔴 DESCOBERTA FINAL — Mapas têm heróis DUPLICADOS

- Versões ANTIGAS (spawnam hoje): Hpal, Hmkg, Edem, H002, H009, N00W
- Versões NOVAS (corretas): N400-N416
- As skills A4XX (base correta) JÁ EXISTEM no mapa
- Bloco A = problema de WIRING, não de skill
- Correção: trocar H002→N40D, H009→N405, N00W→N408, etc.

Casos críticos:
  Seiya: H002 → N40D (A432/A433/A434)
  Aioria: H009 → N405 (A413-A416)
  Milo: N00W → N408 (A41E-A421)

Marin (H000) NÃO tem versão N4XX — pendência separada.
Kiki e Hakurei também não.

## Skins pendentes de importação (assets não estão no MPQ)

- AnasterianSunstrider (Shion / Hmkg)
  → extrair de: war3.w3mod\units\other\AnasterianSunstrider\
  → importar: .mdl + _portrait + BTNAnasterianSunstrider.blp
  → depois: setar umdl/uico/uPor/ussi no Hmkg
  → referência: mesma técnica da Aura Sagrada (Kiki)
