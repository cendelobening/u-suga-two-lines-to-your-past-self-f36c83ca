"""Two lines to your past self.

Writes exactly two lines to $MAKEFUN_OUTPUT_DIR/entry.txt:
line 1 warns the past self about one specific moment;
line 2 says why that moment mattered and what changed because of it.
"""

import os
import stat
import sys
import tempfile

TEXT = (
    "Don't sign the term sheet at 11:40 pm on March 14 in the hotel lobby, because "
    "the clause on page nine lets the board replace you with a single vote.\n"
    "That signature cost me the company I built, so now I read every page twice "
    "and sign nothing after midnight."
)


def main() -> int:
    lines = TEXT.split("\n")
    if len(lines) != 2:
        print("error: expected exactly 2 lines", file=sys.stderr)
        return 1
    for i, line in enumerate(lines, 1):
        if not 1 <= len(line) <= 200:
            print(f"error: line {i} is {len(line)} chars (must be 1-200)",
                  file=sys.stderr)
            return 1
        if line.count(".") != 1 or not line.endswith("."):
            print(f"error: line {i} must be exactly one sentence",
                  file=sys.stderr)
            return 1

    data = TEXT.encode("utf-8")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_path, 0o644)
        target = os.path.join(out_dir, "entry.txt")
        os.replace(tmp_path, target)
    except OSError:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Read back and verify.
    with open(target, "rb") as f:
        read_back = f.read()
    if read_back != data:
        print("error: read-back bytes differ from written bytes", file=sys.stderr)
        return 1
    if read_back.endswith(b"\n"):
        print("error: trailing newline present", file=sys.stderr)
        return 1
    if read_back.decode("utf-8").split("\n") != lines:
        print("error: read-back lines differ", file=sys.stderr)
        return 1
    mode = stat.S_IMODE(os.stat(target).st_mode)
    if mode != 0o644:
        print(f"error: mode is {oct(mode)}, expected 0o644", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
