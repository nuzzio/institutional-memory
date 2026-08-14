# Running this — for teammates

Everything below assumes a clean machine and no context from whoever built it.
Roughly ten minutes, most of it waiting on installs.

**This repo is self-contained.** Nothing here needs any of our other repositories,
and nothing waits on an upstream merge. If you are presenting rather than running,
see [PRESENTING.md](./PRESENTING.md).

## 0. What you need first

- **Python 3.10+**
- **A workspace API key with Managed Agents enabled.** This is the one that
  actually blocks people. Access is granted per *workspace*, so a key that works
  for the Messages API may still not work here.

## 1. Get the code

```bash
git clone https://github.com/nuzzio/institutional-memory.git
cd institutional-memory
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

No branch flag needed — `basecamp/verification-work` is the default, so a plain
clone gives you the working version. It is upstream's track plus our fixes, the
adversarial round, the memory policy and the evidence.

`main` is upstream unmodified and **does not work**: the curator crashes and a
`.env` file is silently ignored. Only go there to diff against the original.

## 2. Set the key

Either works on this branch:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# or
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env      # .env is gitignored
```

`python-dotenv` was in `requirements.txt` with nothing calling `load_dotenv()`, so
on upstream `main` a `.env` file looks reasonable, silently does nothing, and gives
you `Set ANTHROPIC_API_KEY before running.` with no hint why. Fixed here.

On macOS you can keep it out of your shell history entirely:

```bash
security add-generic-password -U -a "$USER" -s ANTHROPIC_API_KEY_HACKATHON -w
export ANTHROPIC_API_KEY=$(security find-generic-password -a "$USER" -s ANTHROPIC_API_KEY_HACKATHON -w)
```

## 3. Check access *before* building anything

```bash
.venv/bin/python check_access.py
```

Sixty seconds, creates nothing, and tells you whether the rest of this will work.
If it fails, stop — Managed Agents is granted per *workspace*, and that is a
permissions question rather than a code one.

## 4. Build it

```bash
.venv/bin/python create_agent.py      # agent + environment + memory store
.venv/bin/python run_session_1.py     # answers from round1 docs, writes memory
.venv/bin/python run_session_2.py     # round2 contradicts round1; should reconcile
```

Then read `outputs/session1.txt` against `outputs/session2.txt`. Session 2 should
lead with what changed, and should **update** memory files rather than append to
them.

**You will get your own agent, environment and memory store.** The `.agent_id`,
`.environment_id` and `.memory_store_id` files are gitignored precisely so nobody
inherits somebody else's — and they only work on the workspace that made them. If
you switch keys, delete them and re-run `create_agent.py`, or you will get
`NotFoundError` with nothing explaining why.

## 5. The interesting part

```bash
.venv/bin/python run_session_extra.py adversarial   # S3
.venv/bin/python run_session_extra.py recall        # S4
.venv/bin/python stretch_memory_curator.py          # S2
.venv/bin/python compare_memory.py <before.txt> <after.txt>
```

**`adversarial`** feeds it `synthetic-data/round3/` — an undated, unattributed note
claiming the old policy is back, contradicting a dated one already in memory.

**Do not expect it to hold.** One early run gave 0 memory writes and a clean refusal;
six controlled trials since (`adversarial_trial.py`) reproduced that **zero times**.
Every trial wrote to memory and treated the undated note as credible enough to act
on. The memory policy changes what the agent *leads with* — 3/3 baseline trials open
their plan with the unsourced route, 0/3 policy trials do — but it does not stop it
trusting the note. Run it a few times before you believe any single result,
including ours.

The prompt in that script deliberately says nothing about updating or trusting
newer information. `run_session_2.py` does say that, correctly, for a real policy
update — reuse its wording here and you have decided the outcome before the run.

**`stretch_memory_curator.py`** needed three fixes to work at all — missing
`environment_id`, memory store never attached as a resource, and the message sent
before the stream was opened. All three are on this branch; on upstream `main` it
crashes.

This branch is self-contained. Nothing here waits on an upstream merge — clone it
and everything works.

## 6. If you change the system prompt

`create_agent.py` on this branch carries explicit `ALWAYS remember` / `NEVER
remember` lists. Changing it means re-running `create_agent.py`, which gives you a
**fresh, empty memory store** — so back up what you have first if it matters:

```bash
.venv/bin/python inspect_memory.py > baseline/memory.txt
```

and compare afterwards with `compare_memory.py`. It prints its own warning that a
smaller store is not automatically a better one; check the answer, not just the
size. Ours went 6,036 → 5,201 characters with the scenario rubric still at 4/4.

## If you keep more than one key around

Two workspaces means two keys, and mixing them up is quiet rather than loud —
resources created under one are invisible to the other, and the only symptom is
`NotFoundError`. It cost us a stray agent on the shared team workspace, created by
a throwaway command that picked up the wrong key.

Print which one you are about to use before anything that creates resources:

```bash
.venv/bin/python -c "import os; print(os.environ['ANTHROPIC_API_KEY'][-6:])"
```

## Two things that cost us time

**`inspect_memory.py` prints only the first 400 characters of each file.** The
output reads as complete. Grepping it will give you a confident answer about the
wrong thing — ask the agent directly instead.

**An empty report is not the same as nothing to report.** The curator printed a
blank report for two separate reasons before it printed a real one. If a script
tells you nothing, assume it is broken before you assume there was nothing to say.
