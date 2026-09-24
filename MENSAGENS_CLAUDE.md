# Mensagens para Claude — Ordem: C → D → A → B

## ═══ BLOCO C (manda primeiro) ═══

BLOCO C — CATEGORIA DE HERÓI (upra)

13 heróis com atributo primário (upra) errado
(10 herança incorreta, 3 explícitos errados).

LISTA:
 1. Aries Mu (Hpal) - Atual: STR → Esperado: INT (Herança)
 2. Aries Shion (Hmkg) - Atual: STR → Esperado: INT (Herança)
 3. Gemini Saga (Edem) - Atual: AGI → Esperado: INT (Herança)
 4. Cancer DeathMask (Udre) - Atual: AGI → Esperado: INT (Herança)
 5. Capricorn Shura (Obla) - Atual: AGI → Esperado: STR (Herança)
 6. Aquarius Kamus (Hjai) - Atual: ? → Esperado: INT (Herança)
 7. Andromeda Shun (Ucrl) - Atual: STR → Esperado: INT (Herança)
 8. Lyra Orpheu (Nbst) - Atual: STR → Esperado: INT (Herança)
 9. Dubhe Siegfried (Hblm) - Atual: INT → Esperado: STR (Herança)
10. Sierene Sorento (Emoo) - Atual: AGI → Esperado: INT (Herança)
11. Leo Aioria (H009) - Atual: INT → Esperado: AGI (Explícito)
12. Pisces Afrodite (Hvsh) - Atual: AGI → Esperado: INT (Explícito)
13. Phoenix Ikki (Nklj) - Atual: INT → Esperado: STR (Explícito)

PEDIDO:
1. Definir explicitamente upra (0=STR, 1=INT, 2=AGI) no
   war3map.w3u para os 13 heróis.
2. Executar audit_categoria.py para validar 0 erros.

REGRA: sem cru, não valido. Obrigatório rodar o validador.


## ═══ BLOCO D (manda segundo) ═══

BLOCO D — SHION (SKIN + ENERGY SHIELD)

2 pendências críticas do Shion.
Nota: dossiê S2 dizia que o código era Hssa.
Análise via Gemini CLI mostrou que é Hmkg.

LISTA:
1. SKIN — nunca aplicada
   Código: Hmkg (Mountain King)
   umdl atual: units\human\Archmage\Archmage.mdl
   umdl esperado: units\other\AnasterianSunstrider\AnasterianSunstrider
   Campos a copiar/aplicar (do Hpal original):
     uico: ReplaceableTextures\CommandButtons\BTNAnasterianSunstrider.blp
     uPor: units\other\AnasterianSunstrider\AnasterianSunstrider_portrait
     ussi: UI\Glues\ScoreScreen\scorescreen-hero-paladin.blp

2. AHbh (Energy Shield) — contaminada
   anam atual: "Lyra's Harmony"
   aub1 atual: "Every spell Orpheu casts resonates a Musical Note..."
   base atual: None
   alev atual: (nenhum dado)

PEDIDO:
1. Aplicar os campos de skin no Hmkg (copiar do Hpal).
2. Reimplementar AHbh:
   - anam = "Energy Shield"
   - alev = 8 níveis
   - atp1 preenchido nos 8 níveis
   - base ANms (Anti-Magic Shell) — absorve dano via mana
   - aub1 em lore CDZ

REGRA: sem cru, não valido. Rodar cdz_audit.py e
confirmar que AHbh sai do erro. Confirmar skin via
parser_w3u.


## ═══ BLOCO A (manda terceiro) ═══

BLOCO A — BASES DE SKILLS ERRADAS

25 skills com base nativa incorreta no war3map.w3a,
confirmadas por análise cruzada (aub1 promete X, base faz Y).

LISTA (agrupada por base errada):

1. ANcl (Firelord - Summon Lava Spawn) — 14 skills:
   Shura: A0BT, A0CU, A0CV, A0CW, A0CX, A0G4
   Milo: A07W, A08Z
   Hyoga: A0FF, A0FK
   Shun: A0BV
   Aldebaran: A07M
   Siegfried: A00Q
   Saga: A083

2. ANrc (Rain of Chaos - invoca infernais) — 2 skills:
   Mu: A010
   Siegfried: A00S

3. AUau (Crypt Lord - Carrion Beetles) — 2 skills:
   Afrodite: A09P
   DeathMask: A016

4. Efeito oposto — 4 skills:
   Afrodite: A09M (Drain), A09R (Starfall)
   Shion: A017 (Immolation)
   Shun: A020 (Slow Poison)

5. Unholy Aura (ACac) — efeito errado — 2 skills:
   Milo: A087
   Shura: A067

6. Shun Crypt Lord nativo — 3 skills:
   AUim (Impale), AUts (Spiked Carapace), AUls (Locust Swarm)

PEDIDO:
1. Substituir a base nativa de cada uma pela base correta.
2. Implementar trigger próprio onde o design exigir.
3. Garantir que efeito in-game bata com o aub1.

REGRA: sem cru, não valido. audit_bases.py confirmando
saída da lista.


## ═══ BLOCO B (manda último) ═══

BLOCO B — LOTE 4 (TERMOS NATIVOS EM aub1/atp1)

191 erros de termos nativos da Blizzard em aub1/atp1
(contaminação cruzada fora do C1).

LISTA (resumo por herói):
  - Hyoga: 22 casos (Lich King)
  - Shina: 20 casos (Mev)
  - Milo: 20 casos (Nevermore)
  - Shiryu: 20 casos (Slardar)
  - Mu: 18 casos (paladin)
  - Seiya: 16 casos (marine)
  - Shura: 15 casos (Blademaster)
  - Afrodite: 14 casos (Vaisha/Vaishi)
  - Saga: 10 casos (Demon Hunter)
  - Aioros: 9 casos (Sylvanas)
  - Aioria: 7 casos (Lightning Queen)
  - Shun: 7 casos (Storm)
  - Aldebaran: 5 casos (Tarsus)
  - DeathMask: 4 casos (dreadlord, knight)
  - Shion: 3 casos (Nome King)
  - Siegfried: 1 caso
(ver ACHADO_LOTE4_2026-09-24.md para lista completa)

PEDIDO:
1. Remover termos nativos de Blizzard dos 191 aub1/atp1.
2. Substituir por texto/nome CDZ correto.

REGRA: sem cru, não valido. Rodar audit_termos.py até
zerar os 191 erros.
