# -*- coding: utf-8 -*-
"""
parser_w3u.py — extrai war3map.w3u (unit data) de um .w3x.

Formato idêntico ao w3a: mesmo wrapper HM3W, mesmo mpyq patch,
mesmo wc3obj.parse_object_file com tag 'w3u'.
"""
import io

from parser_w3a import _abrir_mpq


def _extrair_w3u_bytes(caminho):
    """Aceita .w3x (wrapper HM3W) ou .mpq puro."""
    with open(caminho, 'rb') as f:
        raw = f.read()

    if raw[:4] == b'HM3W':
        raw = raw[512:]

    if not raw.startswith(b'MPQ\x1a'):
        idx = raw.find(b'MPQ\x1a')
        if idx < 0:
            raise RuntimeError("Não achei assinatura MPQ no arquivo.")
        raw = raw[idx:]

    arq = _abrir_mpq(raw)
    data = arq.read_file('war3map.w3u')
    if not data:
        raise FileNotFoundError("war3map.w3u não está dentro do arquivo.")
    return data


def extrair_unidades(caminho_w3x, codigos=None):
    """Retorna {codigo: {...}} com os campos de herói que interessam."""
    from wc3obj import parse_object_file

    data = _extrair_w3u_bytes(caminho_w3x)
    parsed = parse_object_file(data, 'w3u')

    indexado = {}
    for obj in parsed['original']:
        codigo = obj['old_id']
        if codigo and codigo != '\x00\x00\x00\x00':
            indexado[codigo] = obj
    for obj in parsed['custom']:
        codigo = obj['new_id']
        if codigo and codigo != '\x00\x00\x00\x00':
            indexado[codigo] = obj

    resultado = {}
    for codigo in (codigos or indexado.keys()):
        obj = indexado.get(codigo)
        if obj is None:
            resultado[codigo] = {'erro': True}
            continue

        is_custom = obj['new_id'] and obj['new_id'] != '\x00\x00\x00\x00'
        base = obj['old_id'] if is_custom else None

        skill = {
            'erro': False,
            'codigo': codigo,
            'base': base,
            'unam': None,   # nome
            'upro': None,   # nome próprio (proper names)
            'urac': None,   # raça
            'uprim': None,  # atributo primário: 0=STR, 1=INT, 2=AGI
            'ustr': None, 'uagi': None, 'uint': None,
            'ustp': None, 'uagp': None, 'uinp': None,
            'umdl': None, 'uico': None,
        }

        for m in obj['mods']:
            campo = m['field']
            nivel = m.get('level', 0) or 0
            valor = m['value']

            if campo in skill and nivel == 0:
                skill[campo] = valor

        resultado[codigo] = skill

    return resultado


# Nomes amigáveis dos atributos primários
ATRIBUTO_NOME = {0: 'STR', 1: 'INT', 2: 'AGI'}
