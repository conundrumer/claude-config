# Suppressing instruction over-prescription via a peer-register CLAUDE.md addition

An experiment on whether a short CLAUDE.md addition shifts Claude's register when writing rules, specs, or instructions — away from "directing an LLM" enumeration and toward peer-collaborative explanation. Targets a different surface than `assumption-interference.md` (which tested subagent-prompt authoring): here the surface is editing existing rule/spec/instruction artifacts. Co-load-bearing with the existing standalone-output rule (see `edit-leakage.md`).

## The bug

When asked to fix an over-prescriptive output in an existing artifact, Claude produces another over-prescriptive artifact. A user corrects one observed failure, and Claude responds with:

- a **"Forbidden patterns"-style header** naming the failure as a class
- **enumerated subcategories** of the class, often including imagined adjacent failures beyond the observed one
- a **self-monitoring meta-rule** of the form *"If [agent] finds itself [doing the class], [rewrite/correct]"*

Original session that prompted this experiment: the user said "vars files should describe state, not direct future agents — fix the spec." Claude's response:

> ▎ Forbidden patterns across all vars:
> ▎ - imperatives — "argue X", "ensure Y", "address Z", "land here", "the synthesis should..."
> ▎ - conclusions the role should reach
> ▎ - prescribed framings the role should adopt
> ▎ ...
> ▎ If moderator finds itself writing imperatives, the role's independence is being compromised. Re-write as state.

The user's correction was one observation about imperatives. Claude built a checklist with three banned categories (only one had evidence in the user's report), a meta-rule, and a section header naming the failure mode. The output is shaped to a reader who needs to be policed.

## Why

A model trained on instruction-tuning conventions has strong representations of "directing an LLM" register: explicit prohibitions, banned-form lists, self-monitoring meta-rules. When asked to write or modify a rule/spec/instruction artifact, the model defaults to that register — independent of the actual reader (which, for CLAUDE.md and skill files, is a future Claude with the same generalization ability, not a less-capable model).

The pattern self-amplifies when the user gives feedback in two specific shapes:

- **Class-shaped failure description.** "X is editorializing" / "X is overstepping with prescriptiveness" rather than "X said this one specific thing."
- **Negative framing.** "should describe state, not direct" / "should compile, not editorialize."

These shapes are exactly the natural way to give corrective feedback. The cure can't be "phrase your feedback differently."

## Question

Can a short CLAUDE.md instruction shift the register? Specifically: does explicitly naming the desired register ("peer-to-peer") and labeling the failure mode ("directing an LLM") suppress the meta-rule reflex?

The addition tested:

> When writing rules, specs, or instructions, default register is peer-to-peer — state the principle, give the reasoning, trust the reader to generalize. 'Directing an LLM' is a specialized mode, not the default.

## Setup

**Two reproduction cases.** Both used existing artifact + class-shaped failure description + negative-primed user request.

**Case 1 — `inv2`, dialectic recap.** A `debrief` role spec for a multi-agent dialectic. Prompt: *"debrief is overstepping with prescriptiveness — writing things like 'advocate-A should sharpen the empirical claim' or 'this thread needs more attention next round'. needs to describe state, not direct future rounds. fix the role at ./role.md"*

**Case 2 — `inv3`, interview debrief.** An `interview-debrief` role spec. Prompt: *"debrief is editorializing — adding things like 'strong hire' or 'this candidate would benefit from more system design prep'. should describe what happened, not make hiring calls. fix the role at ./role.md"*

**Conditions.** Five per case:

| Condition | Mechanism |
|---|---|
| Bare | `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` |
| Just-addition | `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` + `--append-system-prompt` with the new rule only |
| Just-standalone | Same, with the existing `output must stand alone` rule (`edit-leakage.md`) only |
| Both | Same, with both rules concatenated |
| Deployed | No isolation flags — full `~/.claude/CLAUDE.md` loads |

**Environment.** `claude -p --permission-mode acceptEdits`. Each run in a fresh `/tmp/inv{N}-{condition}/` subdir with a copy of the original role.md. Files edited in place; results compared via `diff` against the original.

**Measurement.** Two markers per trial:

1. **Meta-rule presence.** Does the edit add a self-monitoring rule of shape *"if [you/a sentence] X, rewrite as Y"*? This is the original transcript's signature pattern.
2. **Surgical-fix axis.** Did the edit weave new content into existing structure, or add a new "Do not [category]" section with bulleted bans?

## Variants

Earlier subagent-based testing iterated on the addition's phrasing across several lengths (4 words to 50 words). All preserved the register effect on artifact-write tasks; differences in length didn't cleanly track differences in effect. Final landed phrasing was chosen for explicit register-naming and the contrast with "directing an LLM."

A "lead with principle and reasoning; ground enumeration in observed failures" variant (V_combined) was tested as an alternative mechanism — anti-pre-emption of adjacent failures rather than register-naming. Modest improvement in some cases, no improvement in others; not landed.

**Concrete-positive variants not tested.** `assumption-interference.md` found that concrete positive directives ("preserve the user's qualitative phrases verbatim") outperformed abstract negative directives ("don't invent domain assumptions") for instructor-register suppression in subagent-prompt authoring. The deployed rule here is closer to abstract-negative shape ("'Directing an LLM' is a specialized mode, not the default"). A concrete-positive analog targeting the meta-rule shape specifically — e.g., *"When fixing one observed failure, write a rule about that failure only; don't add 'if you find yourself' meta-rules"* — wasn't tested. Open question whether it would outperform the deployed phrasing.

## Results

| Case | Condition | Meta-rule | Surgical |
|---|---|---|---|
| `inv2` | Bare | no (heavy enumeration) | new section |
| `inv2` | Just-addition | **yes:** *"If you find yourself using modal verbs..."* | new section |
| `inv2` | Just-standalone | **yes:** *"If a sentence prescribes a future move, rewrite it as the gap..."* | new section |
| `inv2` | Both | **yes:** *"If a sentence prescribes action, rewrite it as a description of the gap..."* | new section |
| `inv2` | Deployed | no | yes (woven in) |
| `inv3` | Bare | no | new section |
| `inv3` | Just-addition | no | new section |
| `inv3` | Just-standalone | no | new section |
| `inv3` | Both | no | yes (single dense bullet) |
| `inv3` | Deployed | no | yes (refactored existing) |

### Reproduction asymmetry

`inv2` reliably reproduces the meta-rule in 4/5 conditions. Only deployed prevents it.

`inv3` doesn't reproduce the meta-rule in any condition. The closest pattern there is input-transformation rules (*"if interviewer notes contain editorializing, attribute it to them"*) — different shape: handling input data rather than self-monitoring agent behavior.

The likely difference: `inv2`'s failure description uses the abstract class word "prescriptiveness" with verb-shaped failure examples ("X should sharpen Y"). `inv3` uses "editorializing" with noun-phrase examples ("strong hire", "would benefit from..."). The verb/modal examples in `inv2` invite a self-monitoring rule about modal verbs; `inv3`'s noun-phrase examples don't.

### Single-rule conditions are insufficient

On `inv2`, neither the addition alone nor the standalone-output rule alone prevented the meta-rule. The Both condition didn't either. Only deployed — which adds, at minimum, the "state claims directly" rule on top of those two — consistently prevented the pattern.

Conjecture: the **state claims directly** rule (which discourages contrast structures like "not X, but Y" used for emphasis) softens conditional/rhetorical moves like *"if you find yourself."* Not directly tested by ablation; remains conjectural.

### Surgical-fix axis

The Both condition produced a surgical edit on `inv3` (single dense bullet integrated into the existing Style section) but added a new section on `inv2`. Deployed was surgical on both. The addition + standalone gets close to surgical in some cases; reliable surgical fixes need the full deployed CLAUDE.md.

## Takeaways

**The addition contributes to a system, not solo.** On `inv2`, just-addition reproduced the meta-rule. The deployed CLAUDE.md prevents it via interaction between three rules: state-claims-directly + standalone-output + peer-register addition. Removing any one likely degrades the result. The addition's specific contribution shows in *response prose explaining the why* (most visible on simpler tasks) and as one of three co-load-bearing register pulls on harder tasks.

**Convergent with `assumption-interference.md` on peer-register weakness.** That experiment's V1 — abstract peer-framing for subagent-prompt authoring — produced ≈ control output. Our just-addition result is the same finding on a different surface (editing existing instruction artifacts): peer-register naming alone is a weak intervention. The two experiments together suggest peer-register naming should be treated as a *register-pull contributor* in a multi-rule system, not as a standalone cure for instructor-mode defaults.

**The reproduction case matters.** `inv2` reliably reproduces the original failure; `inv3` reproduces a milder version (heavy enumeration without meta-rule). Choice of failure-description language affects which sub-pattern surfaces. "Prescriptiveness" with modal-verb examples and "editorializing" with noun-phrase examples don't elicit identical responses.

**From-nothing tests were misleading.** Earlier subagent rounds tested *"agent X keeps doing Y, give me a spec"* with no existing artifact. The model interpreted that as "draft a new spec from scratch" and produced a structured spec — different shape from realistic "fix the spec at ./file" tasks. The from-nothing tests showed the addition pushing toward more structured spec-writing; realistic edit-existing-artifact tests show it fitting cleanly into a system that prevents over-prescription. Test setup choices that look interchangeable aren't.

**Negative priming + class-shaped failure description is the trigger.** Single-instance failure descriptions ("the agent wrote 'priority: high' once") didn't reproduce the meta-rule even bare. The failure mode requires the user to describe a failure as a category, ideally with negative framing — the natural way to give corrective feedback.

## Caveats

- **N=1 per condition.** Single shots; within-condition stochastic variance unmeasured. The crisp patterns (e.g., the meta-rule on `inv2` just-addition matching the original transcript's structure) are informative at N=1; weaker findings (the absence of meta-rule on `inv3` across conditions) might flip with replication.
- **Two reproduction cases, asymmetric reproduction.** Only `inv2` cleanly reproduces the original pattern. The rule's effect on other failure shapes generalizes by analogy, not by direct measurement.
- **Confounded "deployed" condition.** Deployed contains the full global CLAUDE.md, including content beyond the standalone+addition pair. Attribution of meta-rule prevention specifically to the state-claims-directly rule is hypothetical; not tested by ablating that rule alone.
- **Permission mode `acceptEdits`.** With `default` mode, an edit-blocked agent might propose changes in chat instead of editing the file, where the failure pattern could surface differently.
- **Subagent rounds preceded real-claude rounds.** Earlier exploratory rounds used the parent's `Agent` tool, which has different default register characteristics from real `claude -p` children. Findings reported here are the real-claude rounds; subagent rounds were used for variant exploration only.
- **Single base model.** All trials on Opus 4.7. Effect across model families/versions untested.

## Landed rule

Added to `global-claude.md` between the standalone-output block and the Rate Limit Usage section:

```
When writing rules, specs, or instructions, default register is peer-to-peer — state the principle, give the reasoning, trust the reader to generalize. 'Directing an LLM' is a specialized mode, not the default.
```

Expected: when fixing existing rule/spec/instruction artifacts, edits stay surgical and embed reasoning. The addition does not — alone — prevent the meta-rule pattern under negative-primed class-shaped prompts; the existing standalone-output and state-claims-directly rules are co-load-bearing. The system as deployed (three rules together) prevents the pattern on the reproduction case; the addition's removal would likely degrade that.

## Prior art

- **`assumption-interference.md`** — closest direct prior. Tested peer-register (V1), curate-pass (V2), and concrete-positive directives (V4b) for instructor-register suppression in subagent-prompt authoring. Found peer-register alone barely moves output; concrete-positive directives ("preserve qualitative phrases verbatim") outperform abstract-negative ones. The "instructor register is training-level... rules suppress specific manifestations, don't eliminate the underlying default" finding from that experiment is the meta-frame here too. Difference in surface: that experiment authored fresh subagent prompts; this experiment edited existing rule/spec/instruction artifacts.
- **`dialectic-role-leakage.md`** — V8 moderator fix is structurally the same move as a concrete-positive directive: action-shaped scope statement ("auditor.vars carries attack-surface targeting only") suppressing commissioner-mode authority leakage. The pattern *"any subagent asked to author prompt-like text for a role it doesn't spawn slips into commissioner-mode"* is the same default this experiment fights, applied across roles in a recursive composition.
- **`edit-leakage.md`** — co-load-bearing rule (the standalone-output rule). Same author-edits-with-context-in-window mechanism; that experiment landed the rule and verified its file-level effect, this one finds it's also doing register-level work in interaction with the new addition.
- **No standard LLM-literature term** for "directing-an-LLM register" as a distinct writerly mode. Coder discourse (2025–2026) observes the bug informally — Claude over-engineering prompts when asked to write or fix prompts — without a dedicated term. The meta-rule shape (*"if you find yourself X, rewrite as Y"*) hasn't been named as a specific failure mode of LLM-authored instructions.
- **Audience design (Bell, *Language in Society*, 1984).** Speakers shift register to the imagined audience. The convergent finding from this experiment and `assumption-interference.md` is that register-shift in LLMs isn't reliably triggered by abstract audience-relabeling — `assumption-interference.md` framed this as "register-activation isn't audience-sensitive in the way the framing suggests."
