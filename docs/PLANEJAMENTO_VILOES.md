# Planejamento — Vilões CDZ (Futuro)

Inspiração: filme "Saint Seiya: The Heaven Chapter — Overture" (2004)
Tema: Anjos, Lucifer, Cavaleiros do Apocalipse

---

## Assets já identificados (mapas custom)

### Anjos — disponíveis

| Asset | Mapa | ID do herói | Uso ideal |
|---|---|---|---|
| `war3mapImported\Archangel_IncarnationofRedemption.mdl` | Eve | (ver skins_eve.json) | **Lucifer** |
| `war3mapImported\Seraphim.mdl` | Eve | (ver skins_eve.json) | Anjo de alto escalão |
| `war3mapImported/Angel.mdl` | Angel Arena | UC18, H00V, H00R | Anjo genérico |

### Espadachins / Guerreiros

| Asset | Mapa | Uso |
|---|---|---|
| `war3mapImported\HeroSaber.mdl` | Angel Arena | Shion / guerreiro |
| `war3mapImported\HeroStormthrasher.mdl` | Angel Arena | Aioria / trovão |

### Casters

| Asset | Mapa | Uso |
|---|---|---|
| `war3mapImported\FemaleMage.mdl` | Angel Arena | Feiticeira genérica |
| `war3mapImported\BloodElfPriestess.mdl` | Angel Arena | Sacerdotisa |

---

## Cavaleiros do Apocalipse — FALTA TUDO

| Cavaleiro | Descrição bíblica/filme | Asset necessário | Status |
|---|---|---|---|
| **Conquista/Guerra** | Cavalo vermelho, espada, coroa | Guerreiro de armadura pesada | ❌ Não temos |
| **Fome** | Balança, cavalo negro | Mago espectral | ❌ Não temos |
| **Peste** | Arco, cavalo branco | Arqueiro angelical | ❌ Não temos |
| **Morte** | Foice, manto pálido | Ceifador/Death | 🟡 Parcial (Abomination TOB) |

---

## Tarefas futuras

1. **Extrair os assets identificados** dos MPQs (Eve + Angel Arena)
   - Precisa: `war3mapImported\` directory decryption
   - Ferramenta: `decrypt_mpq.py` (funciona se souber nome exato)

2. **Buscar mais assets** em outros mapas:
   - Mapas com anjos/anjos caídos
   - Mapas bíblicos/religiosos (raro)
   - Modelos de Lucifer específicos

3. **Verificar CASC Reforged** — pode ter assets de anjo não usados

4. **Buscar assets externos** (Hive Workshop, XGM.guru):
   - Modelos "Lucifer" custom WC3
   - Cavaleiros do Apocalipse custom
   - Anjos caídos

5. **Decidir prioridade:** vilões antes ou depois de fechar os 24 dourados?

---

## Referência visual (filme)

- **Lucifer:** anjo caído com asas negras, armadura completa escura
- **Serafim:** anjo de 6 asas, dourado
- **Cavaleiros do Apocalipse:** 4 cavaleiros sobre cavalos (cores específicas)
- **Anjos caídos:** asas partidas, auréolas rachadas

---

## Arquivos relacionados
- `docs/referencias_externas/skins_eve.json` — modelos custom da Eve
- `docs/referencias_externas/skins_angel.json` — modelos custom do Angel Arena
- `docs/referencias_externas/skins_tob.json` — modelos custom do TOB
