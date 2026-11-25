"""Two Robots in an Elevator — one line of awkward robot small talk.

Writes exactly one line to $MAKEFUN_OUTPUT_DIR/entry.txt (default /output):
the line one robot says to another while they ride an elevator together,
no trailing newline, nothing else. Deterministic, stdlib only, no network,
no randomness.
"""

import os
import sys

ENTRY = "My sensors say you are also avoiding eye contact in this elevator. Neither of us has eyes. This is going well."

# 110 characters, one line: the elevator is named in the line itself, the
# machine logic ("My sensors say") shows through the politeness, the shared
# avoidance of eye contact is the awkwardness neither robot wants to name,
# and the turn — neither of them has eyes — reframes the whole line on
# first read. The gate counts 1-200 characters, so the line is written with
# no trailing newline: exactly the line, nothing else.
MAX_CHARS = 200


def main() -> int:
    # The gate: UTF-8 text of 1-200 characters, not only whitespace, one line.
    if not (1 <= len(ENTRY) <= MAX_CHARS):
        raise SystemExit("entry length %d outside 1-%d" % (len(ENTRY), MAX_CHARS))
    if not ENTRY.strip():
        raise SystemExit("entry is only whitespace")
    if "\n" in ENTRY or "\r" in ENTRY:
        raise SystemExit("entry must be a single line")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    # Clean only the contents of the output folder, never the folder itself.
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)

    data = ENTRY.encode("utf-8")
    target = os.path.join(out_dir, "entry.txt")
    tmp = target + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, target)
    dir_fd = os.open(out_dir, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)

    # Verify by read-back: exactly the line, nothing else.
    with open(target, "rb") as fh:
        back = fh.read()
    if back != data:
        raise SystemExit("read-back mismatch")
    if back.decode("utf-8") != ENTRY:
        raise SystemExit("read-back decode mismatch")

    return 0


if __name__ == "__main__":
    sys.exit(main())
