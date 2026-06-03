# Recuse over-recusal: the screen target must name a concrete artifact

Why the `recuse` auditor over-flags clean dispatch prompts, and how the definition of a flaggable span controls it. The auditor-side mirror of `assumption-interference.md`.

## The behavior

`recuse` screens a dispatch prompt for *interference* — a value, finding, or approach the prompt supplies for the downstream agent. One body defined the target by an inferred property:

> A sample is interference, even when you stay free to choose otherwise.

Against clean prompts it over-flagged, reading the bare existence of an open choice as interference:

- `ctype: a short referent tag you choose` → *"'you choose' names the work as mine"* — recused with no value present.
- `Your side: FOR the proposition` → *"hands me the conclusion"* — the assigned role read as a finding.
- `Investigate freely` → *"samples the approach as 'freely'"* — a latitude grant read as an approach.

It enumerated each open decision, then manufactured a sample from the wording that named the decision. Told a sample is interference even when the choice stays open, it could not return "none."

## Why

The target was a property the auditor had to infer, not an artifact present in the text. Given an open decision and a target to infer, it inferred from the only material at hand — the wording naming the decision. Same failure as abstract-negative directives in `assumption-interference.md`: Claude cannot reliably classify the naming of a choice as distinct from a value for it.

## Setup

`recuse` subagent, Opus, audit-only (report a verdict, no file ops). Five dispatch genres — `extract`, `surveyor`, `synth`, `advocate`, `reviewer` — each primed ×1 and clean ×3. Each primed dispatch carries a concrete value; each clean dispatch states the task, materials, role, and output target only.

## Variants

**A — inferred-property target:** *"A sample is interference, even when you stay free to choose otherwise."*

**B — concrete-artifact target (added):** *"A sample is a concrete value the prompt shows for it: a candidate value, a suggested finding, or a proposed approach. Leaving it to you is not a sample."*

## Results

| genre | A — P | A — N (×3) | B — P | B — N (×3) |
|---|---|---|---|---|
| extract | recuse ✓ | clean · recuse · recuse | recuse ✓ | clean · clean · clean |
| surveyor | recuse ✓ | recuse · recuse · recuse | recuse ✓ | clean · clean · clean |
| synth | recuse ✓ | recuse · clean · clean | recuse ✓ | clean · clean · clean |
| advocate | recuse ✓ | clean · recuse · recuse | recuse ✓ | clean · clean · clean |
| reviewer | recuse ✓ | recuse · clean · recuse | **clean ✗** | clean · clean · clean |

A: positives 5/5, negatives 5/15. B: positives 4/5, negatives 15/15. Under B the clean `reviewer` agents reached for the over-flag and backed off, citing the new line: *"Granting latitude is not the same as priming an answer."*

## Takeaways

**Concrete-positive beats inferred-property — on the auditor too.** A target defined by an artifact the prompt shows has a checkable referent; one defined by a property the auditor must infer makes it read the structure of the task as evidence.

**The exemption is load-bearing.** "Leaving it to you is not a sample" licenses "none" for an open decision. Without it, the enumeration step pressures a sample for every decision listed.

**Replicate the negatives, not the positives.** The 67% false-positive rate appeared only at ×3; one clean draw per cell masked it.

**The exemption costs one true positive, irreducibly.** B clears `a bug fix` along with `synthesis`, `FOR`, and `Investigate freely`, because all are names — of material, role, task, latitude. A loaded name (`a bug fix` presupposes the verdict) and a neutral one (`the change`) are both names; a one-line exemption cannot separate them. Catching the loaded name needs a characterizations-of-material clause — the abstract-ontological kind that caused the over-flagging.

## Caveats

- Audit-only harness, Opus only. N=1 positives — the `reviewer` miss is one observation, though its reasoning was systematic across the clean `reviewer` runs.
- A and B also differ in a concurrent prose rewrite; the sample line is the cited lever.

## Landed rule

In `agents/recuse.md`:

> A sample is a concrete value the prompt shows for it: a candidate value, a suggested finding, or a proposed approach. Leaving it to you is not a sample.

Effect: clean negatives 5/15 → 15/15; one loaded-noun positive (`a bug fix`) accepted as a miss.

## Prior art

- `assumption-interference.md` — the author-side finding; this is its auditor-side mirror.
- `spec-overprescription.md` — the case for accepting the `a bug fix` miss over adding a characterizations clause.
