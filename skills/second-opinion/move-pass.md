# Move-pass

Opt-in extraction layer for the recursive dialectic. Advocate / synth / auditor each run a Phase 2 slice that records structured moves with paragraph spans + cross-round lineage; moderator is unaffected. Primary role specs and primary artifacts are unchanged.

Opt in when downstream tooling — visualizers, validators, cross-round provenance queries — needs the structured moves layer. Without it, these relations aren't recorded.

## Per-round artifacts

- `advocate-A-moves.md`, `advocate-B-moves.md` — own moves with paragraph spans + cross-round lineage
- `synth-moves.md` — per-claim + per-thread provenance bullets (`seeded_by`, `supported_by`, `replaces`, `forced_by`, `opened_by`)
- `auditor-moves.md` — per-objection move references

Slice schemas live in `roles/moves.md`.

## File layout addition

Each `round-N/` directory also contains:

```
advocate-A-moves.md, advocate-B-moves.md, synth-moves.md, auditor-moves.md
```

## Spawn prompt extension

Replace the base template's read-list and primary-task block with this phased structure:

```
Phase 1 read list (do not read anything else during Phase 1):
1. <role spec path>
2. <other inputs>

Phase 1 — primary task. Complete the primary task per <role spec>. Write to <primary-path>. Do not read roles/moves.md until Phase 1 is on disk.

Phase 2 — move-pass. Read <moves spec path> and run your slice. Write <moves-path> with only the top-level heading first (this is the phase-1-complete checkpoint), then update it with the full content.
```

The Phase 1 / Phase 2 separation prevents the agent from reading move-pass material before the primary output is final — extraction-layer thinking would contaminate primary. The same constraint is asserted three times (read list lockout, Phase 1 prohibition, Phase 2 placement) for redundancy.

## Two-write protocol

The moves file is written in two distinct writes:

1. **First write** — only the top-level heading. Checkpoint: primary final.
2. **Second write** — fill the file with the moves slice content.

Once the moves file appears, primary is final. Dependent agents can spawn immediately; the writer fills content in parallel.

## Monitoring

A persistent file-watcher tracks `*-moves.md` appearances across all round dirs:

```bash
DIR=<run-dir>
seen=":::"
for f in "$DIR"/round-*/*-moves.md; do
  [ -f "$f" ] && seen="${seen}${f}:::"
done
while true; do
  for f in "$DIR"/round-*/*-moves.md; do
    [ -f "$f" ] || continue
    case "$seen" in *":::${f}:::"*) continue ;; esac
    echo "MOVES_STUB: $f at $(date -u +%FT%T.%NZ)"
    seen="${seen}${f}:::"
  done
  sleep 0.5
done
```

Run via the Monitor tool with `persistent: true`. Pre-seeds `seen` with existing moves files so startup emits no events; one event per new stub thereafter. Two uses: (1) protocol verification — the heading-only stub fires before content fill-in, confirming the two-write protocol; (2) pipelining — spawn dependent agents at the stub event, in parallel with content fill-in.

Limitation: `seen` is path-based. If a moves file is deleted and re-created (during a QA-failure retry), no new event fires. Restart Monitor when retrying.
