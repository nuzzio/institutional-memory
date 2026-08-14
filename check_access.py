"""Check this key can reach Managed Agents, before building anything.

Sixty seconds, creates nothing, and answers the question that otherwise eats the
first quarter of an hour: Managed Agents is granted per *workspace*, so a key that
works fine for the Messages API may still not work here.

A script rather than a `python -c` one-liner on purpose. The one-liner version of
this did not call load_dotenv(), so anyone who put their key in a .env — the other
option the same instructions offer — got "Could not resolve authentication method"
and nothing pointing at the cause.

    python check_access.py
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    import anthropic

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("No ANTHROPIC_API_KEY found.\n"
              "  export ANTHROPIC_API_KEY=sk-ant-...\n"
              "  or put ANTHROPIC_API_KEY=sk-ant-... in a .env file here",
              file=sys.stderr)
        return 2

    client = anthropic.Anthropic()
    failed = False
    for name in ("agents", "environments", "memory_stores"):
        try:
            existing = getattr(client.beta, name).list(limit=1).data or []
            print(f"  {name:<15} OK    ({len(existing)} existing on this workspace)")
        except Exception as exc:
            failed = True
            print(f"  {name:<15} FAIL  {type(exc).__name__}: {str(exc)[:120]}")

    if failed:
        print("\nManaged Agents is not available on this key's workspace. Nothing else\n"
              "in this repo will work — that is a permissions question, not a code one.",
              file=sys.stderr)
        return 1
    print("\nGood to go:  python create_agent.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
