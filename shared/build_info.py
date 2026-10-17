"""Local source identities, independent of Git availability and runtime data."""

import hashlib
from pathlib import Path


def hash_files(root, files):
    root = Path(root).resolve()
    selected = sorted(
        {Path(p) for p in files if Path(p).is_file()},
        key=lambda p: p.relative_to(root).as_posix().encode("utf-8"),
    )
    digest = hashlib.sha256()
    for path in selected:
        name = path.relative_to(root).as_posix()
        content = hashlib.sha256(path.read_bytes()).hexdigest()
        digest.update(f"{name}\0{content}\n".encode("utf-8"))
    return digest.hexdigest()


def service_fingerprint(root):
    root = Path(root).resolve()
    files = [
        p
        for folder in ["backend", "solver", "shared"]
        for p in (root / folder).rglob("*")
        if p.suffix in (".py", ".json") and "__pycache__" not in p.parts
    ]
    files += list((root / "contracts").glob("*.schema.json"))
    files += [root / "requirements.lock.txt"]
    return hash_files(root, files)


def frontend_files(root):
    root = Path(root).resolve()
    frontend = root / "frontend"
    files = [
        p
        for folder in ["src", "public"]
        for p in (frontend / folder).rglob("*")
        if p.is_file()
    ]
    files += [
        frontend / name
        for name in [
            "index.html",
            "package.json",
            "package-lock.json",
            "scripts/build-info.mjs",
        ]
    ]
    files += list(frontend.glob("tsconfig*.json"))
    files += list(frontend.glob("vite.config.*"))
    return files


def frontend_fingerprint(root):
    return hash_files(root, frontend_files(root))


def verification_fingerprint(root):
    root = Path(root).resolve()
    files = [
        p
        for folder in [
            "tests",
            "scripts",
            "fixtures",
            "contracts",
            ".github",
            "frontend/tests",
            "frontend/scripts",
        ]
        for p in (root / folder).rglob("*")
        if p.is_file() and p.suffix in (".py", ".json", ".mjs", ".ts", ".yml", ".yaml")
    ]
    files += frontend_files(root)
    files += [
        p
        for folder in ["backend", "solver", "shared"]
        for p in (root / folder).rglob("*")
        if p.suffix in (".py", ".json") and "__pycache__" not in p.parts
    ]
    files += list(root.glob("requirements*.txt")) + list(root.glob("*.cmd"))
    return hash_files(root, files)
