# -*- coding: utf-8 -*-
"""
Compara skills entre X-Hero e CDZ DotA por NOME (anam).
Mostra quais skills têm o mesmo nome e como a base difere.
"""
import sys
from pathlib import Path
from wc3obj import parse_object_file
from parser_w3a import _extrair_w3a_bytes


def extrair_skills_dict(caminho_or_data, tag='w3a'):
    """Retorna dict: anam -> {codigo, base, mods}"""
    if isinstance(caminho_or_data, (str, Path)):
        data = _extrair_w3a_bytes(str(caminho_or_data))
    else:
        data = caminho_or_data
    parsed = parse_object_file(data, tag)

    indexado = {}
    for obj in parsed['original']:
        cod = (obj.get('old_id') or '').replace('\x00','')
        if cod:
            indexado[cod] = obj
    for obj in parsed['custom']:
        cod = (obj.get('new_id') or '').replace('\x00','')
        if cod:
            indexado[cod] = obj

    por_nome = {}
    for cod, obj in indexado.items():
        mods_global = {m['field']: m['value']
                       for m in obj['mods'] if m.get('level', 0) == 0}
        anam = mods_global.get('anam')
        if not anam or not isinstance(anam, str):
            continue
        anam = anam.strip()
        if not anam or anam == '?':
            continue
        # Só skills custom (que têm base)
        new_id = (obj.get('new_id') or '').replace('\x00','')
        base = (obj.get('old_id') or '').replace('\x00','') if new_id else None
        if anam not in por_nome:
            por_nome[anam] = []
        por_nome[anam].append({
            'codigo': cod,
            'base': base,
            'mods': {m['field']: m for m in obj['mods']},
        })
    return por_nome


def main():
    # X-Hero
    print("Lendo X-Hero...")
    xhero_path = 'C:/Users/thabr/OneDrive/Documentos/Warcraft III/Maps/sacredwar/X_Hero_Reborn_TESTE_TODOS_HEROIS.w3x'
    xhero = extrair_skills_dict(xhero_path)
    print(f"  X-Hero: {len(xhero)} nomes únicos")

    # CDZ DotA
    print("Lendo CDZ DotA...")
    with open('w3u_cdz/war3map.w3a', 'rb') as f:
        data_cdz = f.read()
    cdz = extrair_skills_dict(data_cdz)
    print(f"  CDZ: {len(cdz)} nomes únicos")
    print()

    # Intersecção
    comuns = sorted(set(xhero.keys()) & set(cdz.keys()))
    print(f"=== {len(comuns)} SKILLS COM MESMO NOME ===\n")

    # Compara base
    iguais = 0
    diferentes = 0
    so_xhero = 0
    so_cdz = 0
    achados = []

    for nome in comuns:
        for x in xhero[nome]:
            for c in cdz[nome]:
                if x['base'] == c['base']:
                    iguais += 1
                else:
                    diferentes += 1
                    achados.append({
                        'nome': nome,
                        'xhero_cod': x['codigo'],
                        'xhero_base': x['base'],
                        'cdz_cod': c['codigo'],
                        'cdz_base': c['base'],
                    })

    # Mostra divergências
    print(f"Base IGUAL: {iguais} | Base DIFERENTE: {diferentes}\n")
    print("=== SKILLS COM BASE DIFERENTE (X-Hero vs CDZ) ===\n")
    for a in achados[:40]:
        print(f"  {a['nome']}")
        print(f"    X-Hero: {a['xhero_cod']} base={a['xhero_base']}")
        print(f"    CDZ:    {a['cdz_cod']} base={a['cdz_base']}")
        print()

    # Skills só no CDZ (perdidas no X-Hero)
    so_cdz_nomes = sorted(set(cdz.keys()) - set(xhero.keys()))
    print(f"=== {len(so_cdz_nomes)} SKILLS QUE EXISTEM NO CDZ MAS NÃO NO X-HERO ===\n")
    for n in so_cdz_nomes[:30]:
        for c in cdz[n]:
            print(f"  {c['codigo']} | base={c['base']} | {n}")
    if len(so_cdz_nomes) > 30:
        print(f"  ... e mais {len(so_cdz_nomes) - 30}")


if __name__ == '__main__':
    import io
    from pathlib import Path

    # Redireciona stdout pra capturar o output
    out = io.StringIO()
    _orig_stdout = sys.stdout
    sys.stdout = out
    main()
    sys.stdout = _orig_stdout

    texto = out.getvalue()
    print(texto[:3000] + '\n\n[...cortado no console, salvo em arquivo]')

    saida = Path('saida')
    saida.mkdir(exist_ok=True)
    arq = saida / 'comparar_cdz.txt'
    arq.write_text(texto, encoding='utf-8')
    print(f"\nRelatorio completo salvo em: {arq}")
