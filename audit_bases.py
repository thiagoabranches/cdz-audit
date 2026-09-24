# -*- coding: utf-8 -*-
"""
Auditor de BASES de skills.
Detecta:
  1. Skills autorreferentes (base == próprio código) — nunca trocou base
  2. Bases compartilhadas por 3+ skills — possível cópia sem trocar
  3. Bases que pertencem a heróis nativos claramente errados
"""
import sys, json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
import parser_w3a

# Campos que podem guardar a base
CAMPOS_BASE = ['base', 'old_id', 'oldid', 'orig', 'original', 'base_id', 'nativo']

# Bases nativas que sabemos que são de herói errado
BASES_SUSPEITAS = {
    'AHhb': 'Paladin - Holy Light',
    'AHad': 'Paladin - Devotion Aura',
    'AHds': 'Paladin - Divine Shield',
    'AHre': 'Paladin - Resurrection',
    'AHtb': 'Mountain King - Storm Bolt',
    'AHbh': 'Mountain King - Bash',
    'AUim': 'Crypt Lord - Impale',
    'AUts': 'Crypt Lord - Spiked Carapace',
    'AUls': 'Crypt Lord - Locust Swarm',
    'AUau': 'Crypt Lord - Carrion Beetles',
    'AEim': 'Demon Hunter - Immolation',
    'AEev': 'Demon Hunter - Evasion',
    'AEme': 'Demon Hunter - Metamorphosis',
    'AOwk': 'Blademaster - Wind Walk',
    'AOcr': 'Blademaster - Critical Strike',
    'AOmi': 'Blademaster - Mirror Image',
    'AOcl': 'Blademaster - Bladestorm',
    'ANrc': 'Rain of Chaos (Infernal)',
    'ANcl': 'Firelord - Summon Lava Spawn',
    'AEsf': 'Starfall',
    'ANdr': 'Drain (canalização)',
    'ACac': 'Death Knight - Unholy Aura',
    'AUav': 'Vampire - Vampiric Aura',
    'ANms': 'Anti-Magic Shell',
    'Ahea': 'Priest - Heal',
    'Apoi': 'Slow Poison',
    'AEsh': 'Shadow Strike',
    'AIda': 'Acid Bomb',
}


def achar_base(info):
    """Tenta achar a base em qualquer campo candidato."""
    for campo in CAMPOS_BASE:
        v = info.get(campo)
        if isinstance(v, str) and 3 <= len(v) <= 5:
            return v
        if isinstance(v, bytes):
            try:
                s = v.decode('ascii', errors='ignore').strip('\x00')
                if 3 <= len(s) <= 5:
                    return s
            except Exception:
                pass
    return None


def main():
    if len(sys.argv) < 2:
        print("Uso: python audit_bases.py <caminho.w3x>")
        sys.exit(1)
    caminho = sys.argv[1]

    print(f"Mapa: {caminho}")
    skills = parser_w3a.extrair_skills(caminho)
    print(f"Skills: {len(skills)}")
    print()

    # === DESCOBERTA ===
    print("=== DISCOVERY — campos disponíveis ===")
    amostra = next(iter(skills.values()))
    for k, v in amostra.items():
        tipo = type(v).__name__
        prev = str(v)[:80]
        print(f"  {k} ({tipo}): {prev}")
    print()

    com_base = sum(1 for s in skills.values() if achar_base(s))
    print(f"Skills com base detectada: {com_base}/{len(skills)}")
    print()

    if com_base == 0:
        print("!!! Parser NAO expoe campo de base.")
        print("Acao: modificar parser_w3a.py pra incluir 'old_id' no retorno.")
        return

    # === CARREGA MAPA HERÓI ===
    with open('codigo_heroi.json', encoding='utf-8') as f:
        mapa_heroi = json.load(f)

    # === ANÁLISE ===
    autorreferentes = []
    bases_count = defaultdict(list)
    suspeitas = []

    for cod, info in skills.items():
        base = achar_base(info)
        if not base:
            continue
        bases_count[base].append(cod)
        if base == cod:
            autorreferentes.append(cod)
        if base in BASES_SUSPEITAS and base != cod:
            suspeitas.append((cod, base))

    # === RELATÓRIO ===
    saida = Path(__file__).parent / 'saida'
    saida.mkdir(exist_ok=True)
    txt = saida / 'audit_bases.txt'

    with open(txt, 'w', encoding='utf-8') as f:
        f.write(f"=== AUTORREFERENTES (base == código) — {len(autorreferentes)} ===\n\n")
        for cod in autorreferentes:
            h = mapa_heroi.get(cod, '?')
            f.write(f"  {cod} ({h})\n")
        f.write(f"\n\n=== BASES USADAS POR 3+ SKILLS ===\n\n")
        for base, cods in sorted(bases_count.items(), key=lambda x: -len(x[1])):
            if len(cods) >= 3:
                f.write(f"  {base}: {len(cods)} skills\n")
                for c in cods:
                    h = mapa_heroi.get(c, '?')
                    f.write(f"    - {c} ({h})\n")
                f.write("\n")
        f.write(f"\n=== BASES SUSPEITAS (herói nativo errado) — {len(suspeitas)} ===\n\n")
        for cod, base in suspeitas:
            h = mapa_heroi.get(cod, '?')
            fam = BASES_SUSPEITAS[base]
            f.write(f"  {cod} ({h}) | base={base} ({fam})\n")

    # === RESUMO CONSOLE ===
    print(f"=== AUTORREFERENTES (base == codigo) — {len(autorreferentes)} ===")
    for cod in autorreferentes[:40]:
        h = mapa_heroi.get(cod, '?')
        print(f"  {cod} ({h})")
    if len(autorreferentes) > 40:
        print(f"  ... e mais {len(autorreferentes) - 40}")
    print()

    print(f"=== BASES SUSPEITAS (heroi nativo errado) — {len(suspeitas)} ===")
    for cod, base in suspeitas[:40]:
        h = mapa_heroi.get(cod, '?')
        fam = BASES_SUSPEITAS[base]
        print(f"  {cod} ({h}) | {base} = {fam}")
    if len(suspeitas) > 40:
        print(f"  ... e mais {len(suspeitas) - 40}")
    print()

    print(f"=== TOP BASES COMPARTILHADAS ===")
    for base, cods in sorted(bases_count.items(), key=lambda x: -len(x[1]))[:15]:
        print(f"  {base}: {len(cods)} skills")

    print()
    print(f"Relatorio: {txt}")


if __name__ == '__main__':
    main()
