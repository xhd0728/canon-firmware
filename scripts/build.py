#!/usr/bin/env python3
"""Build a pinned EOS 60D package; never access cameras or memory cards."""
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from validate import validate

ROOT = Path(__file__).resolve().parent.parent
LOCK = json.loads((ROOT / "sources.lock.json").read_text())


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def checkout(language):
    spec = LOCK["sources"][language]
    path = ROOT / ".work" / language
    if not path.exists():
        run("git", "init", str(path))
        run("git", "-C", str(path), "remote", "add", "origin", spec["url"])
        run("git", "-C", str(path), "fetch", "--depth=1", "origin", spec["commit"])
        run("git", "-C", str(path), "checkout", "--detach", "FETCH_HEAD")
    actual = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if actual != spec["commit"]:
        raise RuntimeError(f"Unexpected source revision in {path}")
    return path


def prepare(language):
    src = checkout(language)
    restored = []
    if language == "zh":
        upstream = checkout("en")
        restored = json.loads((ROOT / "scripts/upstream-files.json").read_text())
        for name in restored:
            target = src / name
            data = (upstream / name).read_bytes()
            if target.exists() and target.read_bytes() != data:
                raise RuntimeError(f"Refusing to replace changed asset: {name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    # The Lua/newlib compatibility declarations are already present in the
    # pinned Chinese fork; apply the same declarations to the English source.
    patches = ["chinese-build.patch"] if language == "zh" else ["english-build.patch", "lua-newlib.patch"]
    for name in patches:
        patch = ROOT / "patches" / name
        applied = subprocess.run(["git", "-C", str(src), "apply", "--reverse", "--check", str(patch)], capture_output=True)
        if applied.returncode:
            run("git", "-C", str(src), "apply", "--check", str(patch))
            run("git", "-C", str(src), "apply", str(patch))
    return src, restored


def build(language):
    tc = ROOT / ".work" / LOCK["toolchain"]["version"] / "bin"
    python = ROOT / ".work/python/bin/python"
    if not (tc / "arm-none-eabi-gcc").exists() or not python.exists():
        raise SystemExit("Run python3 scripts/setup.py first")
    src, restored = prepare(language)
    out = ROOT / "dist" / language
    out.mkdir(parents=True, exist_ok=True)
    stem = f"magiclantern-eos60d-111-{language}"
    log = out / "build.log"
    cmd = ["make", "-C", str(src / "platform/60D.111"), "-j" + str(min(os.cpu_count() or 2, 4)),
           f"ARM_BINPATH={tc}", f"READELF={tc}/arm-none-eabi-readelf", f"PYTHON={python}", f"PYTHON3={python}"]
    if platform.system() == "Darwin":
        cmd.append("STAT_CMD=stat -f %N:%z")
    env = dict(os.environ)
    env["PATH"] = str(python.parent) + os.pathsep + str(tc) + os.pathsep + env.get("PATH", "")
    with log.open("w") as stream:
        result = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT, env=env)
    if result.returncode:
        print("\n".join(log.read_text(errors="replace").splitlines()[-80:]))
        raise SystemExit(result.returncode)
    manifest = {
        "camera": "Canon EOS 60D", "required_canon_firmware": "1.1.1", "language": language,
        "source": LOCK["sources"][language], "restored_assets_from": LOCK["sources"]["en"] if restored else None,
        "patches": ["chinese-build.patch"] if language == "zh" else ["english-build.patch", "lua-newlib.patch"],
        "toolchain": LOCK["toolchain"]["version"], "build_host": platform.system() + " " + platform.machine(),
        "built_at": datetime.now(timezone.utc).isoformat(),
        "repository_commit": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "compiler": subprocess.check_output([str(tc / "arm-none-eabi-gcc"), "--version"], text=True).splitlines()[0],
        "experimental": True, "hardware_tested": False,
    }
    package = out / f"{stem}.zip"
    shutil.copyfile(src / "platform/60D.111/build/magiclantern.zip", package)
    with zipfile.ZipFile(package, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("ML/doc/BUILD.json", json.dumps(manifest, indent=2) + "\n")
        archive.write(src / "COPYING", "ML/doc/COPYING.txt")
    manifest["validation"] = validate(package, src, language, LOCK)
    manifest["package_sha256"] = hashlib.sha256(package.read_bytes()).hexdigest()
    (out / f"{stem}.json").write_text(json.dumps(manifest, indent=2) + "\n")

    # Archive the exact source files used, including patches and restored assets,
    # but never .git, build output, camera data or the compiler installation.
    tracked = subprocess.check_output(["git", "-C", str(src), "ls-files", "-z"]).decode().split("\0")
    source_bundle = out / f"{stem}-source.tar.gz"
    with tarfile.open(source_bundle, "w:gz") as archive:
        for name in sorted(set(filter(None, tracked)) | set(restored)):
            path = src / name
            if path.is_file():
                archive.add(path, arcname=f"{stem}-source/{name}", recursive=False)
        for path in [ROOT / "sources.lock.json", *sorted((ROOT / "scripts").glob("*.py")),
                     ROOT / "scripts/upstream-files.json", *sorted((ROOT / "patches").glob("*.patch"))]:
            archive.add(path, arcname=f"{stem}-source/build-recipe/{path.relative_to(ROOT)}", recursive=False)
    assets = [package, source_bundle, out / f"{stem}.json"]
    (out / f"SHA256SUMS-{language}.txt").write_text("".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in assets))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", choices=["en", "zh"], required=True)
    build(parser.parse_args().language)
