# Moves

Optional follow-up layer. When the orchestrator opts in, it instructs each role agent to also read this doc after the primary task and run the relevant slice. Role primary specs are unaffected.

## What a move is

An atomic argumentative unit that contributes to an advocate's position. Examples:

- A premise or load-bearing claim
- A specific argument or inference
- A concrete example or thought experiment used to support a claim
- An analogy or vocabulary import
- A concession to the opponent
- A diagnosis of a specific failure mode in the opposing view

A move can span sentences within a paragraph or multiple paragraphs. Pick the granularity that lets each move be referenced independently — too coarse and distinct contributions merge, too fine and continuous arguments fragment.

## Move IDs

Round-relative: `r<n>-<A|B>-mv<k>`. Each advocate-round combination starts from `mv1`. Cross-round references use the prior-round ID directly — `derives_from: r2-A-mv3` references advocate A's round 2 move 3.

## Cross-round identity

A move can recur across rounds — same conceptual content, possibly redeployed at a different abstraction level or against a different target. Recurrences get a fresh round-relative ID this round; declare `derives_from` pointing to the prior-round ancestor.

Use `responds_to` instead when the move directly counters an opposing-side move. `derives_from` is for same-side lineage; `responds_to` is for cross-side engagement. A move can carry both — e.g., redeploying the opponent's vocabulary against them.

## Granularity guidance

- **Extract only independent argumentative units.** Decorative examples that illustrate an already-extracted move belong to that move, not separately.
- **A move can span paragraphs.** Three paragraphs may develop one composite move; another paragraph may pack four moves into one rhetorical breath. The unit is conceptual, not paragraph-shaped.
- **Prefer fewer moves when in doubt.** Downstream consumers want a tractable inventory.

## Boundary judgment calls

- **Recurrence vs. refinement.** Same conceptual content possibly redeployed → reuse the prior label or a close variant. Content has shifted → use a fresh label that captures the shift. Either way, declare `derives_from` to the prior move; the lineage edge holds regardless of label continuity.
- **Cross-side redeployment.** When you repurpose the opponent's move to argue against them, declare both `derives_from` and `responds_to` to the same prior move.
- **Engagement vs. passing reference.** A move `engages` a thread when it advances, counters, or refines the thread's open question. Mentioning a thread in service of a different point doesn't qualify.
- **Diffuse vocabulary.** Terms that float across multiple advocates and rounds without a clear introduction point — don't force a lineage. The moves graph captures move-level lineage, not vocabulary-level.

## Output protocol

The moves file is written in two distinct writes; do not combine them.

1. **First write** — only the top-level heading (e.g., `# Advocate A Moves — Round 1`). This checkpoint signals primary final, move-pass starting. The orchestrator can spawn dependent agents while you continue.
2. **Second write** — update the file with the full content described in your slice.

All bullet values are bare IDs — no inline glosses or annotations. Explanatory prose goes in the advocate slice's rationale paragraph; synth and auditor slices carry only structured fields.

## Role slices

### Advocate

File: `round-<n>/advocate-<A|B>-moves.md`

Identify your own moves with paragraph spans. Declare cross-round lineage where applicable. In round N > 1, also list any live threads (from prior `threads.md`) this move substantively contributes to. No dependencies.

```markdown
# Advocate <A|B> Moves — Round <n>

## Moves

### r<n>-<A|B>-mv1

- label: <concise prose, 2-5 words>
- spans: r<n>-<A|B>-<k>.<p>[, ...]
- derives_from: r<m>-<A|B>-mv<k>      # optional, prior-round same-side move(s)
- responds_to: r<m>-<A|B>-mv<k>       # optional, prior-round opposite-side moves and/or synth claims (r<m>-S-<k>); mixed list permitted
- engages: T<k>[, ...]                # optional, live threads from prior threads.md

<optional rationale>

### r<n>-<A|B>-mv2

...
```

Mint round-relative IDs sequentially starting at `mv1`.

The rationale, if present, goes immediately under that move's bullet block, before the next `### r<n>-<A|B>-mv<k>` heading. It explains what *this* move does, why these spans, why the lineage and engagement hold. A single consolidated rationale block at the end of the file that names every move in turn (`mv1...`, `mv2...`, ...) is non-conformant: downstream parsers attribute rationale to the move whose bullets it follows, so a trailing block has no anchor and is unattributable.

### Synth

File: `round-<n>/synth-moves.md`

Depends on both advocates' populated moves files (`round-<n>/advocate-A-moves.md`, `round-<n>/advocate-B-moves.md`) for this round's move IDs. In round N > 1, also reads `round-<n-1>/synthesizer.md` and `round-<n-1>/auditor.md` for cross-round provenance lookups (replaces, forced_by). Cross-round move references to prior-round moves are also valid.

For each claim (including the structural-move claim `r<n>-S-0`):
- **`seeded_by`** — advocate move(s) the claim materially derives from.
- **`supported_by`** — earlier claims (this round or prior) this claim rests on as premises.
- **`replaces`** — prior-round claims this claim supersedes (takes over their explanatory role, does it better).
- **`forced_by`** — prior-round objections that motivated this claim's specific shape, format `r<n>-O-<k>`.

For each new thread (declared in `synth-threads.md`'s `## New threads`): the move(s) that opened the thread, under `opened_by:`. Key entries by the thread's `r<n>-S-th<k>` ID.

```markdown
# Synth Moves — Round <n>

## Per-claim

### r<n>-S-0

- seeded_by: r<n>-A-mv2, r<n>-B-mv1      # this round's advocate moves
- replaces: r<n-1>-S-0                   # prior structural-move claim, optional
- forced_by: r<n-1>-O-3                  # optional

### r<n>-S-1

- seeded_by: r<n>-A-mv2, r<n>-B-mv1
- supported_by: r<n>-S-0                 # this round's structural move, optional
- replaces: r<n-1>-S-2                   # optional
- forced_by: r<n-1>-O-2                  # optional

## Per-thread

### r<n>-S-th1

- opened_by: r<n>-A-mv2
```

Omit a bullet when the relation doesn't apply. A claim with no provenance bullets has no declared lineage.

### Auditor

File: `round-<n>/auditor-moves.md`

Depends on both advocates' populated moves files.

For each objection that references advocate moves:
- **Drop with section or paragraph anchor** → `targets:` lists moves the drop attacks.
- **Promoting objection** (smuggle, self_defeat, or drop with non-thread anchor) → `opens_via:` lists moves that opened the thread your objection now opens.

Skip objections without move references (drops with thread anchors; smuggles or self_defeats whose targets/conflicts are only synth claims).

```markdown
# Auditor Moves — Round <n>

## Move references

### O1

- targets: r<n>-A-mv2

### O3

- opens_via: r<n>-A-mv2, r<n>-A-mv3
```
