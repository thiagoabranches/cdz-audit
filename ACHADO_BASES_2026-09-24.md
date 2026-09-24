# 🎯 ACHADO CRÍTICO — BASES DE SKILLS ERRADAS

**Data:** 2026-09-24
**Ferramenta:** audit_bases.py + check_coerencia.py
**Regra:** veredito in-game > heurística

## Total: 21 confirmados + 5 a confirmar

## 🔴 Categoria 1 — Base invoca unidade (17)

Base ANcl (Firelord - Summon Lava Spawn) = 14 skills:
  Shura: A0BT, A0CU, A0CV, A0CW, A0CX, A0G4
  Milo: A07W, A08Z
  Hyoga: A0FF, A0FK
  Shun: A0BV
  Aldebaran: A07M
  Siegfried: A00Q
  Saga: A083 (a confirmar)

Base ANrc (Rain of Chaos - invoca 2 infernais) = 2 skills:
  Mu: A010 (confirmado in-game)
  Siegfried: A00S

Base AUau (Crypt Lord - Carrion Beetles) = 2 skills:
  Afrodite: A09P
  DeathMask: A016 (a confirmar)

## 🔴 Categoria 2 — Efeito oposto (4, todos confirmados in-game)

  Mu A010 | ANrc — invoca 2 infernais
  Afrodite A09M | ANdr — não funciona (Drain + autocast)
  Afrodite A09R | AEsf — Starfall em vez de detonar rosas
  Afrodite A09P | AUau — a confirmar (mas aub1 fala de buff)

## 🔴 Categoria 3 — Crypt Lord nativo (3)

  Shun AUim (Impale), AUts (Spiked Carapace), AUls (Locust Swarm)
  Design S2: trocar por AHtb, ACcl, Aens, Aent

## 🟡 A confirmar (5)

  A017 (Shion) | AEim — design: Hecatombe
  A020 (Shun) | Apoi — design: Onda Relâmpago
  A087 (Milo) | ACac — design: Terrifying Presence
  A047 (Seiya) | AIda — design: Cosmo Break
  A067 (Shura) | ACac

## Causa raiz

Claude trocou anam/atp1/aub1 mas manteve base nativa errada.
Base usada para clonar não corresponde ao design aprovado.

## Ferramentas usadas

- audit_bases.py — detecta bases suspeitas (comparação com lista)
- check_coerencia.py — cruza aub1 com família da base
- codigo_heroi.json — mapa 141 códigos CDZ
- BASES_SUSPEITAS — dicionário de bases nativas problemáticas

## Próximo passo

Mandar pro Claude:
1. Lista dos 21 confirmados
2. Lista dos 5 a confirmar
3. Pedir: base atual + efeito puro + tem_trigger (sim/não)
4. Corrigir base errada ou implementar trigger
