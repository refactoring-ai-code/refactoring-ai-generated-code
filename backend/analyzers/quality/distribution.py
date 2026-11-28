"""Install only the JVM libraries from PMD's checksum-pinned release."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

VERSION = "7.29.0"
ARCHIVE_NAME = f"pmd-dist-{VERSION}-bin.zip"
ARCHIVE_SHA256 = "d27177c185b837fa57f097e482d1253468aa035379c5eb2671fa0a279109b179"
URL = f"https://github.com/pmd/pmd/releases/download/pmd_releases/{VERSION}/{ARCHIVE_NAME}"
CACHE = Path(__file__).resolve().parent / ".cache"
DIST_NAME = f"pmd-bin-{VERSION}"


def installed_libraries(cache: Path) -> Path | None:
    directory = cache / DIST_NAME
    receipt = directory / "archive.sha256"
    if receipt.is_file() and receipt.read_text(encoding="ascii") == ARCHIVE_SHA256:
        libraries = directory / "lib"
        if (libraries / f"pmd-cli-{VERSION}.jar").is_file():
            return libraries
    return None


def install_distribution(cache: Path = CACHE, archive: Path | None = None) -> Path:
    if libraries := installed_libraries(cache):
        return libraries
    cache.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as workspace:
        temporary = Path(workspace)
        if archive is None:
            archive = temporary / ARCHIVE_NAME
            with urllib.request.urlopen(URL, timeout=60) as response, archive.open("wb") as output:
                shutil.copyfileobj(response, output)
        with archive.open("rb") as source:
            if hashlib.file_digest(source, "sha256").hexdigest() != ARCHIVE_SHA256:
                raise ValueError("PMD distribution SHA-256 mismatch")
            source.seek(0)
            installation = temporary / DIST_NAME
            libraries = installation / "lib"
            libraries.mkdir(parents=True)
            prefix = f"{DIST_NAME}/lib/"
            with zipfile.ZipFile(source) as distribution:
                for entry in distribution.infolist():
                    name = entry.filename.removeprefix(prefix)
                    if name != entry.filename and "/" not in name and name.endswith(".jar"):
                        with distribution.open(entry) as jar, (libraries / name).open("xb") as out:
                            shutil.copyfileobj(jar, out)
            if not (libraries / f"pmd-cli-{VERSION}.jar").is_file():
                raise ValueError("The pinned archive has no PMD CLI library")
            (installation / "archive.sha256").write_text(ARCHIVE_SHA256, encoding="ascii")
            try:
                installation.rename(cache / DIST_NAME)
            except OSError:
                if not installed_libraries(cache):
                    raise
    return cache / DIST_NAME / "lib"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Use a local copy of the official release")
    args = parser.parse_args()
    install_distribution(archive=args.archive)
    print(f"PMD and CPD {VERSION} installed from a SHA-256-verified distribution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
