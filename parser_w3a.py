"""
parser_w3a.py — extrai war3map.w3a de um .w3x / .w3m e desmonta usando wc3obj.

Requer:
    pip install mpyq
    wc3obj.py na mesma pasta

Funciona com .w3x clássico (wrapper HM3W de 512 bytes) e .mpq puro.
Tolera listfile encriptado (patch no mpyq).
"""
import io
import re


def _abrir_mpq(data):
    """Abre MPQ via mpyq, tolerando listfile encriptado."""
    import mpyq
    _orig = mpyq.MPQArchive.__init__

    def _safe(self, fn, *a, **k):
        try:
            _orig(self, fn, *a, **k)
        except NotImplementedError:
            self.files = []

    mpyq.MPQArchive.__init__ = _safe
    return mpyq.MPQArchive(io.BytesIO(data))


def _extrair_w3a_bytes(caminho):
    """Aceita .w3x (wrapper HM3W) ou .mpq puro."""
    with open(caminho, 'rb') as f:
        raw = f.read()

    # .w3x clássico: pula wrapper de 512 bytes
    if raw[:4] == b'HM3W':
        raw = raw[512:]

    # Se não começa com MPQ, procura a assinatura
    if not raw.startswith(b'MPQ\x1a'):
        idx = raw.find(b'MPQ\x1a')
        if idx < 0:
            raise RuntimeError(
                "Não achei assinatura MPQ no arquivo. "
                "Talvez seja CASC puro (Reforged) — não suportado ainda."
            )
        raw = raw[idx:]

    arq = _abrir_mpq(raw)
    data = arq.read_file('war3map.w3a')
    if not data:
        raise FileNotFoundError("war3map.w3a não está dentro do arquivo.")
    return data


def _extrair_hotkey(atp1_dict):
    """Procura '(|cffffcc00X|r)' no primeiro atp1 disponível."""
    for nivel in sorted(atp1_dict.keys()):
        v = atp1_dict[nivel]
        if not v or not isinstance(v, str):
            continue
        m = re.search(r'\(\|cffffcc00([A-Z])\|r\)', v)
        if m:
            return m.group(1)
    return None


def extrair_skills(caminho_w3x, codigos=None):
    """Retorna {codigo: {...}} no formato que o cdz_audit.py espera."""
    from wc3obj import parse_object_file

    data = _extrair_w3a_bytes(caminho_w3x)
    parsed = parse_object_file(data, 'w3a')

    # Indexa por código: custom usa new_id, original usa old_id.
    # Custom tem prioridade (sobrescreve original de mesmo código).
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

        # Base: pra custom, old_id é a base nativa. Pra original, é None.
        is_custom = obj['new_id'] and obj['new_id'] != '\x00\x00\x00\x00'
        base = obj['old_id'] if is_custom else None

        atp1 = {}
        aub1 = {}
        skill = {
            'erro': False,
            'codigo': codigo,
            'base': base,
            'anam': None,
            'arut': None,
            'aret': None,
            'alev': None,
        }

        for m in obj['mods']:
            campo = m['field']
            nivel = m.get('level', 0) or 0
            valor = m['value']

            if campo in ('anam', 'arut', 'aret', 'alev'):
                if nivel == 0:
                    skill[campo] = valor
            elif campo == 'atp1':
                atp1[nivel] = valor
            elif campo == 'aub1':
                aub1[nivel] = valor

        skill['atp1'] = atp1
        skill['aub1'] = aub1

        niveis_com_dado = [n for n in list(atp1.keys()) + list(aub1.keys()) if n > 0]
        skill['nivel_max_real'] = max(niveis_com_dado) if niveis_com_dado else 1
        skill['hotkey_detectado'] = _extrair_hotkey(atp1)

        resultado[codigo] = skill

    return resultado