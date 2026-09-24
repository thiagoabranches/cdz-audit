# 🎯 ACHADO — CATEGORIA DE HERÓI (upra) ERRADA

**Data:** 2026-09-24
**Ferramenta:** audit_categoria.py + war3map.w3u decriptado
**Total:** 13 errados / 13 OK / 0 não achados

## Tipo 1 — Herança errada (nunca setaram upra) — 10 heróis

| Herói | Código | Herda de | Atual | Esperado |
|---|---|---|---|---|
| Aries Mu | Hpal | Paladin | STR | INT |
| Aries Shion | Hmkg | Mountain King | STR | INT |
| Gemini Saga | Edem | Demon Hunter | AGI | INT |
| Cancer DeathMask | Udre | Dark Ranger | AGI | INT |
| Capricorn Shura | Obla | Blademaster | AGI | STR |
| Aquarius Kamus | Hjai | Archmage | ? | INT |
| Andromeda Shun | Ucrl | Crypt Lord | STR | INT |
| Lyra Orpheu | Nbst | Beastmaster | STR | INT |
| Dubhe Siegfried | Hblm | Blood Mage | INT | STR |
| Sierene Sorento | Emoo | Warden | AGI | INT |

## Tipo 2 — upra explícito errado — 3 heróis

| Herói | Código | Atual | Esperado |
|---|---|---|---|
| Leo Aioria | H009 | INT | AGI |
| Pisces Afrodite | Hvsh | AGI | INT |
| Phoenix Ikki | Nklj | INT | STR |

## Causa raiz

Herói clone herda `upra` do WC3 base se não for redefinido.
O Claude ou nunca setou (Tipo 1) ou setou errado (Tipo 2).

## Fix

Definir `upra` explicitamente nos 13:
  Hpal → INT
  Hmkg → INT
  Edem → INT
  Udre → INT
  Obla → STR
  Hjai → INT
  Ucrl → INT
  Nbst → INT
  Hblm → STR
  Emoo → INT
  H009 → AGI
  Hvsh → INT
  Nklj → STR

## OK (13)

Aldebaran, Shaka, Dohko, Milo, Aioros, Hyoga, Shiryu,
Seiya, Marin, Hakurei, Geki, Kiki, Shina.

## Ferramenta

- decrypt_mpq.py: decripta w3u/w3h/w3q/w3t do MPQ
- audit_categoria.py: lê w3u decriptado + analisa upra
