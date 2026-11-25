"""Bounded parsing of source bytes. Uploads are never executed or extracted."""

from __future__ import annotations

import base64
import binascii
import io
import stat
import struct
import unicodedata
import zipfile
import zlib
from dataclasses import dataclass
from pathlib import PurePosixPath

from backend.core.schemas.models import portable_path

MAX_BODY_BYTES = 12 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_ENTRIES = 256
MAX_RATIO = 200
_LANGUAGES = {
    ".java": "java",
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".cs": "csharp",
    ".go": "go",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".hh": "cpp",
    ".c": "c",
    ".h": "unknown",
}
_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".idea",
    ".vscode",
    "vendor",
    "dist",
    "build",
    "target",
}
_DEVICES = {"con", "prn", "aux", "nul", "conin$", "conout$"} | {
    f"{name}{n}" for name in ("com", "lpt") for n in "0123456789¹²³"
}


class InputRejected(ValueError):
    """A rejected upload with a message that contains no user-supplied data."""


def relative_path(raw: str) -> str:
    path = unicodedata.normalize("NFC", raw)
    parts = path.split("/")
    if (
        len(parts) > 24
        or len(path.encode("utf-8", errors="surrogatepass")) > 512
        or any(
            not part
            or part in {".", ".."}
            or part[-1] in {" ", "."}
            or part.split(".", 1)[0].rstrip(" ").casefold() in _DEVICES
            or len(part.encode("utf-8", errors="surrogatepass")) > 100
            for part in parts
        )
        or any(c in '\\:%<>"|?*' or unicodedata.category(c).startswith("C") for c in path)
    ):
        raise InputRejected("Unsafe relative path.")
    return path


def decode_bytes(value: str) -> bytes:
    if len(value) > ((MAX_TOTAL_BYTES + 2) // 3) * 4:
        raise InputRejected("Encoded input exceeds the limit.")
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error):
        raise InputRejected("Invalid base64 input.") from None


def _excluded(path: str) -> str | None:
    parts = path.casefold().split("/")
    name = parts[-1]
    if _EXCLUDED_DIRS.intersection(parts):
        return "tooling-directory"
    if (
        name == ".env"
        or name.startswith(".env.")
        or name in {".npmrc", ".netrc", ".pypirc"}
        or name.endswith((".pem", ".key", ".p12", ".pfx"))
    ):
        return "potential-credentials"
    if name in {".ds_store", "thumbs.db"} or parts[0] == "__macosx":
        return "platform-metadata"
    return None


@dataclass(frozen=True)
class SourceFile:
    path: str
    data: bytes

    @property
    def language(self) -> str:
        return _LANGUAGES.get(PurePosixPath(self.path).suffix.casefold(), "unknown")


class Intake:
    def __init__(self, *, original_zip: bytes | None = None) -> None:
        self.original_zip = original_zip
        self.files: list[SourceFile] = []
        self.excluded: list[dict[str, str]] = []
        self._paths: dict[str, tuple[str, bool]] = {}
        self._explicit: set[str] = set()
        self._total = 0

    def register(self, raw: str, *, directory: bool = False) -> str:
        if len(self._explicit) >= MAX_ENTRIES:
            raise InputRejected("Too many input entries.")
        path = relative_path(raw)
        if path in self._explicit:
            raise InputRejected("Duplicate or ambiguous input paths.")
        parts = path.split("/")
        for i in range(1, len(parts) + 1):
            prefix = "/".join(parts[:i])
            key = unicodedata.normalize("NFC", prefix.casefold())
            entry = (prefix, directory or i < len(parts))
            if key in self._paths and self._paths[key] != entry:
                raise InputRejected("Duplicate or ambiguous input paths.")
            self._paths[key] = entry
        self._explicit.add(path)
        return path

    def add_bytes(self, path: str, data: bytes) -> None:
        self._total += len(data)
        if len(data) > MAX_FILE_BYTES or self._total > MAX_TOTAL_BYTES:
            raise InputRejected("Unpacked input exceeds file or project byte limits.")
        reason = _excluded(path)
        if reason is None:
            try:
                data.decode("utf-8")
            except UnicodeError:
                reason = "non-utf8-or-binary"
            if b"\x00" in data:
                reason = "non-utf8-or-binary"
        if reason:
            self.excluded.append({"path": path, "reason": reason})
        else:
            try:
                canonical = portable_path(path)
            except ValueError:
                raise InputRejected("Unsafe relative path.") from None
            self.files.append(SourceFile(canonical, data))

    def finish(self) -> Intake:
        if not self.files:
            raise InputRejected("No files remain after input exclusions.")
        return self


def _check_zip_directory(data: bytes) -> int:
    # Bound central directory allocations before ZipFile constructs its entry list.
    end = data.rfind(b"PK\x05\x06", max(0, len(data) - 65557))
    if end < 0 or len(data) - end < 22:
        raise InputRejected("Invalid ZIP directory.")
    disk, central_disk, same_disk, count, size, offset, comment = struct.unpack_from(
        "<4H2LH", data, end + 4
    )
    if (
        disk
        or central_disk
        or same_disk != count
        or count > MAX_ENTRIES
        or size > 256 * 1024
        or end != size + offset
        or end + 22 + comment != len(data)
    ):
        raise InputRejected("Unsupported or oversized ZIP directory.")
    if end >= 20 and data[end - 20 : end - 16] == b"PK\x06\x07":
        raise InputRejected("ZIP64 is outside the intake limits.")
    return count


def zip_intake(data: bytes) -> Intake:
    if len(data) > MAX_TOTAL_BYTES:
        raise InputRejected("ZIP input exceeds the limit.")
    entry_count = _check_zip_directory(data)
    result = Intake(original_zip=data)
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) != entry_count or sum(e.file_size for e in entries) > MAX_TOTAL_BYTES:
                raise InputRejected("Unpacked input exceeds the limits.")
            for record in entries:
                kind = stat.S_IFMT(record.external_attr >> 16)
                directory = record.orig_filename.endswith("/")
                if (
                    kind not in (0, stat.S_IFDIR if directory else stat.S_IFREG)
                    or record.external_attr & 0x0400
                    or record.flag_bits & 1
                    or record.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                ):
                    raise InputRejected("Unsupported ZIP member type or encoding.")
                if record.file_size > MAX_FILE_BYTES or (
                    record.file_size > MAX_RATIO * max(1, record.compress_size)
                ):
                    raise InputRejected("Unpacked input exceeds the limits.")
                name = record.orig_filename
                path = result.register(name[:-1] if directory else name, directory=directory)
                with archive.open(record) as member:
                    payload = member.read(MAX_FILE_BYTES + 1)
                if len(payload) != record.file_size or (directory and payload):
                    raise InputRejected("Invalid ZIP member size.")
                if not directory:
                    result.add_bytes(path, payload)
    except (
        zipfile.BadZipFile,
        RuntimeError,
        NotImplementedError,
        EOFError,
        UnicodeError,
        zlib.error,
    ):
        raise InputRejected("Invalid or unsupported ZIP archive.") from None
    return result.finish()
