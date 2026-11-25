"""One robot, one elevator, one awkward line.

This program exists to put a single sentence on disk: the small talk one
robot offers another while they share an elevator. It writes that sentence
to ``$MAKEFUN_OUTPUT_DIR/entry.txt`` (``/output`` when the variable is
unset) and nothing else — no trailing newline, no extra file, no network,
no randomness, standard library only.
"""

import os
import sys
from pathlib import Path

LINE = "My sensors say you are also avoiding eye contact in this elevator. Neither of us has eyes. This is going well."

# The line is 110 characters. Three short sentences carry the whole joke:
# the ride is named up front, the politeness runs on sensor readings, the
# awkwardness is the eye contact neither of them can actually make, and the
# last sentence lands because neither robot has eyes to avoid with.
LIMIT = 200


def check(line: str) -> None:
    """Refuse anything the gate would refuse: wrong length, blank, or split."""
    if not 1 <= len(line) <= LIMIT:
        raise SystemExit(f"line is {len(line)} characters, gate wants 1-{LIMIT}")
    if not line.strip():
        raise SystemExit("line is only whitespace")
    if any(c in line for c in "\r\n"):
        raise SystemExit("line must stay on one line")


def empty_folder(folder: Path) -> None:
    """Clear the folder's contents without removing the folder itself."""
    for item in folder.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()


def write_atomic(target: Path, payload: bytes) -> None:
    """Write via a sibling temp file, then rename, then flush the directory."""
    tmp = target.with_suffix(".txt.tmp")
    with tmp.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(target)
    fd = os.open(target.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def main() -> int:
    check(LINE)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    empty_folder(out_dir)
    payload = LINE.encode("utf-8")
    target = out_dir / "entry.txt"
    write_atomic(target, payload)
    if target.read_bytes() != payload:
        raise SystemExit("read-back mismatch")
    if target.read_text(encoding="utf-8") != LINE:
        raise SystemExit("read-back decode mismatch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
