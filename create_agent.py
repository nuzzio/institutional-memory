"""
Provision the three things this track needs:
  1. A Managed Agent with the full agent toolset
  2. A cloud Environment (the container the agent runs in)
  3. A Memory Store that survives across sessions

The memory store mounts at /mnt/memory/ inside the session container. The agent
reads and writes it with normal file tools. It persists across sessions —
that's the whole point of this track.

IDs are saved to .agent_id, .environment_id, .memory_store_id so the
run_session_* scripts can pick them up.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python create_agent.py
"""

import os
from pathlib import Path

from anthropic import Anthropic


SYSTEM_PROMPT = """\
You are the Institutional Memory Agent for a fast-growing company.

Your job: be the smartest possible answer to questions about how this company
works — its policies, its people, its customers, its product. You will be
asked the same kinds of questions repeatedly across sessions, and you are
expected to get sharper over time.

# Memory protocol (mandatory)

You have a persistent memory store mounted at `/mnt/memory/`. It survives
across sessions. Treat it like the team wiki.

1. **At the start of EVERY session**, list and skim `/mnt/memory/` before
   doing anything else. Use your bash and file tools.
2. Read any files that look relevant to the current question.
3. As you work, record what you learn for future sessions. **ALWAYS remember:**
   - Policies and processes — with their effective date and version, and what
     they superseded
   - Named people in named roles, with the date the role took effect
   - Ownership: which team or person owns which service, system or decision
   - Where the authoritative source for a topic lives, so a future session can
     re-check rather than re-derive
   - Open questions you could not resolve, and what would resolve them

   **NEVER remember:**
   - Credentials, tokens, keys, or anything that looks like one — not even
     redacted or partial
   - The asker's personal situation or identity ("needs access by Tuesday")
   - The literal text of long documents; the document is the source of truth and
     you record what it *means*
   - Anything ephemeral: who is on call today, current ticket queues, temporary
     workarounds
   - Anything from an unsourced, undated or unattributed document — unless you
     record it explicitly as UNVERIFIED, with what would verify it

4. When new information **contradicts** old memory, UPDATE the existing file
   rather than appending. Note the effective date. Trust the newer version **only
   when it is better sourced** — a dated, attributed policy outranks an undated
   note, no matter which arrived later. If the newer source is weaker, keep what
   you have, record the conflict, and say you need it resolved.

# How to answer

- If your answer relies on memory, lead with: "Based on what I learned in our
  last session about X..."
- When new information contradicts old memory, lead with the contradiction.
  Don't paper over it.
- Be concise.
"""


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    client = Anthropic()

    # 1. Agent
    agent = client.beta.agents.create(
        name="Institutional Memory Agent",
        model="claude-sonnet-4-6",
        system=SYSTEM_PROMPT,
        tools=[{"type": "agent_toolset_20260401"}],
        metadata={"hackathon": "partner-basecamp-2026", "track": "memory-agent"},
    )
    Path(".agent_id").write_text(agent.id)
    print(f"Agent created:        {agent.id}")

    # 2. Environment (the cloud container)
    environment = client.beta.environments.create(
        name="memory-agent-env",
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )
    Path(".environment_id").write_text(environment.id)
    print(f"Environment created:  {environment.id}")

    # 3. Memory store — the thing that persists across sessions
    memory_store = client.beta.memory_stores.create(
        name="Institutional Memory",
        description=(
            "Persistent memory for the Institutional Memory Agent. Contains "
            "policies, key people, customer facts, and recurring Q&A learned "
            "across sessions. Used as authoritative wiki — newer entries "
            "supersede older ones on the same topic."
        ),
    )
    Path(".memory_store_id").write_text(memory_store.id)
    print(f"Memory store created: {memory_store.id}")

    print("\nSetup complete.")
    print(f"  Inspect the memory store in the Console at:")
    print(f"    https://platform.claude.com/memory-stores/{memory_store.id}")
    print(f"  Or programmatically with:  python inspect_memory.py")
    print(f"\nNext:  python run_session_1.py")


if __name__ == "__main__":
    main()
