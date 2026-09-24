# -*- coding: utf-8 -*-
"""
Cruza aub1 (texto que o Claude escreveu) com base nativa da skill.
Objetivo: identificar skills onde o TEXTO promete algo que a BASE
nao entrega — sinal de que nunca houve troca de base nem trigger.
"""
import sys, json, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import parser_w3a

# Familia de cada base (o que ela faz puro)
FAMILIA_BASE = {
    # INVOCA UNIDADE
    'ANcl': 'invoca',  'ANrc': 'invoca',  'AUau': 'invoca',
    'AUin': 'invoca',  'ANlm': 'invoca',  'AUls': 'invoca',
    'ANsg': 'invoca',  'ANfa': 'invoca',  'AOsh': 'invoca',
    'Auhf': 'invoca',  'AUan': 'invoca',  'ANst': 'invoca',
    'AHwe': 'invoca',  'A008': 'invoca',  'AHpx': 'invoca',
    'ANto': 'invoca',  'A0A1': 'invoca',  'A06O': 'invoca',

    # DANO DIRETO
    'AHtb': 'dano_stun', 'AHbh': 'crit',    'AHhb': 'dano',
    'AHfs': 'dano_area', 'ANfl': 'dano',    'AOcl': 'dano_area',
    'AEfk': 'dano_area', 'ANht': 'buff_area','ACcl': 'dano',
    'AEsf': 'dano_area', 'ANdr': 'drain',   'ACtb': 'dano',
    'AIda': 'dano_area','ANfd': 'dano',     'Aehf': 'dano',
    'AOae': 'buff',     'AHbn': 'dano',

    # BUFF/AURA
    'ACac': 'aura',    'AUav': 'aura',     'AEim': 'buff_fogo',
    'AEev': 'evasao',  'AEme': 'metamorf', 'AOwk': 'invis',
    'AOcr': 'crit',    'AOmi': 'ilusao',   'ANms': 'escudo',
    'Apoi': 'poison',  'AEsh': 'poison',   'Ahea': 'heal',
    'Afod': 'nuke',    'ANrc': 'invoca',   'ANcl': 'invoca',
    'AUts': 'defesa',  'Arsw': 'invoca',   'Asth': 'area',

    # INVOCAÇÃO ESPECÍFICA
    'AUim': 'dano',    'A05Z': 'crit',     'A07W': 'aura',
    'A07V': 'dano_area','A082': 'dano',    'A092': 'dano_area',
}

# Palavras-chave no aub1 que indicam o que o design promete
PALAVRAS_DESIGN = {
    'invoca': ['summon', 'invoke', 'call', 'spawn', 'creatures',
               'beetle', 'golem', 'infernal', 'spirit', 'elemental',
               'corpse', 'skeleton'],
    'dano_direto': ['deal', 'damage', 'strike', 'strikes', 'blast',
                    'explosion', 'burn', 'fiery', 'ice', 'lightning',
                    'burns', 'pierce'],
    'dano_area': ['nearby', 'area', 'all enemies', 'surrounding',
                  'fan of', 'wave', 'storm', 'rain of', 'blast'],
    'buff': ['gains', 'increases', 'bonus', 'enhances', 'aura',
             'regeneration', 'absorption', 'protection', 'shield'],
    'stun_slow': ['stun', 'slow', 'miss', 'disable', 'immobilize',
                  'silence', 'poison'],
    'heal': ['heal', 'restore', 'regenerate', 'replenish'],
}


def palavras_no_texto(texto, lista):
    t = texto.lower()
    return [p for p in lista if p in t]


def coerencia(base_fam, texto):
    """
    Retorna (veredito, motivo):
      CONFIRMADO_QUEBRADO — texto promete X mas base faz Y
      SUSPEITO             — texto é ambíguo
      OK                   — texto bate com a base
    """
    if not texto or base_fam is None:
        return 'SEM_DADOS', ''

    t = texto.lower()

    if base_fam == 'invoca':
        # Se o texto promete dano direto, ta quebrado (base invoca,
        # não faz dano direto)
        if palavras_no_texto(texto, PALAVRAS_DESIGN['dano_direto']):
            if not palavras_no_texto(texto, PALAVRAS_DESIGN['invoca']):
                return 'CONFIRMADO_QUEBRADO', 'base invoca unidade, texto promete dano direto'
        if palavras_no_texto(texto, PALAVRAS_DESIGN['dano_area']):
            if not palavras_no_texto(texto, PALAVRAS_DESIGN['invoca']):
                return 'CONFIRMADO_QUEBRADO', 'base invoca unidade, texto promete dano em area'
        if palavras_no_texto(texto, PALAVRAS_DESIGN['buff']):
            if not palavras_no_texto(texto, PALAVRAS_DESIGN['invoca']):
                return 'CONFIRMADO_QUEBRADO', 'base invoca unidade, texto promete buff'

    if base_fam == 'drain':
        if palavras_no_texto(texto, PALAVRAS_DESIGN['dano_area']):
            return 'CONFIRMADO_QUEBRADO', 'base drain (canalizacao), texto promete area'

    if base_fam == 'buff_fogo':
        if palavras_no_texto(texto, PALAVRAS_DESIGN['dano_area']):
            if 'flame' not in t and 'fire' not in t:
                return 'CONFIRMADO_QUEBRADO', 'base immolation, texto promete area diferente'

    return 'OK', ''


def main():
    if len(sys.argv) < 2:
        print("Uso: python check_coerencia.py <caminho.w3x>")
        sys.exit(1)
    caminho = sys.argv[1]

    with open('codigo_heroi.json', encoding='utf-8') as f:
        mapa_heroi = json.load(f)

    skills = parser_w3a.extrair_skills(caminho)

    # Lista fixa das 21+5 pra analisar
    ALVO = [
        # ANcl
        ('A0BT', 'Shura'), ('A0CU', 'Shura'), ('A0CV', 'Shura'),
        ('A0CW', 'Shura'), ('A0CX', 'Shura'), ('A0G4', 'Shura'),
        ('A07W', 'Milo'), ('A08Z', 'Milo'), ('A083', 'Saga'),
        ('A00Q', 'Siegfried'), ('A0BV', 'Shun'),
        ('A0FF', 'Hyoga'), ('A0FK', 'Hyoga'), ('A07M', 'Aldebaran'),
        # ANrc
        ('A010', 'Mu'), ('A00S', 'Siegfried'),
        # AUau
        ('A09P', 'Afrodite'), ('A016', 'DeathMask'),
        # Efeito oposto
        ('A09M', 'Afrodite'), ('A09R', 'Afrodite'),
        ('A017', 'Shion'),    ('A020', 'Shun'),
        # Confirmar
        ('A087', 'Milo'), ('A07N', 'Orpheu'), ('A099', 'Shiryu'),
        ('A047', 'Seiya'), ('A067', 'Shura'),
    ]

    print(f"Analisando {len(ALVO)} skills...\n")

    resultados = []
    for cod, heroi in ALVO:
        info = skills.get(cod)
        if not info:
            resultados.append((cod, heroi, '?', 'NAO_ENCONTRADO', ''))
            continue
        base = info.get('base') or '?'
        fam = FAMILIA_BASE.get(base, '?')

        # Pega aub1 (todos os níveis, concatena)
        aub1 = info.get('aub1', {})
        if isinstance(aub1, dict):
            texto = ' '.join(str(v) for v in aub1.values() if v)
        else:
            texto = str(aub1 or '')

        veredito, motivo = coerencia(fam, texto)
        resultados.append((cod, heroi, base, veredito, motivo))

    # Saída
    saida = Path(__file__).parent / 'saida'
    txt = saida / 'check_coerencia.txt'
    with open(txt, 'w', encoding='utf-8') as f:
        f.write(f"=== COERENCIA aub1 x base — {len(resultados)} skills ===\n\n")

        grupos = {}
        for r in resultados:
            grupos.setdefault(r[3], []).append(r)

        for veredito in ['CONFIRMADO_QUEBRADO', 'SUSPEITO', 'OK', 'SEM_DADOS', '?', 'NAO_ENCONTRADO']:
            if veredito not in grupos:
                continue
            f.write(f"\n### {veredito} ({len(grupos[veredito])})\n\n")
            for cod, heroi, base, v, motivo in grupos[veredito]:
                f.write(f"  {cod} ({heroi}) | base={base}\n")
                if motivo:
                    f.write(f"      {motivo}\n")

    # Console
    for veredito in ['CONFIRMADO_QUEBRADO', 'SUSPEITO', 'OK', 'SEM_DADOS', '?']:
        if veredito not in grupos:
            continue
        print(f"### {veredito} ({len(grupos[veredito])})")
        for cod, heroi, base, v, motivo in grupos[veredito]:
            print(f"  {cod} ({heroi}) | base={base}" + (f" — {motivo}" if motivo else ""))
        print()

    print(f"Relatorio: {txt}")


if __name__ == '__main__':
    main()
