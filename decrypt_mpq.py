# -*- coding: utf-8 -*-
"""
Decriptador MPQ completo (multi-sector + encriptação).
Usa zlib.decompressobj para tolerar Adler corrompido do último setor.
"""
import sys, zlib, bz2
from pathlib import Path
from parser_w3a import _abrir_mpq


def init_crypt_table():
    seed = 0x00100001
    table = [0] * 0x500
    for i in range(0x100):
        idx = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp1 = (seed & 0xFFFF) << 0x10
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp2 = seed & 0xFFFF
            table[idx] = (temp1 | temp2) & 0xFFFFFFFF
            idx += 0x100
    return table

CT = init_crypt_table()


def hash_string(s, hash_type):
    seed1 = 0x7FED7FED
    seed2 = 0xEEEEEEEE
    for ch in s.upper():
        c = ord(ch)
        seed1 = (CT[(hash_type * 0x100) + c] ^ (seed1 + seed2)) & 0xFFFFFFFF
        seed2 = (c + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1


def decrypt(data, key):
    seed = 0xEEEEEEEE
    result = bytearray()
    for i in range(0, len(data), 4):
        key &= 0xFFFFFFFF
        seed = (seed + CT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        ch = int.from_bytes(data[i:i+4], 'little')
        ch = (ch ^ ((key + seed) & 0xFFFFFFFF)) & 0xFFFFFFFF
        result += ch.to_bytes(4, 'little')
        not_key = (~key) & 0xFFFFFFFF
        new_key = (((not_key << 0x15) & 0xFFFFFFFF) + 0x11111111) & 0xFFFFFFFF
        new_key |= (key >> 0x0B)
        key = new_key & 0xFFFFFFFF
        seed = (ch + seed + (seed << 5) + 3) & 0xFFFFFFFF
    return bytes(result[:len(data)])


def descomprimir_setor(sector_data):
    """Cada setor MPQ tem 1 byte de tipo + corpo."""
    if len(sector_data) == 0:
        return b''
    comp_type = sector_data[0]
    body = sector_data[1:]
    if comp_type == 0x00:
        return body
    if comp_type == 0x02:
        # zlib: header 2 bytes (78 xx) + deflate + adler32
        # Usa raw deflate pra ignorar o adler32 final
        if len(body) >= 2 and body[0] in (0x78, 0x58, 0x28):
            raw = body[2:-4]  # tira header 2B + adler 4B
            try:
                return zlib.decompress(raw, -15)
            except Exception:
                pass
        # fallback: tenta zlib puro
        d = zlib.decompressobj()
        out = d.decompress(body)
        try:
            out += d.flush()
        except Exception:
            pass
        return out
    if comp_type == 0x10:
        return bz2.decompress(body)
    for f in (zlib.decompress, bz2.decompress):
        try:
            return f(body)
        except Exception:
            pass
    raise ValueError(f'Tipo desconhecido: 0x{comp_type:02X}')


def ler_arquivo(mapa_path, nome_arquivo):
    with open(mapa_path, 'rb') as f:
        raw = f.read()
    base_offset = 0
    if raw[:4] == b'HM3W':
        base_offset = 512
    if raw[base_offset:base_offset+4] != b'MPQ\x1a':
        idx = raw.find(b'MPQ\x1a')
        if idx < 0:
            raise RuntimeError('Sem assinatura MPQ')
        base_offset = idx

    arq = _abrir_mpq(raw[base_offset:])
    entry = arq.get_hash_table_entry(nome_arquivo)
    if entry is None:
        return None, None

    block = arq.block_table[entry.block_table_index]
    block_offset = block.offset
    block_comp = block.archived_size
    block_size = block.size
    block_flags = block.flags

    offset = base_offset + block_offset
    data = raw[offset:offset+block_comp]

    FIX_KEY   = 0x00020000
    ENCRYPTED = 0x00010000
    COMPRESS  = 0x00000200
    SINGLE    = 0x01000000

    base_key = hash_string(nome_arquivo, 3)
    file_key = base_key
    if block_flags & FIX_KEY:
        file_key = ((base_key + block_offset) ^ block_size) & 0xFFFFFFFF

    SECTOR_SIZE = 0x1000

    # Multi-sector
    if (block_flags & COMPRESS) and not (block_flags & SINGLE):
        num_sectors = (block_size + SECTOR_SIZE - 1) // SECTOR_SIZE
        table_size = (num_sectors + 1) * 4

        table_bytes = bytes(data[:table_size])
        if block_flags & ENCRYPTED:
            table_bytes = decrypt(table_bytes, (file_key - 1) & 0xFFFFFFFF)

        sector_offsets = [int.from_bytes(table_bytes[i*4:i*4+4], 'little')
                          for i in range(num_sectors + 1)]

        decompressed = bytearray()
        for i in range(num_sectors):
            start = sector_offsets[i]
            end = sector_offsets[i+1]
            sector_data = bytes(data[start:end])

            if block_flags & ENCRYPTED:
                sector_data = decrypt(sector_data, (file_key + i) & 0xFFFFFFFF)

            expected_unc = SECTOR_SIZE
            if i == num_sectors - 1:
                expected_unc = block_size - (num_sectors - 1) * SECTOR_SIZE

            if len(sector_data) == expected_unc:
                decompressed += sector_data
            else:
                decompressed += descomprimir_setor(sector_data)

        return bytes(decompressed), {
            "offset": block_offset, "compressed_size": block_comp,
            "size": block_size, "flags": block_flags,
        }

    # Single unit ou sem compressão
    if block_flags & ENCRYPTED:
        data = decrypt(data, file_key)
    if block_flags & COMPRESS:
        return descomprimir_setor(data), {"offset": block_offset,
            "compressed_size": block_comp, "size": block_size,
            "flags": block_flags}
    return bytes(data), {"offset": block_offset,
        "compressed_size": block_comp, "size": block_size,
        "flags": block_flags}


def main():
    if len(sys.argv) < 2:
        print("Uso: python decrypt_mpq.py <caminho.w3x>")
        sys.exit(1)

    mapa = sys.argv[1]
    saida_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('w3u')
    saida_dir.mkdir(parents=True, exist_ok=True)

    for nome in ['war3map.w3a', 'war3map.w3u', 'war3map.w3h', 'war3map.w3q', 'war3map.w3t']:
        print(f'--- {nome} ---')
        try:
            data, block = ler_arquivo(mapa, nome)
            if data is None:
                print('  NAO ENCONTRADO\n')
                continue
            print(f'  block: offset={block["offset"]} comp={block["compressed_size"]} '
                  f'size={block["size"]} flags=0x{block["flags"]:08X}')
            print(f'  descomprimido: {len(data)} bytes (esperado: {block["size"]})')
            print(f'  primeiros 16 bytes: {data[:16].hex()}')
            if len(data) >= 4:
                v = int.from_bytes(data[:4], 'little')
                print(f'  versão: {v}')

            out = saida_dir / nome
            with open(out, 'wb') as f:
                f.write(data)
            print(f'  salvo em {out}')
        except Exception as e:
            import traceback
            print(f'  ERRO: {type(e).__name__}: {e}')
            traceback.print_exc()
        print()


if __name__ == '__main__':
    main()
