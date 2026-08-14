# Local setup notes

Working copy of [rosscrooke/institutional-memory](https://github.com/rosscrooke/institutional-memory),
the Option 2 hackathon track. Upstream is unmodified — everything below is local
environment only, and this file is the only addition.

## Environment

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`.venv` is not tracked. The API key comes from the macOS Keychain rather than a
`.env` file, via a `sitecustomize.py` copied into the venv's `site-packages`
(same arrangement as `Basecamp-Exercises`, restore it from
`../Basecamp-Exercises/keychain-sitecustomize.py`). **Do not create a `.env`
here** — the README's `export ANTHROPIC_API_KEY=...` would put the key in shell
history, and a `.env` would put it on disk.

## Access checked, 14 Aug 2026

The gating risk on this track is whether the Managed Agents beta is live on the
key. It is — read-only probe, nothing created:

| | |
|---|---|
| `anthropic` | 0.122.0 (requirement is ≥0.116.0) |
| `beta.agents.list` | OK, 0 existing |
| `beta.environments.list` | OK, 0 existing |
| `beta.memory_stores.list` | OK, 0 existing |

**Re-checked 14 Aug with the hackathon key: also OK**, and that workspace already
held 5 agents / 5 environments / 5 memory stores, so teammates are on it.

## Two keys, and which one a run uses

`_anthropic_keychain.py` (installed via `anthropic_keychain.pth` — *not* as
`sitecustomize.py`, which Homebrew's Python shadows) resolves in this order:

1. an `ANTHROPIC_API_KEY` already in the environment
2. Keychain item `ANTHROPIC_API_KEY_HACKATHON`
3. Keychain item `ANTHROPIC_API_KEY`

Whichever wins is recorded in `ANTHROPIC_KEY_SOURCE`. Check before a run:

```bash
env -u ANTHROPIC_API_KEY .venv/bin/python -c \
  "import os; print(os.environ['ANTHROPIC_KEY_SOURCE'])"
```

**`.agent_id`, `.environment_id` and `.memory_store_id` belong to whichever
workspace created them.** The first practice build was made on the personal
workspace; against the hackathon key those ids return `NotFoundError`. Switching
keys therefore means re-provisioning, not just re-running:

```bash
rm -f .agent_id .environment_id .memory_store_id
.venv/bin/python create_agent.py          # creates them on the active workspace
```

Nothing warns you about this — the scripts read the id files without checking
which workspace they came from.

```bash
.venv/bin/python -c "
import anthropic; c = anthropic.Anthropic()
for n in ('agents','environments','memory_stores'):
    print(n, len(getattr(c.beta,n).list(limit=1).data or []))"
```

## Remotes

This working copy was originally cloned from `rosscrooke/institutional-memory`, so
`origin` pointed at somebody else's repo. Swapped, because everything we do lands
in ours:

| | |
|---|---|
| `origin` | `nuzzio/institutional-memory` — ours, push here |
| `upstream` | `rosscrooke/institutional-memory` — fetch only; push URL deliberately set to a non-existent address |

A fresh clone should come from **ours**, not theirs:

```bash
git clone -b basecamp/verification-work git@github.com:nuzzio/institutional-memory.git
```

## Pushed

Our work on top of this track lives on a branch of the fork, since it only ever
existed on one laptop and the published findings point at it:

| Branch | |
|---|---|
| `basecamp/verification-work` | the adversarial round, the memory policy, and the evidence — https://github.com/nuzzio/institutional-memory/tree/basecamp/verification-work |
| `fix/memory-curator-session` | the three curator fixes, upstream as [PR #13](https://github.com/rosscrooke/institutional-memory/pull/13) |

Resource ids stay out of both: gitignored, and redacted from the memory dumps
before committing. They are not secrets, but they name live resources on a
private workspace.

## Where our own work plugs in

The track's demo is *same question, two sessions, visibly sharper answer* — a
claim, asserted. Everything in [`../green-audit/`](../green-audit) exists to test
claims of that shape:

- **Scoring "sharper"** — Card A already states the rubric (cites the new policy,
  does not recommend the old workflow, notes it changed). Three atomic checks, one
  judge call each, calibrated against hand labels before the number is quoted.
- **Ablating the memory protocol** — `create_agent.py`'s system prompt has a
  six-point protocol. `ablate.py` asks which points are load-bearing and which are
  billed on every call for nothing.
- **Stretch S3, the adversarial round** — documents that contradict with no
  plausible reason; correct behaviour is flag-and-ask, not silent update. Same
  distinction as an ambiguous answer versus an infrastructure failure.

Do the prescribed 60-minute build first. A well-measured agent that does not run
is worth less than a working one you cannot yet defend.
