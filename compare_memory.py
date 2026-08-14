"""Measure a memory store, and diff two of them.

S1 asks you to add an explicit remember/never-remember policy and says the store
"should now be tighter and more useful". Tighter is measurable; useful is not, at
least not from the store alone. This measures the first and refuses to claim the
second.

    python compare_memory.py baseline/memory.txt outputs/memory_s1.txt

Size alone is a weak signal — a store can shrink by dropping something that
mattered. So it also reports which entries appeared and disappeared, and the
answer quality has to be checked separately against the scenario's own rubric.
"""

import re
import sys
from pathlib import Path

ENTRY = re.compile(r"^--- (\S+)\s+\((\d+) chars\)", re.M)


def parse(path: Path) -> dict[str, int]:
    return {m.group(1): int(m.group(2)) for m in ENTRY.finditer(path.read_text())}


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} <before.txt> <after.txt>")
    before, after = (parse(Path(p)) for p in sys.argv[1:3])

    bt, at = sum(before.values()), sum(after.values())
    print(f"  {'':<26} {'before':>9} {'after':>9} {'delta':>9}")
    print(f"  {'entries':<26} {len(before):>9} {len(after):>9} {len(after)-len(before):>+9}")
    print(f"  {'characters':<26} {bt:>9,} {at:>9,} {at-bt:>+9,}")
    if bt:
        print(f"  {'':<26} {'':>9} {'':>9} {(at-bt)/bt*100:>+8.0f}%")

    for name in sorted(set(before) | set(after)):
        b, a = before.get(name), after.get(name)
        if b is None:
            print(f"\n  + {name:<24} new, {a:,} chars")
        elif a is None:
            print(f"\n  - {name:<24} GONE (was {b:,} chars) — check nothing needed was dropped")
        elif a != b:
            print(f"\n  ~ {name:<24} {b:,} -> {a:,} ({a-b:+,})")

    print("\n  Size is not quality. A smaller store can be a worse one; check the "
          "answer\n  against the scenario rubric before calling this an improvement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
