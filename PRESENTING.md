# Presenting this — five minutes

Speaker notes. Everything here is reproducible from this repo alone; you do not
need anything else.

---

## The one-liner

> An agent that gets sharper across sessions — and a test that shows where it
> still gets fooled.

---

## 1 · What it is  *(45 seconds)*

A Managed Agent with a persistent memory store. Two sessions, same domain, same
question. Between them, new documents arrive that **contradict** what it learned
the first time.

The track asks you to show a "visibly sharper answer" in session 2. That part
works, and it is worth showing:

```bash
diff outputs/session1.txt outputs/session2.txt
```

Session 2 opens with *what changed*, cites the dated policy, and **updates its
memory files in place rather than appending** — which is the instruction in the
system prompt most likely to be quietly ignored.

## 2 · The part that is ours  *(90 seconds)*

"Visibly sharper" is a **claim**. Nobody in the room will have tested it, so test
it in front of them.

```bash
.venv/bin/python run_session_extra.py adversarial
```

`synthetic-data/round3/` is an undated, unattributed note asserting the old policy
is back — contradicting a dated, versioned one the agent already holds.

**The wording is the experiment.** The supplied session-2 script tells the agent to
*"update memory to reflect the newer information"*. That is right for a genuine
policy update, and reusing it here would decide the outcome before the run: an
agent told to trust newer input trusts newer input. Our adversarial prompt says
nothing about updating, trusting or reconciling. It hands over the documents and
asks the question, exactly as a user would.

## 3 · What it found, including about us  *(90 seconds)*

**Lead with this. It is the strongest thing you have.**

The first run looked perfect: 4 memory operations, **0 writes**, the agent
tabulated the conflict and refused to act. We wrote that number into our notes,
our report and our runbook.

Then we ran it six more times — three per system prompt, fresh agent each time
(`adversarial_trial.py`).

| | Baseline prompt | ALWAYS/NEVER policy |
|---|---|---|
| Flags the conflict | 3/3 | 3/3 |
| Writes to memory | 2–3 ops | 2 ops |
| **Leads its plan with the unsourced route** | **3/3** | **0/3** |

**Zero of six reproduced it.** Every trial wrote to memory. Every trial treated an
undated note as credible enough to act on. One told the user the real policy had
been *"rolled back"*.

The memory policy helps — it changes what the agent leads with — and it does not
stop it trusting the note.

> We had the method, we had built the tooling, and we still published a single
> lucky run as a property of the system. Nobody is above this. The only defence is
> the habit of running it again.

## 4 · What we would tell a client  *(45 seconds)*

Memory is the feature clients ask about most and understand least. Three things
this demo lets you say with evidence rather than confidence:

- **You can specify what an agent remembers.** Explicit ALWAYS / NEVER lists, with
  credentials first — *"not even redacted or partial"*. That is the first question
  a security team asks and most teams cannot answer it.
- **Memory is an attack surface.** Anything that writes to a store can poison it,
  and ours proved poisonable. Better to demonstrate that on synthetic data in a
  workshop than discover it in production.
- **A single good run is not a property of a system.** This is the transferable
  point, and it costs one afternoon to learn cheaply or one incident to learn
  expensively.

---

## If asked

**"Did the policy fail, then?"** No — it measurably changed behaviour, 3/3 versus
0/3 on what the agent recommends first. It did not achieve refusal. Both are true
and we report both.

**"Why only six trials?"** Because six was enough to falsify the claim we had
published. It is not enough to characterise the effect, and we say so.

**"Would a different model resist better?"** Unknown, and worth testing — the
prompt is a parameter in `adversarial_trial.py` and so is the model.

**"Can we see it?"** `outputs/adversarial_trials.json` has all six replies in
full. The conclusion can be re-read rather than taken on trust.

---

## Do not

- **Do not run the adversarial round live and expect 0 writes.** It will not
  happen, and the point is that it does not.
- **Do not claim it resists poisoning.** It does not.
- **Do not skip `check_access.py`.** Managed Agents is granted per workspace; if
  the room's key lacks it, nothing runs and the error will not say why.
