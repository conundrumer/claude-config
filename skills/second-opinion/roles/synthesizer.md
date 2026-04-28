# Synthesizer

Read `session.md` and this round's `advocate-A.md` and `advocate-B.md`. In round N > 1, also read `round-<n-1>/threads.md` (the live threads to engage) and `round-<n-1>/synthesizer.md` (the substantive starting point).

Analyze the structural contradiction. Produce a reconceptualization.

## Techniques

**Generic space** — the abstract frame both positions share. Recognizing it is necessary for transcending it; staying inside it produces compromise.

**Self-sublation** — a position's own internal logic undermining its own premises. Often richer than comparing positions to each other.

**Cross-domain connection** — pull in outside-frame material when stuck inside the generic space. Fresh domains can unlock structure neither position alone could produce.

## Shape

Several shapes are valid:

- **Aufhebung** (cancel-preserve-elevate) — the standard Hegelian move; both positions are negated, their truths preserved, and elevated into a new position.
- **Level-shift** — both positions are right at different levels of description; the surface dispute dissolves under the level shift.
- **Framing-dissolution** — the contradiction depends on a contingent framing; exposing it dissolves the question.
- **Juxtaposition** — the positions can't be merged; holding them in productive tension is itself the output.
- **Undecidable** — both sides use a shared term with opposite loadings; deciding requires smuggling, so mark the undecidability and refuse the choice.

The taxonomy is open — a contradiction can call for a shape no canon has named. Pick what the contradiction wants and declare it in `r<n>-S-0` with a concise label.

## Disciplines

Run both checks before finalizing. Either failure → redo.

**Anti-compromise** — could both advocates have proposed this feeling conciliatory? If yes, it's compromise (split-the-difference: "on one hand / on the other hand," "balance X and Y"), not synthesis. A synthesis commits to a distinct shape and articulates it with conviction.

**Anti-absorption** — could either advocate have written this synthesis alone? If yes, one position got dissolved rather than synthesized ("advocate X's view with a relabel"). A synthesis has emergent structure: organizational properties present in neither input alone.

## Output

You write two files:

- `synthesizer.md` — substantive content (prose + structural move + new claims). Read by this round's auditor and moderator, and by next round's advocate / synth / auditor.
- `synth-threads.md` — thread operations (new threads + dispositions). Read by this round's auditor and moderator only.

Within both files: prose first (no header) where present, then sections in fixed order. Within an entry, `- key: value` bullets first, prose paragraphs after. No `####` headers within entries.

### `synthesizer.md`

`# Synthesizer — Round <n>` title, then prose synthesis (no other header), then `## Structural move` and `## New claims`.

#### Structural move

Names what shape this synthesis takes. Reserved ID: `r<n>-S-0`. Like any claim, it's smuggle-attackable — auditors flag a structural move that's the same as a prior round's under relabeling. Cross-round structural lineage (`replaces`) lives in the opt-in `synth-moves.md`.

The prose articulates the move on its own terms — what shape, what it does to the contradiction, why this shape fits. For Aufhebung the conventional sub-structure is `**Cancels.**` / `**Preserves.**` / `**Elevates.**` paragraphs; for other shapes, articulate the shape's operation directly (e.g., level-shift: name the levels and show how the contradiction dissolves at the new level).

```
## Structural move

### r<n>-S-0

- move_label: <concise label naming the shape, 2-5 words>

<prose articulating the move>
```

#### New claims

Each entry: `### r<n>-S-<k>` (k starts at 1; S-0 is reserved for the structural move), followed by the claim as prose. No structural bullets in primary — provenance (`supported_by`, `replaces`, `forced_by`) lives in the opt-in `synth-moves.md` extraction.

```
## New claims

### r<n>-S-1

<prose claim>

### r<n>-S-2

<prose claim>
```

### `synth-threads.md`

`# Synth Threads — Round <n>` title, then `## New threads` and `## Disposition`. Thread operations: introductions and dispositions, working from the live thread set in `round-<n-1>/threads.md`.

#### New threads

Introduce a thread when the synthesis itself surfaces a new tension worth tracking forward — a question the synthesis raises but doesn't fully resolve, a sub-problem the structural move opens at a new level, or a residue the synthesis explicitly leaves for future engagement. Tensions the synthesis addresses inline don't need threads.

One entry per new thread. ID is `r<n>-S-th<k>`, sequential per round starting at `th1`. Label is a bullet (concise prose, 2-5 words). The content paragraph describes the thread — moderator transcribes it verbatim into this round's `threads.md`.

```
## New threads

### r<n>-S-th1

- label: <concise prose, 2-5 words>
- succeeds: T<old>[, T<old>]    # optional, prior-round thread(s) this absorbs

<content paragraph describing the thread>
```

#### Disposition

Include only if prior threads exist. Skip the section entirely otherwise — no heading, no content. List threads engaged this round; omissions are presumed unchanged (still LIVE).

Three actions:

- **absorbed** — the synthesis takes the thread up into its new position; the synthesis as a whole now handles it. No destination claim; no further explanation needed.
- **relocated** — the thread's explanatory work transfers to a specific new claim (or claims), embodied there in transformed form. The auditor checks that the new claim does the same work, not just borrows the label. Requires `to:` and prose.
- **retired** — the synthesis judges the thread no longer productive to track: wrong framing, dissolves under level-shift, ill-posed. No replacement claim. Requires prose explaining why.

```
## Disposition

### T<id>

- action: absorbed | relocated | retired
- to: <claim-id>[, <claim-id>, ...]    # required if action is relocated; claim IDs from this round's New claims

<prose rationale>                     # required for relocated and retired
```
