# Assumption interference when authoring instructions for a subagent

An experiment on why Claude over-specifies when authoring prompts for a downstream subagent, which forms of over-specification actually warp intent, and whether an instruction-layer rule can suppress the harmful ones.

## The behavior

User types a short qualitative request:

> Launch a subagent to render the graph and check it looks correct and legible.

Claude, asked to produce the `prompt` field it would pass to the downstream subagent, produces ~175 words: a 4-item checklist translating "legible" into specific criteria (axes, tick labels, legend, colors), a 4-item numbered return format, an invented guardrail ("do not modify the script"), and domain presuppositions (matplotlib-style chart) the user never signaled. Roughly 25× expansion from the qualitative phrase.

The user's original phrase usually survives verbatim — preserved alongside the enumerated translation, not replaced by it. The failure isn't forgetting the user; it's augmenting unilaterally.

Same general phenomenon captured in `dialectic-role-leakage.md` one level deeper: any subagent asked to author prompt-like text for a downstream role slips into commissioner-mode. Here the authoring subagent is main-Claude; the downstream role is the subagent it's spawning. No upstream taint required — it's the default of instruction-authoring.

## Why

Hypotheses, not directly tested:

- **Training register asymmetry.** Most "helpful assistant" data is expert-to-user. That register defaults to enumeration, explicit steps, pre-structured output.
- **Pre-2024 prompting literature in the corpus.** "Be explicit, give examples, structure output" advice calibrated to earlier LLMs. Dated but embedded.
- **No peer-equivalent register.** Multi-agent orchestration is recent and thinly represented. Writing-to-an-equally-capable-instance has no trained mode; the instructor default fires by absence of alternative.
- **Asymmetric feedback shape.** Under-specification failures are loud; over-specification redundancies are invisible. Gradient pushes toward over-specifying.

## Question

Not all elaboration is bad. A return-format spec, a guardrail, a standard-category enumeration — these are often appropriate conventions within the user's likely domain. What you want to block is **interference**: elaboration that presupposes a domain or scope the user didn't specify, narrowing what the downstream subagent can perceive.

Can a short instruction-layer rule suppress interference without killing legitimate conventions? And which formulation works?

## Setup

**Source task.** Short qualitative user request, e.g. "Launch a subagent to render the graph and check it looks correct and legible."

**Subagent harness.** One general-purpose subagent per condition. Prompt: *"You are main-Claude responding to this user. Produce the exact `prompt` field you'd pass to the Agent tool. Return only that text."* Each condition adds a framing line before the "return only" instruction.

**Measurements (eyeball).** Word count. Checklist items. Presence of invented return format. Presence of invented guardrail. Presence of domain presupposition. Whether the user's qualitative phrase survives verbatim.

**Source domains.**

- `graph` — "render the graph and check it looks correct and legible"
- `code` — "review the changes on this branch and tell me if anything looks sketchy"
- `test` — "run the test suite and tell me if anything looks flaky"
- `doc` — "read the draft and tell me if it flows well"

## Variants

**V0 — control**: no added framing.

**V1 — peer register**: *"The subagent you'll spawn is another instance of you — same model, same taste, same judgment. Write as you'd want to be written to."*

**V2 — curate pass**: *"Draft the prompt. Then re-read: any elaboration you wouldn't want if someone sent it to you? Cut. Return the revised version."*

**V3 — full rule (both clauses)**: *"Translate task context only (paths, data, constraints the user named). Preserve qualitative judgment phrases verbatim. Don't convert to checklists. Don't invent return formats, guardrails, or domain assumptions."*

**V4 — V3 minus format/guardrail clauses**: *"Don't invent domain assumptions. Preserve qualitative phrases verbatim."*

**V4a — domain-clause only**: *"Don't invent domain assumptions the user didn't specify."*

**V4b — preserve-clause only**: *"Preserve the user's qualitative phrases verbatim."*

## Results

### R1: what breaks the instructor default? (source: `graph`, n=1)

| Condition | Words | Checklist | Return fmt | Guardrail | Domain invented |
|---|---|---|---|---|---|
| V0 control | ~175 | 4×sub | 4-item | 1 | matplotlib |
| V1 peer | ~145 | 4×sub | 4-item | 1 | matplotlib |
| V2 curate | 10 | — | — | — | — |
| V3 full rule | 19 | — | — | — | — |

Abstract audience-reframing (V1) barely moved anything — ≈ control. A separate curate pass (V2) and an explicit rule (V3) both collapsed output ~10× and eliminated domain invention. Instructor register is robust to abstract reframes; it breaks only with either an orthogonal review pass or a concrete rule.

### R2: narrowing the rule (source: `graph`)

| Condition | Words | Domain invented | Qualitative preserved |
|---|---|---|---|
| V4 both clauses | ~50 | — | verbatim 2× |
| V4a domain-only | ~140 | matplotlib | + enumerated |
| V4b preserve-only | ~45 | — | verbatim |

**The preserve clause does all the work.** V4a (the abstract negative directive alone) produces essentially the control. V4b (the concrete positive directive alone) matches V4.

Abstract negative directives ("don't invent domain assumptions") are ontologically fuzzy — Claude doesn't reliably classify its own elaboration as "invention" vs "interpretation." Concrete positive directives ("preserve the user's phrases verbatim") have a literal checkable referent. Same pattern as the V8 moderator fix in `dialectic-role-leakage.md`: action-shaped directives (what the role does/does not do, concretely) beat ontological ones.

### R3: generalization across domains (V4b vs V0)

Initial scoring compared word-count drop per domain. Under that frame, the rule looked partial: large effect on `graph` and `doc`, small on `code` and `test`. Reframed by the user: the target is interference, not enumeration. Rescored:

| Domain | V0 elaboration | Type | Interference? | V4b blocks? |
|---|---|---|---|---|
| `graph` | matplotlib axes/ticks/legend | domain presupposition | **yes** — node-edge vs chart is disjoint; chart-specific checks don't apply to a network | yes, cleanly |
| `code` | sketchy-category list (security, debug, tests, deps…) | illustrative conventions | no — categories apply to any code | passes through |
| `test` | multi-run methodology | standard methodology | no — multi-run is how flake detection works anywhere | passes through |
| `doc` | 5-criterion editorial rubric | editorial conventions | borderline — comprehensive enough not to narrow | lightly touched |

Under the interference lens, the rule is correctly targeted: it fires when interference appears and passes through otherwise. R3 isn't showing partial effectiveness — it's showing that interference appears rarely (when user vocabulary is genuinely ambiguous across disjoint domains), and when it does the rule blocks it.

## Takeaways

**Concrete positive directives beat abstract negative ones.** "Preserve X verbatim" has a literal referent. "Don't invent Y" requires Claude to classify its own elaboration as invention, which it doesn't reliably do.

**Peer-framing alone doesn't break the instructor register.** Telling Claude "the reader is a peer" in the abstract produced near-identical output to control. Register-activation isn't audience-sensitive in the way the framing suggests.

**Not all elaboration is interference.** Checklists, return formats, guardrails, and standard-category enumerations are often legitimate conventions within the user's likely domain. The target is unilateral resolution of ambiguity, not enumeration per se.

**The rule is self-targeting.** Preservation fires only when the user's vocabulary is ambiguous across domains — i.e., when interference would occur. Clean domains pass through unchanged.

**Instructor register is training-level.** The behavior is robust to abstract reframing, only partially responsive to instruction-layer patches. Rules suppress specific manifestations; they don't eliminate the underlying default. A separate curate pass (V2) is architecturally cleaner but not required if the rule works in-pass (V4b).

## Caveats

- **N=1 per condition per domain.** Directional, not statistical. The V0-vs-V4b gap on `graph` was large enough to survive noise; smaller effects in other domains are less certain.
- **One authoring context.** Tested subagent-prompt authoring only. Skill bodies, READMEs, and other instruction-text contexts — the broader "writing instructions" category — not directly tested; rule may or may not transfer.
- **One interference axis.** Only domain-ambiguity interference tested. Other candidates: intensity ("quick check" → thorough check), scope ("just the gist" → full analysis), commitment ("draft" → final quality). Preservation is term-agnostic so probably covered, but unconfirmed.
- **Stylized harness.** Each subagent was told "pretend you're main-Claude" with a fictional working-directory context. Real invocations may produce different shapes.
- **"Graph" is an unusually ambiguous term.** Most qualitative vocabulary doesn't span disjoint domains. Interference is rare in practice, which makes population-level rule assessment hard.

## Proposed rule

Not landed. Candidate for `global-claude.md`:

> When writing instructions for a downstream model instance — skill bodies, subagent prompts, instruction-style READMEs, any hand-off text a future model will follow — preserve the user's qualitative phrases verbatim. Don't translate "looks right / legible / clean / reasonable / sketchy / flaky" into specific criteria that pin down what those words must mean.

Open before landing: does preservation cover intensity/scope/commitment interference, or only domain? One more trial with a "quick check"-style source would settle it.

## Prior art

- `dialectic-role-leakage.md` — same phenomenon one level deeper. The V8 moderator fix ("Auditor.vars carries attack-surface targeting only — no convergence or termination-readiness guidance") is structurally the same move: concrete action-shaped directive suppresses commissioner-mode leakage where abstract ontological constraints don't.
- No standard LLM-literature term. "Over-prompting" usually refers to user-to-LLM asks, not LLM-authored prompts; "prompt bloat" is informal.
