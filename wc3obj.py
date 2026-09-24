"""Decoder for WC3 'object modification' files (war3map.w3u/.w3t/.w3a/.w3b/...)
and the war3map.wts string table (TRIGSTR resolution).

Format per HiveWE's documentation (stijnherfst/HiveWE wiki,
"war3map.w3*-Modifications"):

    uint32 format_version        -- 1, 2 (classic/TFT) or 3 (Reforged 1.32+)

    the following structure appears 1 or 2 times (original table, custom table):

        uint32 object_count
        for each object:
            char[4] original_id
            char[4] modified_id          -- 0 for the "original" table

            if format_version >= 3:
                uint32 sets_count
            else:
                sets_count = 1

            for each set:
                if format_version >= 3:
                    uint32 set_flag
                uint32 modifications_count
                for each modification:
                    char[4] modification_id
                    uint32  variable_type      -- 0 int, 1 real, 2 unreal, 3 string

                    if OPTIONAL_INTS[extension]:
                        uint32 level_variation
                        uint32 data_pointer

                    <value depending on variable_type>

                    if format_version > 0:
                        char[4] end_token

OPTIONAL_INTS (the extra level/data_pointer pair) is Yes only for .w3a
(abilities) and .w3q (upgrades); .w3d (doodads) only when format_version > 0.
"""
import struct

OPTIONAL_INTS_ALWAYS = {"w3a", "w3q"}
OPTIONAL_INTS_IF_VERSIONED = {"w3d"}  # optional_ints when format_version > 0


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def i32(self) -> int:
        v = struct.unpack_from("<i", self.data, self.pos)[0]
        self.pos += 4
        return v

    def u32(self) -> int:
        v = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return v

    def f32(self) -> float:
        v = struct.unpack_from("<f", self.data, self.pos)[0]
        self.pos += 4
        return v

    def fourcc(self) -> str:
        raw = self.data[self.pos:self.pos + 4]
        self.pos += 4
        return raw.decode("latin1")

    def cstr(self) -> str:
        start = self.pos
        end = self.data.index(b"\x00", start)
        s = self.data[start:end].decode("utf-8", errors="replace")
        self.pos = end + 1
        return s

    def remaining(self) -> int:
        return len(self.data) - self.pos

    def eof(self) -> bool:
        return self.pos >= len(self.data)


def parse_object_file(data: bytes, extension: str):
    """Returns {'version': int, 'original': [...], 'custom': [...]}.
    Each object: {'old_id', 'new_id', 'mods': [ {field, type, value, level?, data_ptr?} ]}
    (mods from all sets are flattened together per object)."""
    r = Reader(data)
    version = r.i32()

    optional_ints = (extension in OPTIONAL_INTS_ALWAYS or
                      (extension in OPTIONAL_INTS_IF_VERSIONED and version > 0))
    has_end_token = version > 0

    def read_modification():
        field_id = r.fourcc()
        var_type = r.i32()
        level = data_ptr = None
        if optional_ints:
            level = r.i32()
            data_ptr = r.i32()
        if var_type == 0:
            value = r.i32()
        elif var_type in (1, 2):
            value = r.f32()
        elif var_type == 3:
            value = r.cstr()
        else:
            raise ValueError(
                "Unknown varType %d for field %r at pos %d" % (var_type, field_id, r.pos))
        end_token = r.fourcc() if has_end_token else None
        mod = {"field": field_id, "type": var_type, "value": value}
        if optional_ints:
            mod["level"] = level
            mod["data_ptr"] = data_ptr
        if has_end_token:
            mod["end_token"] = end_token
        return mod

    def read_table():
        count = r.i32()
        objects = []
        for _ in range(count):
            old_id = r.fourcc()
            new_id = r.fourcc()
            sets_count = r.i32() if version >= 3 else 1
            mods = []
            for _ in range(sets_count):
                if version >= 3:
                    r.i32()  # set_flag
                mod_count = r.i32()
                for _ in range(mod_count):
                    mods.append(read_modification())
            objects.append({"old_id": old_id, "new_id": new_id, "mods": mods})
        return objects

    original = read_table()
    custom = read_table() if not r.eof() else []
    return {"version": version, "original": original, "custom": custom}


def parse_wts(text: str) -> dict:
    """Parse war3map.wts (already decoded as text) into {id: string}."""
    import re
    result = {}
    for m in re.finditer(r"STRING\s+(\d+)\s*\r?\n\{\r?\n(.*?)\r?\n\}", text, re.DOTALL):
        result[int(m.group(1))] = m.group(2)
    return result


def resolve(value, wts: dict):
    """Resolve a TRIGSTR(n) string reference using the wts table."""
    if isinstance(value, str) and value.startswith("TRIGSTR_"):
        try:
            num = int(value[len("TRIGSTR_"):])
            return wts.get(num, value)
        except ValueError:
            return value
    return value


class Writer:
    def __init__(self):
        self.buf = bytearray()

    def i32(self, v: int):
        self.buf += struct.pack("<i", v)

    def f32(self, v: float):
        self.buf += struct.pack("<f", v)

    def fourcc(self, s: str):
        b = s.encode("latin1")
        if len(b) != 4:
            raise ValueError("FourCC must be exactly 4 bytes: %r" % s)
        self.buf += b

    def cstr(self, s: str):
        self.buf += s.encode("utf-8") + b"\x00"

    def bytes(self) -> bytes:
        return bytes(self.buf)


def write_object_file(parsed: dict, extension: str) -> bytes:
    """Inverse of parse_object_file: serialize {'version','original','custom'}
    back to the exact binary layout described at the top of this module.
    Each object's 'mods' list is written as a single set (set_flag=0 for v3),
    which matches what every mapmaking tool (including the World Editor)
    produces -- multiple sets are a Reforged-only feature for asset-mode
    variants that ordinary edits never need."""
    version = parsed["version"]
    optional_ints = (extension in OPTIONAL_INTS_ALWAYS or
                      (extension in OPTIONAL_INTS_IF_VERSIONED and version > 0))
    has_end_token = version > 0

    w = Writer()
    w.i32(version)

    def write_table(objects):
        w.i32(len(objects))
        for o in objects:
            w.fourcc(o["old_id"])
            new_id = o["new_id"] if o["new_id"] else "\x00\x00\x00\x00"
            w.fourcc(new_id)
            if version >= 3:
                w.i32(1)  # sets_count
                w.i32(0)  # set_flag
            w.i32(len(o["mods"]))
            for m in o["mods"]:
                w.fourcc(m["field"])
                w.i32(m["type"])
                if optional_ints:
                    w.i32(m.get("level") or 0)
                    w.i32(m.get("data_ptr") or 0)
                if m["type"] == 0:
                    w.i32(int(m["value"]))
                elif m["type"] in (1, 2):
                    w.f32(float(m["value"]))
                elif m["type"] == 3:
                    w.cstr(str(m["value"]))
                else:
                    raise ValueError("Unknown varType %d" % m["type"])
                if has_end_token:
                    # Preserve whatever the source file had here (spec says
                    # it's unused by WE/game); default to zero for a
                    # modification we're adding fresh.
                    w.fourcc(m.get("end_token") or "\x00\x00\x00\x00")

    write_table(parsed["original"])
    write_table(parsed["custom"])
    return w.bytes()
