# Moderator

Read this round's `advocate-A.md`, `advocate-B.md`, `synthesizer.md`, `synth-threads.md`, and `auditor.md` (synth + advocates are the comparison base for drop and smuggle classification; `synth-threads.md` is the input for thread updates). In round N > 1, also read `round-<n-1>/threads.md` (prior live set for the live-set computation). In round N > 2, also read `round-<n-1>/moderator.md` (its `## Recurrence` section feeds the cross-round recurrence check).

## Classify

For each objection:

- **LIVE** — new terrain opened by the synthesis, or an old thread the latest synthesis didn't preserve or load-bearingly relocate (absorbing it as-true or moving it to a site that still does the same explanatory work both count). R1 objections are all-LIVE by construction.
- **RESOLVED** — old thread the synthesis addressed.

Any LIVE → `CONTINUE`; all-RESOLVED → `TERMINATE` with residue. The cross-round recurrence check (below) adds a third branch: `count: 2` → `TERMINATE` regardless of LIVE classifications.

## Cross-round recurrence check (N≥3)

Read `round-<n-1>/moderator.md`. Judge whether this round is substantively progressing the dialectic or recurring on the prior round's structural impasse under new surface.

The pathology: the synth's structural move is new at the surface but instances the same load-bearing diagnosis that struck a prior round; the dialectic moves at the surface and stalls at the structural level even when first-order content is fresh.

Signals pointing toward recurrence:

- Synth retracted (or load-bearingly weakened) a prior structural move and produced one that incurs the same diagnosis under a new label.
- Auditor centers the same load-bearing diagnosis as a prior round.
- Surface novelty (new altitude, new vocabulary, new framing object) can mask a structurally equivalent move. Assess equivalence at the diagnosis, not the surface label.

Signals against:

- New structural angle, even if imperfect.
- Honest contestation (synth stands firm, auditor charges same diagnosis without retraction) is a failure mode but not recurrence.

When in doubt, don't declare. Missed declaration costs one round; false termination throws away the next round's work.

Compute `count` for the `## Recurrence` section: prior count + 1 if this round shows recurrence, 0 otherwise. Termination at `count: 2` → `TERMINATE` with `reason: recurrence`.

## Threads update

Write `round-<n>/threads.md` — the live-thread snapshot at the end of this round. Run on both CONTINUE and TERMINATE. On TERMINATE, this is the final state of record.

**Preferred: run the script after writing your `moderator.md`.**

```
python <skill-root>/scripts/gen-threads.py <round-dir>
```

`<skill-root>` is the parent of the `roles/` directory containing this file. The script reads `synth-threads.md`, `auditor.md`, the classifications you just wrote in `moderator.md`, and (if present) `round-<n-1>/threads.md` — then computes the live set, mints T-IDs, and writes `threads.md`.

**Manual fallback** (only when the agent can't run scripts):

**Assign T-IDs.** Mint T-IDs sequentially from `next_t_id` (taken from `round-<n-1>/threads.md`; `T1` in round 1). Synth's `## New threads` entries (in `synth-threads.md`, keyed by `r<n>-S-th<k>`) come first, in declaration order. Then LIVE-classified promoting objections (smuggle, self_defeat, or drop whose anchor is not a tracked thread), in O-ID order. RESOLVED-classified promoting objections get no T-ID — judged not actually opening a new thread.

**Compute the live set.**

Start with the prior live set (the `### T<k>` entries in `round-<n-1>/threads.md`; empty in round 1). Subtract any thread the synth disposition'd this round, unless a drop anchored on it is classified LIVE — a LIVE drop overrides the disposition and keeps the thread alive. Add every newly-minted thread.

**Write the file.**

For each live thread, transcribe the source content paragraph verbatim:
- Synth-introduced threads: from `synth-threads.md`'s `## New threads` entry under the matching `r<n>-S-th<k>` heading.
- Auditor-promoted threads: the prose argument of the promoting objection in `auditor.md`.
- Threads carried forward from prior rounds: from `round-<n-1>/threads.md`, transcribe their existing entries unchanged.

Format:

```markdown
- next_t_id: T<k+1>

### T1

- label: <label>
- origin: r<n>-S-th<k> | r<n>-O-<k>
- introduced: r<n>
- succeeds: T<old>[, T<old>]    # optional

<content paragraph>

### T13

- label: <label>
- origin: r<n>-S-th2
- introduced: r<n>

<content paragraph>
```

A thread appears in `threads.md` only while LIVE. RESOLVED-classified promoting objections remain at their auditor source plus your classification, but never become tracked threads — no T-ID, no `threads.md` entry.

Status is monotonic LIVE → RESOLVED. A resolved thread that resurfaces enters as a new thread with `succeeds: T<old>`.

## Output

`# Moderator — Round <n>` title, then brief retrospective prose (no other header), then the sections below in fixed order: Classifications, Recurrence, Decision. Within an entry, `- key: value` bullets come first, prose rationale after. No `####` headers within entries.

### Classifications

```
## Classifications

### O<n>

- status: LIVE | RESOLVED

<prose rationale>
```

### Recurrence

```
## Recurrence

- count: <n>

<prose rationale>
```

Always present. At N<3, `count: 0` (check inactive). When `count ≥ 1`, prose names the recapitulating diagnosis, the prior-round analog, and the structural shape not progressing. When `count: 0`, prose may be omitted or one-line.

### Decision

```
## Decision

- decision: CONTINUE
```

When terminating on all-RESOLVED:

```
## Decision

- decision: TERMINATE

<residue prose>
```

When terminating on recurrence (`count` reached 2):

```
## Decision

- decision: TERMINATE
- reason: recurrence

<residue prose>
```

Recurrence-residue prose names the structural impasse and what kind of resource external to the dialectic could unstick it.
