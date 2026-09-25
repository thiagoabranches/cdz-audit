# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from wc3obj import parse_object_file

def analisar(pasta, nome):
    print(f"\n{'═'*60}")
    print(f"📁 {nome} ({pasta}/)")
    print('═'*60)
    
    try:
        with open(f'{pasta}/war3map.w3u', 'rb') as f:
            w3u = parse_object_file(f.read(), 'w3u')
    except Exception as e:
        print(f"ERRO: {e}")
        return
    
    todos = w3u['original'] + w3u['custom']
    print(f"Total unidades: {len(todos)}")
    
    achados = []
    for obj in todos:
        mods = {m['field']: m['value'] for m in obj['mods'] if m.get('level',0) == 0}
        texto = ' '.join(str(v) for v in mods.values() if isinstance(v, str))
        if 'anasterian' in texto.lower() or 'sunstrider' in texto.lower():
            cod = (obj.get('new_id') or '').replace('\x00','') or (obj.get('old_id') or '').replace('\x00','')
            achados.append({
                'codigo': cod,
                'unam': mods.get('unam'),
                'umdl': mods.get('umdl'),
                'uico': mods.get('uico'),
                'uPor': mods.get('uPor'),
                'ussi': mods.get('ussi'),
                'uhab': mods.get('uhab'),
                'uabi': mods.get('uabi'),
            })
    
    if achados:
        print(f"\n🎯 ENCONTRADO em {len(achados)} unidades!")
        for a in achados:
            print(f"\n  Código:   {a['codigo']}")
            print(f"  Nome:     {a['unam']}")
            print(f"  Modelo:   {a['umdl']}")
            print(f"  Ícone:    {a['uico']}")
            print(f"  Portrait: {a['uPor']}")
            print(f"  ScoreScr: {a['ussi']}")
            print(f"  uhab:     {a['uhab']}")
            print(f"  uabi:     {a['uabi']}")
    else:
        print("\n❌ Não encontrado em uhab/uabi/unam")
    
    print(f"\n--- Modelos custom (war3mapImported) ---")
    modelos_custom = set()
    for obj in todos:
        mods = {m['field']: m['value'] for m in obj['mods'] if m.get('level',0) == 0}
        m = str(mods.get('umdl', '') or '')
        if 'war3map' in m.lower() or 'imported' in m.lower():
            modelos_custom.add(m)
    
    for m in sorted(modelos_custom):
        print(f"  {m}")

print("="*60)
print("PROCURA ANASTERIAN SUNSTRIDER")
print("="*60)

analisar('w3u_fol', 'FoL 0.23')
analisar('w3u_lta', 'Lordaeron The Aftermath 1.15a')

print("\n" + "="*60)
print("FIM")
print("="*60)
