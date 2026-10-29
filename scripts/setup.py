#!/usr/bin/env python3
"""Install the pinned compiler and Python dependencies inside .work/."""
import hashlib
import json
import platform
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = json.loads((ROOT / "sources.lock.json").read_text())
host = {("Darwin", "arm64"): "darwin-arm64", ("Linux", "x86_64"): "linux-x64"}.get(
    (platform.system(), platform.machine())
)
if host is None:
    raise SystemExit("Supported hosts: Linux x86-64 and macOS arm64")
work = ROOT / ".work"
work.mkdir(exist_ok=True)
archive = work / f"gcc-{host}.tar.gz"
spec = LOCK["toolchain"]["platforms"][host]
if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest() != spec["sha256"]:
    subprocess.run(["curl", "-fL", "--retry", "3", "--max-time", "600", spec["url"], "-o", str(archive)], check=True)
if hashlib.sha256(archive.read_bytes()).hexdigest() != spec["sha256"]:
    raise SystemExit("Compiler archive checksum mismatch")
compiler = work / LOCK["toolchain"]["version"] / "bin/arm-none-eabi-gcc"
if not compiler.exists():
    with tarfile.open(archive) as package:
        package.extractall(work, filter="data")
subprocess.run(["python3", "-m", "venv", str(work / "python")], check=True)
subprocess.run([str(work / "python/bin/pip"), "install", "docutils==" + LOCK["python_dependencies"]["docutils"]], check=True)
