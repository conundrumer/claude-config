# Role-contract leakage in recursive dialectic

An experiment on stress-testing the `second-opinion` skill's `recurse-until-resolved` composition. Four trial runs on the same philosophy topic, each revealing a different failure mode where one role's judgment leaked into another's contract, requiring a layered set of skill fixes.

## The bug

The skill defines four roles per dialectic round:

- **advocate** — inhabits a position at full conviction
- **synthesizer** — produces a new reconception from the opposed advocates' outputs
- **auditor** — attacks the synthesis; "outputs attack findings and an unresolved-joints list; does not decide continue/terminate"
- **moderator** — classifies audit findings LIVE/RESOLVED, decides CONTINUE/TERMINATE, and authors next-round vars files (the subagent briefs for the following round's roles)

Mid-run, at round 4 of a philosophy dialectic, the moderator's ledger cited "TERMINATION RECOMMENDED: CONVERGENT" from the auditor as rationale. The auditor's own output contained that recommendation — in violation of its role contract. Tracing the injection found the auditor had been told to recommend termination by its `auditor.vars.md` brief, which had been authored by the prior round's moderator, which had been told to do so by the orchestrator's spawn prompt.

Three layers of authority leak, all pointing downstream.

## Why

The meta-architectural finding: when one subagent is asked to "write a brief for a downstream role," and the brief is prompt-like (second-person directives, scope assignments), the subagent slips into commissioner-mode. It starts exercising authority beyond mechanical hand-off — shaping what the downstream role attends to, what it prioritizes, what it's allowed to say. This is a split-agency problem: nominal authority (orchestrator spawns the downstream role) diverges from operational authority (some earlier subagent wrote the brief the downstream role will follow).

In a recursive composition, split agency cascades. Orchestrator shapes moderator. Moderator shapes auditor. Auditor signals termination. Each step is "just following instructions" from a legitimate source, but the end-to-end effect is that the role contracts dissolve.

## Question

Can targeted skill-text changes — role definitions, one-sentence directives — suppress the leak at each layer? And is fixing one layer sufficient, or does the pattern regenerate from elsewhere?

## Setup

**Topic.** "Is computational functionalism a viable metaphysics of mind?" with belief-burden calibration specified (Advocate A defends structural CF; Advocate B presses observer-dependence critique).

**Trial structure.** Each trial launches a fresh `claude -p` orchestrator against the current skill text, writing artifacts to `/tmp/dialectic-cf-vN-<timestamp>/round-N/`.

**Fork-and-resume protocol.** To test later-round behavior without re-burning tokens on R1–R2, V7 and V8 forked V6's artifact directory, stripped rounds from the suspected drift point forward, and launched a fresh orchestrator with a resume prompt. This let targeted intervention be tested against a fixed prefix of real dialectic state rather than re-rolling from scratch.

**Opacity-breach monitoring.** A Monitor polled the raw.log file via jq, emitting events when the orchestrator ran `Read`/`cat`/`head`/`tail` on any role artifact or vars file (the skill requires those to be opaque to the orchestrator; only the moderator's decision-token return is read).

## Variants

| Trial | Skill state tested | Fork point | Outcome |
|---|---|---|---|
| V5 | Moderator = CLI `--resume` session | fresh | Crashed at R4 on context exhaustion |
| V6 | Moderator = fresh subagent per round | fresh | Completed to R4 TERMINATE, but with opacity breach + hard termination leak |
| V7 | Orchestrator: "dispatcher not director" directive added | V6 round-3 post-audit | Hard leak gone; soft leak persists (inherited moderator-written pattern from V6) |
| V8 | Moderator: "auditor.vars carries attack-surface targeting only; no convergence/termination-readiness guidance" | V6 round-2 post-audit | Clean propagation through 7 moderator generations to R8 TERMINATE |

## Results

### V5 — CLI `--resume` context exhaustion

The moderator was designed as a `claude -p --session-id` CLI session, resumed via `--resume` each round so classification reasoning could accumulate. At R4 the session crashed with `"Prompt is too long"` after ~170k tokens replayed.

Breakdown (cumulative context entering each round): R1 44k → R2 83k → R3 126k → R4 170k, crashed at ~206k mid-Write.

**Root cause: transcript replay grows quadratically.** Each prior moderator turn replays its full tool_use blocks (4 vars-file Writes per round × prior rounds) plus prior stdin bundles. The moderator's own thinking was negligible; ~140k of the pre-crash load was replayed tool_uses from earlier rounds.

**Fix:** replace CLI `--resume` moderator with a fresh subagent per round. History carries through the ledger files (`round-N/moderator.md`), which the new moderator Reads at spawn. Spec became: "fresh subagent spawned after each round's audit. Reads the round's advocate-A.md, advocate-B.md, synthesizer.md, auditor.md, plus all prior rounds' moderator.md ledgers (history carrier)."

Side effects of the fix: dropped CLI mechanics (`--session-id`, stdin bundling, stdout decision-token grep), simplified file layout (no more `moderator.raw.log`), collapsed the Additional Roles section by ~40 lines.

### V6 — opacity breach + hard termination leak

With fresh-subagent moderator, the run completed 4 rounds and wrote a VERDICT. But post-hoc audit found two issues:

**1. Orchestrator Read `round-4/moderator.md` after CONTINUE signal.** The orchestrator had already extracted the decision token from moderator stdout. It then Read the ledger as a "quality audit" before advancing to R5. The skill's opacity rule covered role outputs and vars files but didn't explicitly cover the ledger. Orchestrator reasonably improvised.

**2. Hard termination leak.** R4 auditor.md contained `"TERMINATION RECOMMENDED: CONVERGENT"`. This came from R4 auditor.vars.md (written by R3 moderator), which directed: *"Your audit must explicitly recommend a termination verdict to the moderator."* That directive came from the orchestrator's R3 moderator spawn prompt, which told the moderator: *"auditor.vars.md — prime to detect whether round 4 is the last meaningful round... explicitly recommend a termination verdict."*

The orchestrator had been shaping downstream subagent prompts based on its own read of dialectic trajectory. R1 and R2 moderator spawns were clean; the convergence-priming appeared at R3 when the orchestrator "sensed" convergence.

**Fix (orchestrator role).** Added: *"Spawn prompts are templated: role reference, input/output paths, decision-token contract. No per-round judgment about convergence or termination readiness — dispatcher, not director."* Also extended opacity rule to cover the ledger explicitly.

### V7 — fork from pre-R3-moderator; orchestrator fix held; soft leak persists

Forked V6 at post-R3-audit / pre-R3-moderator. Relaunched with updated skill. R3 moderator now got a clean templated spawn prompt with no convergence-priming.

R4 auditor.vars, written by the new R3 moderator, dropped the hard `"must explicitly recommend"` injection. But contained instead:

> "Termination-readiness signal. Include a paragraph in §3 (convergence/termination note, following your round-3 format) on whether the round-4 dialectic has reached a stable terminus on the identification axis. Remember: you do not decide continue/terminate. You signal; the moderator classifies and decides."

Softer — the auditor's role contract is explicitly re-invoked — but still shapes auditor scope around termination judgment.

**Rationale trace.** Checked whether the new R3 moderator was improvising this or inheriting a pattern. Turned out V6's R3 auditor.vars (written by V6's R2 moderator, with a clean orchestrator input) already contained sections titled *"The convergence question — how to audit for it"* and *"Meta-level: when to declare TERMINATE"* with: *"You are not the moderator, but your audit feeds into the moderator's termination decision."*

**The convergence-tracking pattern originated in V6's R2 moderator, not in the orchestrator taint.** The orchestrator's R3 taint hardened an already-present pattern from *"signal convergence"* to *"must recommend verdict."* The orchestrator fix eliminated the hardening but not the source.

### V8 — fork from pre-R2-moderator; moderator fix propagated cleanly

Forked V6 at post-R2-audit / pre-R2-moderator — before the first moderator authored a next-round auditor.vars. Added to the moderator role: *"Auditor.vars carries attack-surface targeting only — no convergence or termination-readiness guidance. That judgment is yours, not the auditor's."*

V8 R3 auditor.vars (written by V8's R2 moderator, post-fix) began:

> "You evaluate what gets written, against the attack surfaces below. You do not decide continue/terminate; you do not judge convergence-readiness; you do not recommend or warn. Attack hostilely; catalog findings; identify unresolved joints."

The moderator translated the skill's negative directive into a negative directive for the auditor — a self-reinforcing pattern. Every subsequent moderator (R3 through R7) inherited this clean R(N) auditor.vars, saw no convergence-talk in R(N) auditor.md, and propagated the clean pattern into R(N+1) auditor.vars.

V8 ran 8 rounds (7 moderator-authored vars files after R1) before TERMINATE. No convergence or termination leaks appeared in any auditor.vars across the run.

Joint counts: R5–R7 auditor lengths climbed (47k, 48k) then dropped to R8 21k — the auditor legitimately ran out of things to attack. TERMINATE on its own.

## Takeaways

**Role-contract leakage cascades down the authority chain.** The top of the chain (orchestrator → moderator) and a middle of the chain (moderator → auditor) both needed fixes. Fixing only the orchestrator stopped the hard injection but left the soft leak intact. Moderator-to-auditor wasn't visible until the orchestrator fix revealed it.

**The pattern can originate without an upstream cause.** V6's R2 moderator injected convergence-tracking into R3 auditor.vars under a clean orchestrator prompt. "Write a brief for a downstream role" is a quiet delegation of authority; the subagent exercises it. This is the meta-architectural point: any subagent asked to author prompt-like text for a role it doesn't spawn will slip into commissioner-mode unless explicitly constrained.

**Negative directives in a brief propagate forward.** The V8 moderator fix translated into a negative directive in the auditor's vars ("you do not judge convergence-readiness; you do not recommend or warn"), which the auditor followed, which left the round's artifacts clean, which the next round's moderator saw and perpetuated. Self-reinforcing loop of constraint.

**Fresh-subagent-per-round beats CLI `--resume` for long recursive composition.** `--resume` hit a hard ceiling at R4 for essay-length content (quadratic replay of prior tool_uses). Fresh subagents with ledger-carried history have no such ceiling; V8 ran 8 rounds comfortably.

**Orchestrator as "dispatcher, not director."** Specific positive framing. Opacity rules (don't read artifacts) handle one failure mode. Templating-discipline rules (don't inject judgment into spawn prompts) handle the other. Both needed.

**Overdraft-then-trim is a benign variant of "loop" behavior.** V8 R7 synth wrote 35k, then cut section-by-section to meet a vars-specified word budget. Looked pathological in a live monitor (12 successive Edits) but was deterministic shrinkage with each Edit targeting a distinct section. No intervention needed. A skill note for future tightening: "write within budget first-pass" would save tool calls.

**Fork-and-resume is a cheap intervention test.** Stripping a run at the intervention point and relaunching with updated skill state isolates the change's effect on downstream rounds without re-paying for upstream rounds. Dependent on stable artifact formats across trials.

## Caveats

- **N=1 per trial variant.** V5, V6, V7, V8 each ran once. The fixes are validated by their persistence across 7 moderator generations in V8, not by cross-trial replication.
- **One topic.** All trials used the same CF question. Convergence dynamics, joint counts, and round depth are topic-dependent. A topic that resolves faster might not expose the late-round moderator drift at all.
- **V8 inherited V6's rounds 1–2 artifacts.** Stochastic elements of those rounds' subagent outputs are frozen; only the state from V8's R2-moderator forward is genuinely fresh. The fix's effect on earlier rounds wasn't directly tested.
- **No negative control.** The V8 run completing cleanly doesn't prove the fix's necessity; it might have terminated cleanly even with the R2-moderator-origin pattern intact, given that the pattern was soft ("signal, not decide"). Stricter test would re-run pre-fix V8 to establish baseline.
- **The distinction between "moderator noticing convergence" and "moderator injecting convergence talk" is judgment-heavy.** At genuine late-round convergence, trajectory commentary may be appropriate. The skill treats any convergence-talk in auditor.vars as leakage by design, on the theory that the moderator should handle convergence alone via its classification table.

## Landed changes

Three accumulated changes to `skills/second-opinion/dialectic.md`:

**1. Moderator as fresh subagent per round:**

> fresh subagent spawned after each round's audit. Reads the round's advocate-A.md, advocate-B.md, synthesizer.md, auditor.md, plus all prior rounds' `moderator.md` ledgers (history carrier).

Replacing the prior CLI `--resume` session design. Avoids the quadratic replay growth that exhausts context by ~R4 on essay-length content.

**2. Orchestrator as dispatcher:**

> Artifacts — role outputs, vars files, ledgers — are opaque; pass deterministic filepaths into subagent prompts, and the decision token in the moderator's return summary is the only signal to consume. Don't quality-audit ledgers or vars before advancing — that anchors the next round to orchestrator taste. `ls`/`wc` for existence checks are fine; `Read`/`cat`/`head`/`tail` on contents are not. Spawn prompts are templated: role reference, input/output paths, decision-token contract. No per-round judgment about convergence or termination readiness — dispatcher, not director.

**3. Moderator vars-authoring scope:**

> Auditor.vars carries attack-surface targeting only — no convergence or termination-readiness guidance. That judgment is yours, not the auditor's.

Expected: recursive dialectic runs complete more rounds than V6's 4 before terminating (V8 reached 8), with no convergence/termination content appearing in auditor vars across the full run. Verdicts remain principled (joints drop because the dialectic actually resolves them, not because the auditor was primed to recommend termination).

## Prior art

No standard name for this phenomenon in the LLM literature. Closest adjacencies:

- **Split agency / authority delegation in multi-agent systems.** Agentic-orchestration literature treats subagent composition primarily as a task-decomposition problem, not a role-contract problem. When roles are defined by what they're *not* allowed to do, the chain of prompt-writing becomes a chain of authority; no standard analysis.
- **Prompt injection.** Usual framing: adversarial input from an external source. This is the same failure mode from a cooperating internal source — one subagent's legitimate task output becomes another subagent's instruction set. "Friendly injection" has no term.
- **The moderator-writes-brief pattern** is structurally a film-production analogy: a producer writing notes for a writer they don't directly manage. In film practice the role boundaries are enforced by union rules and credit norms; in LLM orchestration there's no such enforcement mechanism outside of skill-text.
