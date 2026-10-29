"""Validate package structure, installer identity, modules and CJK fonts."""
import hashlib
import re
import stat
import struct
import zipfile
from pathlib import PurePosixPath


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(package, source, language, lock):
    checks = []
    with zipfile.ZipFile(package) as archive:
        require(archive.testzip() is None, "ZIP CRC failure")
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate ZIP entries")
        for entry in archive.infolist():
            path = PurePosixPath(entry.filename)
            require(not path.is_absolute() and ".." not in path.parts, "Unsafe ZIP path")
            require(not stat.S_ISLNK(entry.external_attr >> 16), "Unexpected ZIP symlink")
        required = {"autoexec.bin", "ML-SETUP.FIR", "ML/modules/60D_111.sym", "ML/doc/BUILD.json", "ML/doc/COPYING.txt"}
        require(required <= set(names), "Missing required package files")
        require(hashlib.sha256(archive.read("ML-SETUP.FIR")).hexdigest() == lock["installer_sha256"], "Wrong EOS 60D installer")
        require(not any(n.upper().endswith("MODULES.LST") or n.upper().startswith("ML/SETTINGS/") and not n.endswith("/") for n in names), "Unexpected personal settings or module autoload")
        binary = archive.read("autoexec.bin")
        require(len(binary) > 0 and len(binary) % 4 == 0, "Invalid startup binary size")
        checksum = 0
        for (word,) in struct.iter_unpack("<I", binary):
            checksum ^= word
        require(checksum == 0, "Invalid startup XOR checksum")
        checks.extend(["ZIP CRC and paths", "EOS 60D installer SHA-256", "No user settings or module autoload", "Startup XOR checksum"])
        modules = [x.strip() for x in (source / "platform/60D.111/modules.included").read_text().splitlines() if x.strip() and not x.startswith("#")]
        for module in modules:
            require(f"ML/modules/{module}.mo" in names, f"Missing module: {module}")
        checks.append(f"All {len(modules)} configured modules")
        if language == "zh":
            require("ML/doc/menuidx.dat" in names, "Missing Chinese help index")
            characters = set()
            for directory in ("src", "modules"):
                for path in (source / directory).rglob("*.c"):
                    characters.update(re.findall(r"[\u4e00-\u9fff]", path.read_text(errors="replace")))
            for height in (12, 23, 28, 32):
                data = archive.read(f"ML/fonts/cjk{height}.rbf")
                magic, version, h, count = struct.unpack_from("<4sIHI", data)
                require((magic, version, h) == (b"CRBF", 1, height), "Invalid CJK header")
                offset, points = 14, []
                for _ in range(count):
                    cp, width, _advance = struct.unpack_from("<IHH", data, offset)
                    offset += 8 + ((width + 7) // 8) * h
                    require(offset <= len(data), "Truncated CJK glyph")
                    points.append(cp)
                require(offset == len(data) and points == sorted(set(points)), "Invalid CJK layout")
                require(not (characters - set(map(chr, points))), "Missing Chinese characters")
            checks.append("Four CJK fonts: structure, ordering and source character coverage")
    return checks
