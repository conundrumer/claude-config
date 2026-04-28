# Dialectic Schema

Reference for the entities, IDs, and relations a recursive dialectic produces. The role prompts encode this implicitly; this doc collects it for parsers, validators, and visualizers.

The base layer (advocate / synth / auditor / moderator outputs) is always written. The move-pass layer (`*-moves.md`) is opt-in and adds finer-grained provenance on top of the base.

## Identity tiers

- **Per-round IDs** — declared inline in a round's artifacts, namespaced by the round. Format: `r<n>-<role>-<k>`. Examples: `r2-S-1` (claim), `r2-S-0` (this round's structural-move claim), `r2-S-th3` (synth-introduced thread declaration), `r2-O-3` (objection), `r2-B-3` (advocate B's section 3), `r2-A-mv4` (advocate A's move 4).
- **Cross-round IDs** — cumulative sequential, persist across rounds. Format: `<role-letter><k>`. Currently: `T<k>` (thread; minted by moderator).

ID conventions: lowercase round prefix (`r<n>`); capital role letter (S, O, A, B, T); single-hyphen separators between segments; no zero-padding.

Paragraph IDs extend section IDs with a dot separator: `r<n>-<A|B>-<k>.<p>`. Used as cite targets by drop anchors and by move `spans`.

## Entities

### AdvocateSection · `r<n>-<A|B>-<k>`

Numbered section in an advocate essay. Heading `### <k>. <title>` in `round-<n>/advocate-<A|B>.md`. Section ID's `<k>` is the leading integer in the heading.

```yaml
declared_by:  advocate
fields:
  prose:        required
```

### AdvocateParagraph · `r<n>-<A|B>-<k>.<p>` *(derived)*

Paragraph within an advocate section. Blank-line-separated block; within-section counting (each section restarts at ¶1). Not declared anywhere — derived from parsing the advocate file. Cite target for drop anchors and for move `spans`.

### Claim · `r<n>-S-<k>`

Synth's structured assertion. Heading `### r<n>-S-<k>` in `round-<n>/synthesizer.md`.

Index `0` is reserved for the **structural-move claim** — the claim that names what shape this synthesis takes. It lives under `## Structural move` and carries a `move_label:` bullet plus prose articulating the move on its own terms. The shape can be Aufhebung, level-shift, framing-dissolution, juxtaposition, undecidable, or anything else the contradiction calls for. Indexes `1+` are content claims under `## New claims`.

```yaml
declared_by:  synth
fields:
  prose:        required
  move_label:   required for r<n>-S-0; absent otherwise
```

Cross-round provenance (`seeded_by`, `supported_by`, `replaces`, `forced_by`) is not declared in primary. The opt-in `synth-moves.md` carries it per-claim.

### SynthThreadIntro · `r<n>-S-th<k>`

Synth's introduction of a new thread, declared this round before T-IDs are minted. Heading `### r<n>-S-th<k>` under `## New threads` in `round-<n>/synth-threads.md`. IDs are sequential per round starting at `th1`. The moderator maps each `r<n>-S-th<k>` to a T-ID when classifying LIVE; the th-ID itself stays as the `origin:` reference in `threads.md`.

```yaml
declared_by:  synth
fields:
  label:       required (concise prose, 2-5 words)
  content:     required (paragraph describing the thread; transcribed verbatim into threads.md if classified LIVE)
  succeeds:    list[T-id]    # optional, prior-round threads this absorbs
```

### Disposition · *(per-thread, per-round; keyed by T-id)*

Synth's update for a thread it engaged this round. Sub-entry under `## Disposition` in `round-<n>/synth-threads.md`, heading `### T<id>`.

```yaml
declared_by:  synth
fields:
  action:    absorbed | relocated | retired
  to:        list[claim-id]    # required when action is relocated
  prose:     required for relocated and retired
```

Omitted threads from the prior live set are presumed unchanged (still LIVE).

### Objection · `r<n>-O-<k>`

Auditor's attack on the synthesis. Heading `### O<k>` under `## Objections` in `round-<n>/auditor.md`. O-IDs are round-local sequential integers (O1, O2, ...); the global ID is `r<n>-O-<k>`.

```yaml
declared_by:  auditor
fields:
  prose:           required (the argument; also the thread's content when a promoting objection is classified LIVE)
  kind:            drop | smuggle | self_defeat
  label:           required (concise 2-5 word name; for promoting kinds also names the thread if classified LIVE)
  anchor:          T-id | section-id | paragraph-id | free-form    # drop only; type derived from value shape
  target:          claim-id                                         # smuggle only
  conflicts:       list[claim-id] (≥2)                              # self_defeat only
  succeeds:        list[T-id]                                       # optional, promoting kinds only
```

**Anchor disambiguation** (drop only). Type is derived from the value's shape:

| Pattern | Type |
|---|---|
| `^T\d+$` | thread |
| `^r\d+-[AB]-\d+$` | section |
| `^r\d+-[AB]-\d+\.\d+$` | paragraph |
| anything else | free-form prose |

**Promoting kind** = smuggle, self_defeat, or drop whose anchor is not a `T<id>`. A promoting objection becomes the origin of a new thread iff the moderator classifies it LIVE; RESOLVED-classified promoting objections receive no T-ID.

### Classification · *(per-objection, per-round; keyed by O-id)*

Moderator's LIVE/RESOLVED call on each objection. Heading `### O<k>` under `## Classifications` in `round-<n>/moderator.md`.

```yaml
declared_by:  moderator
fields:
  status:    LIVE | RESOLVED
  prose:     required (rationale)
```

### Decision · *(once per round)*

Moderator's CONTINUE/TERMINATE call. `## Decision` block in `round-<n>/moderator.md`.

```yaml
declared_by:  moderator
fields:
  decision:  CONTINUE | TERMINATE
  residue:   required for TERMINATE (prose)
```

CONTINUE iff any objection classified LIVE; otherwise TERMINATE.

### Thread · `T<k>`

Persistent recurring tension. Cross-round ID minted by the moderator only when classifying its source LIVE. Sources: synth's `## New threads` entry (origin `r<n>-S-th<k>`), or auditor's promoting objection (origin `r<n>-O-<k>`). While LIVE, the thread appears as `### T<k>` in `round-<n>/threads.md` with `label:` as the first bullet.

```yaml
declared_by:  synth (intro) | auditor (promote)
t_id_minted:  moderator (only for LIVE classification)
fields:
  label:       required (immutable after introduction)
  content:     required (transcribed verbatim from source into threads.md)
  introduced:  r<n>                          # round of first appearance
  origin:      r<n>-S-th<k> | r<n>-O-<k>     # immutable
  status:      LIVE | RESOLVED               # all threads start LIVE; synth disposition transitions LIVE → RESOLVED unless a LIVE drop on the thread overrides (monotonic)
  succeeds:    list[T-id]                    # optional, prior-round threads absorbed
```

A RESOLVED-classified promoting objection never becomes a thread: no T-ID, no `threads.md` entry. Status is monotonic LIVE → RESOLVED. A resolved thread that resurfaces enters as a new thread with `succeeds: T<old>`.

`round-<n>/threads.md` carries one root-level bullet for parser convenience: `- next_t_id: T<k+1>`.

### Move · `r<n>-<A|B>-mv<k>` *(opt-in via move-pass)*

Atomic argumentative unit. Round-relative — each advocate-round combination starts at `mv1`. A move that recurs from a prior round gets a fresh ID this round and declares `derives_from` to the prior ID. Heading `### r<n>-<A|B>-mv<k>` in `round-<n>/advocate-<A|B>-moves.md`.

```yaml
declared_by:  advocate (move-pass)
fields:
  label:         required (concise prose, 2-5 words)
  spans:         list[paragraph-id]          # paragraph IDs in same advocate's same-round essay
  derives_from:  list[move-id]               # optional, prior-round same-advocate moves
  responds_to:   list[move-id | claim-id]    # optional, prior-round opposite-advocate moves and/or prior-round synth claims
  engages:       list[T-id]                  # optional, live threads from prior threads.md
  rationale:     optional prose paragraph immediately below the bullets, before the next move heading
```

`responds_to` ref types by shape: `r<m>-<A|B>-mv<k>` → opposite-advocate move; `r<m>-S-<k>` → synth claim. Mixed lists permitted.

Per-claim and per-thread provenance live in `synth-moves.md`; per-objection move references live in `auditor-moves.md`.

## Relations

### Base layer

| From | Relation | To | Cardinality | Where declared |
|---|---|---|---|---|
| thread | succeeds | thread (prior round) | many | synth (intro) or auditor (promote) |
| disposition | addresses | thread | one | synth (`### T<id>` heading under `## Disposition`) |
| disposition | to | claim (this round) | many | synth (when action is relocated) |
| objection (drop) | anchor | thread \| section \| paragraph \| free-form | one | auditor |
| objection (smuggle) | target | claim | one | auditor |
| objection (self_defeat) | conflicts | claim | many (≥2) | auditor |
| objection (LIVE-promoting) | promotes | thread | one | implicit (via thread's `origin` field; T-ID minted by moderator) |
| classification | classifies | objection | one (paired by O-id) | moderator |

### Move-pass layer *(opt-in)*

| From | Relation | To | Cardinality | Where declared |
|---|---|---|---|---|
| move | spans | paragraph | many | advocate (`spans:`) |
| move | derives_from | move (prior round, same advocate) | many | advocate (`derives_from:`) |
| move | responds_to | move (prior round, opposite advocate) \| claim (prior round) | many | advocate (`responds_to:`) — element type by shape |
| move | engages | thread | many | advocate (`engages:`) |
| claim | seeded_by | move | many | synth (`seeded_by:` per-claim) |
| claim | supported_by | claim (this or prior round) | many | synth (`supported_by:` per-claim) |
| claim | replaces | claim (prior round) | many | synth (`replaces:` per-claim) |
| claim | forced_by | objection (prior round) | many | synth (`forced_by:` per-claim) |
| SynthThreadIntro | opened_by | move | many | synth (`opened_by:` per-thread, keyed by `r<n>-S-th<k>`) |
| objection (drop with section/paragraph anchor) | targets | move | many | auditor (`targets:`) |
| objection (promoting) | opens_via | move | many | auditor (`opens_via:`) |

Field naming: `seeded_by`, `opened_by`, `targets`, `opens_via` — each names one specific relation, so a parser knows the edge type from the field alone.

## Authoring

| Entity | Authored by | Notes |
|---|---|---|
| AdvocateSection | advocate | `### <k>. <title>` heading + prose in `advocate-<A|B>.md` |
| AdvocateParagraph | — | derived; not declared |
| Claim (content) | synth | `### r<n>-S-<k>` heading + prose under `## New claims` in `synthesizer.md` |
| Claim (structural-move, `r<n>-S-0`) | synth | `move_label:` bullet + prose under `## Structural move` |
| SynthThreadIntro | synth | `### r<n>-S-th<k>` heading + `label:` bullet + content paragraph under `## New threads` in `synth-threads.md` |
| Disposition | synth | `### T<id>` heading + bullets + prose under `## Disposition` in `synth-threads.md` |
| Objection | auditor | `### O<k>` heading + bullets + prose argument in `auditor.md`; the prose serves as thread content for promoting objections classified LIVE |
| Classification | moderator | `### O<k>` heading + `status:` bullet + prose in `moderator.md` |
| Decision | moderator | `## Decision` block in `moderator.md` |
| Thread | synth or auditor (declares) + moderator (mints T-ID, transcribes into `threads.md`) | minted only when classified LIVE |
| Move *(opt-in)* | advocate | in `advocate-<A|B>-moves.md` — own moves with paragraph spans + cross-round lineage |
| Per-claim provenance *(opt-in)* | synth | in `synth-moves.md` — `seeded_by`, `supported_by`, `replaces`, `forced_by` |
| Per-thread provenance *(opt-in)* | synth | in `synth-moves.md` — `opened_by` keyed by `r<n>-S-th<k>` |
| Per-objection move references *(opt-in)* | auditor | in `auditor-moves.md` — `targets` (drop) or `opens_via` (promoting) |

## Files

```
<dialectic-dir>/
  session.md            # topic, scope, positions, belief-burden — orchestrator, once
  round-<n>/
    advocate-A.md       # numbered sections + ## Root
    advocate-B.md       # numbered sections + ## Root
    synthesizer.md      # prose + ## Structural move + ## New claims
    synth-threads.md    # ## New threads + ## Disposition
    auditor.md          # prose + ## Objections
    moderator.md        # prose + ## Classifications + ## Decision
    threads.md          # - next_t_id bullet + ### T<k> entries (live only)
    advocate-A-moves.md # opt-in: A's moves + cross-round lineage
    advocate-B-moves.md # opt-in: B's moves + cross-round lineage
    synth-moves.md      # opt-in: per-claim and per-thread provenance
    auditor-moves.md    # opt-in: per-objection move references
```

Each `round-<n>/threads.md` is a write-once snapshot of the live thread set at the end of round N. Roles in round N+1 read it as `round-<n-1>/threads.md` (relative to their round) for the inherited live-thread set.

## Parser notes

- Headings with `### <ID>` carry the ID; entity type is determined by the parent `## Section` heading (and the filename for cases like `### O<k>` which appears as both Objection and Classification under different parents).
- Bullets within an entry come before prose paragraphs.
- No `####` headings appear inside entries.
- Multi-valued fields are comma-separated inline (`succeeds: T1, T3`); whitespace after commas is permitted.
- Optional fields are omitted entirely when empty (no blank values).
- Cross-file thread linking is ID-based throughout. Synth declares with `### r<n>-S-th<k>` in `synth-threads.md`'s `## New threads`; synth's `## Per-thread` in `synth-moves.md` keys by the same `r<n>-S-th<k>`; the moderator records `origin: r<n>-S-th<k>` on the minted `### T<k>` in `threads.md`. Labels are content, not handles.
- For a promoting objection classified LIVE, the moderator transcribes its prose argument verbatim as the new thread's content paragraph in `threads.md`.
