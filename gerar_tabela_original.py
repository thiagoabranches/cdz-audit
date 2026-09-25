# -*- coding: utf-8 -*-
"""Gera tabela markdown do X-Hero original."""
import json
from pathlib import Path

with open('saida/herois_original.json', encoding='utf-8') as f:
    herois = json.load(f)

saida = Path('saida')
saida.mkdir(exist_ok=True)

with open(saida / 'tabela_original.md', 'w', encoding='utf-8') as f:
    f.write(f"# TABELA — X-HERO ORIGINAL (sem CDZ)\n\n")
    f.write(f"**Heróis:** {len(herois)}  \n")
    f.write(f"**Skills totais:** {sum(len(h.get('skills', [])) for h in herois)}\n\n")
    f.write("---\n\n")

    for h in herois:
        cod = h.get('codigo', '?')
        nome = h.get('nome', '?')
        attr = h.get('atributo', '?')
        hp = h.get('hp_nv1', '?')
        s_b = h.get('str_base', '?')
        s_g = h.get('str_gain', '?')
        a_b = h.get('agi_base', '?')
        a_g = h.get('agi_gain', '?')
        i_b = h.get('int_base', '?')
        i_g = h.get('int_gain', '?')

        f.write(f"## {nome} ({cod}) — {attr}\n")
        f.write(f"**Stats:** STR {s_b} (+{s_g}) / AGI {a_b} (+{a_g}) / INT {i_b} (+{i_g}) / HP {hp}\n\n")

        skills = h.get('skills', [])
        if not skills:
            f.write("_(sem skills)_\n\n")
            continue

        f.write("| Slot | Código | Nome | Base | Nv | Mana | CD |\n")
        f.write("|---|---|---|---|---|---|---|\n")

        for i, s in enumerate(skills):
            slot = ['Q', 'W', 'E', 'R', 'T', 'X'][i] if i < 6 else '?'
            if s.get('erro'):
                f.write(f"| {slot} | {s.get('codigo','?')} | *NAO ENCONTRADA* | — | — | — | — |\n")
                continue

            sc = s.get('codigo', '?')
            sn = s.get('nome', '?')
            base = s.get('base', '?')
            nv = s.get('niveis', 0)
            mana = s.get('mana', {})
            cd = s.get('cooldown', {})

            def fmt(d):
                if not d: return '—'
                v1 = d.get('1', d.get('0', '?'))
                v8 = d.get('8', d.get('4', d.get('0', '?')))
                if v1 == v8: return str(v1)
                return f"{v1}→{v8}"

            f.write(f"| {slot} | {sc} | {sn} | {base} | {nv} | {fmt(mana)} | {fmt(cd)} |\n")

        f.write("\n---\n\n")

print(f"Tabela gerada: saida/tabela_original.md")
print(f"Heróis: {len(herois)}")
print(f"Skills totais: {sum(len(h.get('skills', [])) for h in herois)}")
