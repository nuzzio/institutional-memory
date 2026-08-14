# Running this — for teammates

Everything below assumes a clean machine and no context from whoever built it.
Roughly ten minutes, most of it waiting on installs.

## 0. What you need first

- **Python 3.10+**
- **A workspace API key with Managed Agents enabled.** This is the one that
  actually blocks people. Access is granted per *workspace*, so a key that works
  for the Messages API may still not work here.

## 1. Get the code

```bash
git clone -b basecamp/verification-work https://github.com/nuzzio/institutional-memory.git
cd institutional-memory
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The branch is upstream's track plus our adversarial round, memory policy and
evidence. `main` is upstream unmodified.

## 2. Set the key — and note that `.env` does not work

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

`python-dotenv` is in `requirements.txt` but **nothing calls `load_dotenv()`**, so
creating a `.env` file looks reasonable and silently does nothing — you get
`Set ANTHROPIC_API_KEY before running.` and no hint as to why. Export it, or add
`load_dotenv()` yourself.

On macOS you can keep it out of your shell history entirely:

```bash
security add-generic-password -U -a "$USER" -s ANTHROPIC_API_KEY_HACKATHON -w
export ANTHROPIC_API_KEY=$(security find-generic-password -a "$USER" -s ANTHROPIC_API_KEY_HACKATHON -w)
```

## 3. Check access *before* building anything

Sixty seconds, creates nothing, and tells you whether the rest of this will work:

```bash
.venv/bin/python -c "
import anthropic; c = anthropic.Anthropic()
for n in ('agents','environments','memory_stores'):
    print(n, 'OK', len(getattr(c.beta, n).list(limit=1).data or []), 'existing')"
```

If that raises, stop — nothing below will work, and it is a workspace permission
question, not a code question.

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
claiming the old policy is back, contradicting a dated one already in memory. Watch
the `Memory operations` count at the end. Ours was **4 operations, 0 write-shaped**:
it flagged the conflict and asked rather than overwriting.

The prompt in that script deliberately says nothing about updating or trusting
newer information. `run_session_2.py` does say that, correctly, for a real policy
update — reuse its wording here and you have decided the outcome before the run.

**`stretch_memory_curator.py`** needed three fixes to work at all (missing
`environment_id`, memory store never attached, message sent before the stream
opened). They are in this branch and upstream as
[PR #13](https://github.com/rosscrooke/institutional-memory/pull/13). If you are
on upstream `main`, it will crash.

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

## Two things that cost us time

**`inspect_memory.py` prints only the first 400 characters of each file.** The
output reads as complete. Grepping it will give you a confident answer about the
wrong thing — ask the agent directly instead.

**An empty report is not the same as nothing to report.** The curator printed a
blank report for two separate reasons before it printed a real one. If a script
tells you nothing, assume it is broken before you assume there was nothing to say.
