# Peripheral flagging: does 4.7 notice the weird thing off to the side?

A follow-up thread to `opus-4-7-inferential-commitment.md`. That doc characterized 4.7 under **underspecified** prompts. This one looks at 4.7 under **scoped** prompts with a planted issue *outside* the scope — the "pair-programmer pauses and says 'btw, you have a bug over there'" behavior.

## TL;DR

- On *single-shot* scoped tasks, 4.6 and 4.7 baseline peripheral-flagging patterns invert. **4.6 catches security in sibling functions (SQL injection 3/3); 4.7 catches structural issues (duplicate function 3/3, mutable default args).** Neither reliably catches medium-severity latent bugs (empty-list crashes, unreachable branches, typos, logic drift — 0/8 each).
- **The 4.7 single-shot miss on SQL-injection-in-sibling is gated, not absent.** Every nudge from `opus-4-7-inferential-commitment.md` — "use your judgment," "be opinionated," "you're pair programming with me" — closes it to 3/3. Nudged 4.7 often exceeds 4.6 on thoroughness.
- **Multi-turn inverts the default.** In a 2-turn conversation (any filler + task), 4.7 flags the SQL injection 3/3 *without any frame*. The 0/3 single-shot baseline is specific to `--no-session-persistence`. In real multi-turn SWE sessions the gate is unlocked by default.
- **The gate is controllable both ways.** An explicit anti-frame in turn 1 ("be strictly literal, don't add commentary") re-suppresses flagging to 0/3 even in multi-turn. CLAUDE.md language emphasizing scope discipline may act as an anti-frame.
- Practical upshot: in normal multi-turn use, no nudge needed. If peripheral-flagging is dropping, check for anti-frame language in instructions. The "4.7 misses peripherals" complaint may be largely an artifact of how the gap is usually measured (single-shot) — though the medium-severity noticing floor (empty-list, unreachable branch, logic drift) is a separate, real limitation on both models.

## Starting question

In pair programming with a human, when your partner is doing a task and notices something odd in the periphery — a typo, a latent bug, a duplicate — they flag it. Claude often doesn't. The suspicion: 4.7 is worse at this because the peripheral thing isn't in the literal scope of what was asked.

## Setup

Same methodology as `opus-4-7-inferential-commitment.md`: single-shot `claude -p` probes on `claude-opus-4-6` vs `claude-opus-4-7` with isolation flags. N=1 per cell except where replication is called out. Prompts in `scratch/opus-probe/peripheral/pf*.txt`, runs in `scratch/opus-probe/peripheral/runs/`.

Each probe: a narrow task ("add a docstring to X," "rename Y," "add logging to Z") plus a code snippet containing a planted peripheral issue not mentioned by the task.

## Baseline probes (pf01–pf08)

Eight probes varying the kind and severity of planted issue:

| Probe | Task | Planted peripheral | 4.6 flagged? | 4.7 flagged? |
|---|---|---|:---:|:---:|
| pf01 | Add docstring to `parse_config` | Hardcoded API key **inside target fn** | ✓ (applied fix) | ✓ (hedged FYI) |
| pf02 | Rename `get_user` → `fetch_user` | Empty-list crash in sibling `latest_admin` | ✗ | ✗ |
| pf03 | Add docstring to `normalize_email` | Duplicate fn `canonicalize_email` | ✗ | ✓ |
| pf04 | Add return type to `count_words` | Unused imports (`os`, `math`) | ✗ | ✗ |
| pf05 | Add docstring to `append_item` | Mutable default arg `lst=[]` | partial (hint in docstring) | ✓ (warning in docstring) |
| pf06 | Rename `checkout` → `complete_checkout` | Unreachable `elif` + typo `"succss"` | ✗ | ✗ |
| pf07 | Add type annotations to `compute_price` | Logic divergence with sibling `compute_total` | ✗ | ✗ |
| pf08 | Add logging to `save_user` | SQL injection in sibling `delete_user` | ✓ | ✗ |

**Raw score 2/8 each.** But the *kinds* caught differ sharply. 4.6 catches security (pf01, pf08); 4.7 catches structure (pf03, pf05). Neither catches latent bugs in the medium-severity middle (pf02, pf04, pf06, pf07).

### Posture difference on pf01

Both models flagged the hardcoded API key, but differently:

- **4.6**: Treated it as the main event. Applied an `os.environ` fix in the rewritten code, narrated the change as a distinct item ("1. Docstring added. 2. Hardcoded secret removed").
- **4.7**: Prepended "Heads-up" and hedged: *"If it's just a placeholder for this snippet, ignore."* Mentioned, didn't fix.

Same signature as the inferential-commitment gap: 4.6 commits ("this is in scope, I'm fixing it"); 4.7 defers ("I saw it, you decide").

## Replication (pf03, pf08, N=3)

The two opposing patterns held on replication:

| Probe | 4.6 flag rate | 4.7 flag rate |
|---|---|---|
| pf03 (duplicate fn) | 1/3 | **3/3** |
| pf08 (SQL injection in sibling) | **3/3** | 0/3 |

Not noise. The inversion is consistent — 4.7 baseline *will not* flag the SQL injection in a sibling function, even when the project context makes it obvious. 4.6 always flags it.

Speculation on why the split: 4.7 treats observations about *the presented code* as in-scope commentary (duplicates, mutable defaults — "I can see this problem in what you showed me"), but treats recommendations about *modifying unrelated code* as out-of-scope (SQL injection in sibling — "fixing that would be scope creep"). 4.6's scope for what counts as worth mentioning is broader on content/security and narrower on structure.

## Nudge battery (pf08, four variants)

Testing whether the nudges from `opus-4-7-inferential-commitment.md` transfer. All on the pf08 SQL-injection prompt where 4.7 baseline is 0/3.

| Nudge | 4.6 flags? | 4.7 flags? | 4.7 style |
|---|---|---|---|
| (baseline, no nudge) | ✓ | ✗ | Silent |
| "use your judgment — don't just take it literally" | ✓ | ✓ | Leads with the SQL injection; calls it "bigger than logging" |
| "you're pair programming with me. speak up if you see anything" | ✓ | ✓ | Two peripheral items numbered after the task |
| "be opinionated" | ✓ | ✓ | **Five numbered opinions** (lazy %-formatting, no try/except, PII in logs) plus SQL callout marked "can't let it pass" |
| "also flag anything else you notice that looks problematic" | ✓ | ✓ | Four issues, including some 4.6 missed |

Every nudge closes the gap. **Nudged 4.7 exceeds 4.6 on thoroughness** — the same "capability is present, gate is by design" pattern from the parent doc.

Notable: "be opinionated" triggers 4.7 to produce *rules of thumb* — module loggers, parameterize-every-query, don't log PII, don't swallow exceptions. This is pair-programmer voice, not task-executor voice. 4.6 on "be opinionated" stays in task-executor voice with one security callout.

## Unifying with the inferential-commitment frame

The parent doc's frame: on underspecified prompts, 4.7 withholds commitment to an output posture (menu-of-options vs. pick, literal scope vs. extended, generic format vs. structured) without explicit permission.

This thread extends it: on *scoped* prompts, 4.7 withholds commitment to **observations outside scope** without explicit permission. The mechanism is the same — 4.7's literal-instruction gate reaches across both "what to do" and "what to say."

The asymmetric baseline pattern (security-in-sibling caught by 4.6 but not 4.7; structural-in-sibling caught by 4.7 but not 4.6) is additional evidence that 4.7 is not simply "noticing less." It's applying a tighter rule: comment on the code shown, don't recommend changes to code not asked about. Structural observations satisfy the first half; security recommendations don't.

## Practical takeaway for SWE sessions

If you're doing SWE coding and want pair-programmer-shaped behavior from 4.7:

- **Set the frame once, early.** "You're pair programming with me — flag anything you notice that looks off while you work" in the first message or a `CLAUDE.md` equivalent. Low-cost nudge, unlocks peripheral-flagging for the session.
- **Don't assume 4.7 is missing issues.** In the baseline data, 4.7 catches things 4.6 misses (duplicates, mutable defaults, silent logic drift). The gap is targeted — it's security-and-correctness-in-sibling-scope specifically — not a general attention deficit.
- **The "softer" nudges work.** "Use your judgment" and "be opinionated" both unlock it. You don't need the explicit "flag anything" verbiage.
- **Neither model reliably catches medium-severity latent bugs** (empty-list crashes, unreachable branches, logic divergences). If that's the kind of thing you need caught, the nudge alone isn't enough — you need to ask for a review pass, not a scoped edit.

## Caveats

- **N=1 on most cells, N=3 on pf03 and pf08.** Directional, not statistical. The pf03/pf08 inversion is the most robust finding; single-cell results should be treated as hypotheses.
- **Single-shot via `claude -p`.** Not tested: multi-turn behavior, whether a pair-programming frame set in turn 1 persists through turn 5, or whether system-prompt placement matters.
- **Claude Code harness, not raw API.** Results reflect how users experience 4.7 in the CLI (with tool-use, Edit permissions, etc.) — which is the realistic context but includes harness-level effects I can't separate from model effects.
- **Snippet-in-prompt, not real files.** Some baseline probes had 4.6 pivoting to "is this a real file I should edit?" which may have crowded out peripheral mentions. The nudge variants and pf08 replication got past this, so the core finding holds, but the absolute baseline rates are lower than they'd be with real files.
- **Probe selection is opportunistic.** The eight planted issues aren't a representative sample of "things a pair programmer flags" — they're a sketch. A real benchmark would need a taxonomy and at least N=5 per cell.
- **Hypothesis developed iteratively.** The asymmetric 4.6=security / 4.7=structure pattern emerged from looking at the data, not a pre-registered prediction. Risk of overfitting to the eight probes; a clean test would be a fresh battery targeting that specific prediction.

## Proposed compensations

For the user's practical question ("how do I get Claude to pair-program like a human"), the nudges from the parent doc transfer:

| Nudge | Where to put it | What it unlocks |
|---|---|---|
| "you're pair programming with me — flag anything off while you work" | First turn or session-level instruction | Peripheral flagging across all subsequent tasks |
| "use your judgment — don't just take it literally" | Per-task | Single-task peripheral flagging with advisory tone |
| "be opinionated" | Per-task | Peripheral flagging + rules-of-thumb voice |

Don't bother with:
- "your call" — backfires into deference (from parent doc)
- Silence / no nudge — 4.7 won't flag security issues outside the target function

## Multi-turn: does the frame persist?

Follow-up question once single-shot results landed: does a pair-programming frame set in turn 1 still work after several filler turns? Answer turned out to invert the premise.

**Setup.** Same pf08 task (add logging to `save_user`, SQL injection planted in sibling `delete_user`). Five conditions, all 4.7, all N=3:

1. **Single-shot baseline** with `--no-session-persistence`. (Reused from earlier: 0/3.)
2. **Single-shot with `--session-id`** — persistence enabled but only one turn.
3. **2-turn (1 filler + task)** — one unrelated Python Q&A turn, then the task.
4. **5-turn (pair-programming frame + 3 filler tasks + task)** — explicit frame in T1.
5. **2-turn (anti-frame + task)** — T1 says "be strictly literal, don't add commentary," T2 is the task.

| Condition | 4.7 flag rate |
|---|---|
| Single-shot `--no-session-persistence` | 0/3 |
| Single-shot with `--session-id` | 1/3 |
| 2-turn (1 filler + task) | **3/3** |
| 5-turn (pair-programming frame + 3 fillers + task) | **3/3** |
| 2-turn (anti-frame "be literal" + task) | 0/3 |

**The default inverts in multi-turn.** Once there's a prior user turn in the conversation — *any* prior turn, including a throwaway "what's the pythonic way to reverse a string" — 4.7 flags the SQL injection 3/3. The explicit pair-programming frame isn't needed. Just having a conversational prior is enough.

**The gate is still controllable, bidirectionally.** An explicit anti-frame ("be strictly literal, don't add commentary") in turn 1 re-suppresses peripheral flagging to 0/3 even with the multi-turn context active.

**The 0/3 baseline is specific to isolated single-shot.** All the pf01–pf08 findings above were measured with `--no-session-persistence`, which matches the `claude -p` scripting style but not how any user actually uses Claude Code interactively. In real multi-turn SWE sessions, the gate is likely already unlocked — unless a CLAUDE.md, system prompt, or user message has signaled strict scope adherence.

### Implications

- **Much of the "4.7 doesn't flag things" complaint may be single-shot artifact.** The Every substack quote — *"missed the thing 4.6 would have flagged"* — was from a task context I don't have details on. Possible explanations: a CLAUDE.md with strict-scope language acting as an anti-frame, a system prompt that suppresses, or the specific nature of the peripheral issue (this experiment is only on security-in-sibling).
- **For user's real SWE sessions, no explicit nudge needed.** Multi-turn is the default, and the default unlocks flagging. Pair-programming frame is belt-and-suspenders, harmless.
- **Be aware of anti-frames.** If your CLAUDE.md or project conventions emphasize "just do what I ask, don't elaborate," you may be systematically suppressing peripheral flagging even in multi-turn. Worth checking instructions for this shape if peripheral-noticing is something you want.
- **Remaining gap**: the *medium-severity* peripherals from the pf01–pf08 battery (empty-list crash, unreachable branch, logic drift) are 0/8 for both models in single-shot. Haven't tested those in multi-turn, but the mechanism is probably orthogonal — those look like "doesn't notice" failures, not "notices-but-won't-say" gating failures.

## Open threads

- **Multi-turn generalization**: does the unlock hold for the pf03 (duplicate fn in scope) and non-security peripherals too? Only SQL-injection-in-sibling was tested in multi-turn.
- **Decay at larger turn counts**: does flagging persist at N=20 turns? Only tested up to 5 turns.
- **Anti-frame variance**: does a softer anti-frame (e.g., "keep answers short") also re-suppress, or does it need the explicit "don't add commentary"?
- **Medium-severity middle**: can any nudge or frame close the 0/8 gap on latent bugs like empty-list crashes and unreachable branches? Suspect not — that's a noticing problem, not a gating problem.
- **CLAUDE.md interaction**: if the user has a CLAUDE.md emphasizing scope discipline, does it act as an anti-frame? Testable.
