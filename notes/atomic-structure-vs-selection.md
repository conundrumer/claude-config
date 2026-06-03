# Inducing atomic structure vs. selection in generated writing

An experiment series testing whether format and style prompt levers make cleanroom Claude *select* and *de-compress* when answering one question, instead of compressing. Mostly n=1 per cell; n=3 for two conditions. Single topic, single model (Opus). Findings are directional, not conclusive.

## Frame

Levers tested: format, style rule, structural instruction. Effects tracked: scope depth, atomic decomposition, verbatim-term preservation, empty-rhetoric ("fluff") retention.

Every run answers one prompt — **"How does natural language encode graph structure?"** — in one of two modes:
- **fresh**: generate from the bare question.
- **rewrite**: re-express a fixed dense "control" answer (the unstyled fresh run, ~1850 words).

## Setup

One cleanroom child per run:

```
CLAUDE_CONFIG_DIR=<scratch> CLAUDE_CODE_DISABLE_CLAUDE_MDS=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
  CLAUDE_CODE_OAUTH_TOKEN=<tok> claude --disable-slash-commands \
  --permission-mode acceptEdits --allowedTools Write --model opus -p "<prompt>"
```

Isolated config dir (no skills, no global/project CLAUDE.md), auto-memory off, write-only tool surface. Each run writes one file; metrics by `grep`/`wc`. A separate `/revise` audit ran one general subagent per artifact in the *normal* environment (so the `/revise` catalog loads), each acting as a single analyzer fork — one pass, no edits, no spawning — reporting issue counts in four catalog categories (Leakage / Correctness / Fluff / Coherence).

**Measurement caveat, load-bearing for everything below:** "term survival" and "tic survival" are **exact-string** presence. A precise term re-expressed into plain words (`near-planarity` → "near-flat shape") counts as *lost* even when the underlying point survives. So this measures *verbatim preservation*, not correctness or quality — and high preservation can be *worse* writing, because it also preserves terms a good selection would cut.

Four empty-rhetoric **tics** tracked on rewrites, all lifted from the dense control: "this is the deepest trick", "the exceptions that prove the rule", "not competing answers (so much as)", "worth naming".

## Fresh runs — scope vs. style

| condition | words | scope band |
|---|--:|---|
| none (control) | 1847 | **deep** — only run to reach it |
| any single style — 8 cells (STE / atomic / modSTE, prose and YAML; + nested-list) | 439–1126 | **core** |
| NestedText + modSTE, n=3 | 1037 / 551 / 1020 | formalisms / **core** / formalisms |

Scope bands: **core** = nodes/edges/triples, coreference, linearization, ambiguity; **formalisms** = + AMR/RDF/dependency grammar/SRL; **deep** = + projectivity, dependency-length minimization, neural-probe results, citations.

## Rewrites of the control — terms, tics, structure

| condition (all rewrite control) | words | planar | relaxation | bijective | tics kept /4 | atomic? |
|---|--:|:--:|:--:|:--:|:--:|:--:|
| STE, as YAML | 2156 | ✗ | ✗ | ✗ | 0 | restructured |
| atomic, as YAML | 1993 | ✗ | ✗ | ✗ | 1 | list items |
| modSTE, as YAML | 2202 | ✗ | ✗ | ✗ | 2 | partial |
| NestedText + modSTE + "each sentence its own leaf" (n=3) | 2307/2180/2278 | ✓ | ✓ | ✓ | 4 / 4 / 4 | yes |
| NestedText + modSTE + "one idea per leaf" | 2107 | ✓ | ✓ | ✗ | 4 | yes |
| NestedText + modSTE + "one sentence max" | 2074 | ✗ | ✓ | ✗ | 4 | yes |
| NestedText + modSTE + *no leaf rule* | 2219 | ✓ | ✓ | ✗ | 2 | no (56 multi-sentence leaves) |
| nested-list (markdown) + atomic-spec + "each point: one sentence, one idea" | 2098 | ✓ | ✓ | ✓ | 1 | yes |

Style rules, verbatim:
- **STE**: `Write/Rewrite … in Simple Technical English.`
- **modSTE**: `… in Simple Technical English, with one change to the rules: use simple words, unless precision is needed.`
- **atomic prose**: `Short sentences. / Active voice. / Present tense. / One idea per sentence (or: Each point: one sentence, one idea). / Use simple words, unless precision is needed. / Use the same word for the same thing.`
- **NestedText format line**: `Write … in NestedText. Use multiline strings only for quoted text or code.`

## Takeaways (each hedged)

**1. Any style instruction caps fresh-generation scope; only the unstyled control reached the deep layer.** Every styled fresh run dropped the deep layer (AMR/probes/projectivity/citations) the control produced. *Hedge:* n=1 per cell, single topic; fresh scope is high-variance — n=3 of one styled fresh condition swung 551↔1037 words, core↔formalisms. The cap is directional and its level varies run-to-run.

**2. Fresh generation self-selects a shallow core; rewriting preserves the source's depth.** Same style instruction yields ~450–1040w fresh vs ~2000–2300w rewriting the control (~2–4×). *Hedge:* the gap is large and consistent across styles, but the *cause* (active reselection vs. the source anchoring the model) is inferred, n=1 per fresh cell.

**3. Structure is reliably inducible; selection is not.** Atomic structure appeared on demand (YAML list items, NestedText leaves, markdown points), and "minimal NestedText" emerged from the bare format name. But an explicit selection task — cut a structured doc to what a named reader (a KG-pipeline engineer) needs — failed: the model kept ~82–85% under both subtractive ("cut what they don't need") and inverted ("add only what's needed") framings, and kept whole sections irrelevant to that reader. *Hedge:* n=1–2; the "rationalizes retention section-by-section" reading comes from the model's own justifications, not an independent measure.

**4. Atomic structure exposes units; it neither selects nor de-fluffs.** Atomizing the dense control preserved every idea, and the `/revise` audit found atomic rewrites carried the source's empty rhetoric forward. Atomization did surface a latent correctness bug — a fabricated "house" node in the control's worked example — that the dense control's own reviewer missed. *Hedge:* single reviewer per artifact.

**5. The precision clause recovers verbatim technical terms on rewrites — cleanly isolated.** Adding "use simple words, unless precision is needed" to a plain-STE rewrite (register held constant, single variable) recovered claim-bearing terms (acyclic, stack, codec, contextual) that plain STE dropped; replicated near-deterministically across the NestedText n=3 rewrites. *Hedge:* single substrate; "recovers" is exact-string, and the model still drops terms it reads as non-load-bearing (planar, relaxation). An in-session judgment held those drops were *correct selection* — so this is verbatim preservation, not a quality gain.

**6. The leaf rule drives structure and part of fluff retention, not term fidelity (one clean within-family isolation).** Inside NestedText+modSTE+`>`, toggling "each sentence its own leaf" on/off is a single-variable swap. Removing it left term fidelity unchanged (planar/relaxation still kept), de-atomized the structure (one sample went from one-sentence leaves to 56 multi-sentence leaves), and dropped tic retention from 4/4 to 2/4. So term fidelity tracks something else (the format / `>`-restriction band, which kept planar/relaxation in every NestedText cell), while the leaf rule governs atomicity and some of the fluff. *Hedge:* the no-leaf cell is n=1; the leaf side is n=3 for tic/term counts but n=1 for the "one idea" / "one sentence max" phrasings; treat the 4→2 tic count as the signal, not which two survive.

**7. `/revise` Fluff+Leakage tracked the compression gradient.** Per-1000-word Fluff+Leakage: dense control highest (~3.3); both atomic variants zero. Within the fresh-YAML family, Fluff fell monotonically as simplicity pressure rose (plain-YAML 3 → STE-YAML 1 → atomic-YAML 0), format held constant. *Hedge:* n=1 per artifact, single reviewer, ±1 counts, threshold-dependent; Correctness and Coherence were entangled with the shared "house" example bug and with YAML's recurring recap-redundancy, so only Fluff+Leakage reads as a clean-ish writing-quality signal here.

## Caveats

- **n.** n=1 for nearly every cell; n=3 only for the two NestedText-modSTE conditions — where replication was near-deterministic for term/fluff counts and high-variance for fresh scope.
- **Single substrate.** One topic. The dense control's particular terms and tics drive most of the term/fluff measurement; another topic could move the numbers.
- **Single model.** Cleanroom Opus only.
- **Confounded cross-condition comparisons.** The headline contrasts (YAML vs NestedText, leaf vs no-leaf across families) varied multiple prompt dimensions together. Only within-family single-variable swaps isolate; the rest are directional.
- **Single-reviewer audit.** `/revise` counts are one fork per artifact, ±1, threshold-dependent.
- **Revised attributions.** At least one in-session causal claim was wrong and corrected by a follow-up run (term fidelity was first credited to the leaf instruction; the no-leaf run refuted it). Treat single-run causal stories here as provisional.

## Proposed (not landed) leads

- One single run combined atomicity, kept precise terms, and shed most tics: a markdown nested list with "each point: one sentence, one idea" (atomic, planar/relaxation/bijective kept, 1/4 tics, ~2100w). Worth verifying — n=1, and confounded against the NestedText runs on four axes (format, style spec, phrasing, `>`-restriction).
- Open question that would isolate why that cell shed tics while the NestedText leaf cells kept them: run "each point: one sentence, one idea" *in NestedText* (format held, phrasing swapped) against the leaf phrasing. Not yet run.

## Prior art

In-repo: `notes/negative-parallelism.md` (the "not X but Y" tic, one of the four tracked here), the global CLAUDE.md anti-compression / leakage rules, and `skills/experiment/` (the framework-development experiment posture this series follows).
