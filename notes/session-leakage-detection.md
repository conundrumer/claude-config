# Detecting session leakage: phrase, context, substrate

An experiment on what directive phrase catches session-leakage in artifact prose, and under what evaluation conditions detection actually works.

Sibling to [edit-leakage.md](edit-leakage.md), which landed the underlying rule but flagged the session-leakage half as not separately experimentally validated. This is that validation, plus a phrase-shootout for using the rule as a directive.

## The phenomenon

Recap. Session leakage is content in an artifact that derives from the conversation, source files, or prior file states that the artifact's reader cannot access. Surface forms vary by elicitation conditions:

- **Doc-history bleed** (chat-driven elicitation): canonical "Y not X", "stays X", "(was: ...)" framings. Example from a tidytable DESIGN.md run — *"(Earlier versions also listed 'no type coercion' as a non-goal. That turned out to be wrong: every caller was doing the same `int(row['age'])` pattern, so the library now ships per-column coercion steps. See 'Type coercion' below.)"* The "every caller" was one user (me); the parenthetical narrates a session decision a future reader has no access to.

- **Phantom-counterpoint bleed** (chat-driven elicitation): multi-sentence refutation of a position the reader doesn't hold. Example from a design-reviews essay — three sentences disproving "send the doc ahead" in a post that isn't proposing it; the refutation only makes sense because the prior draft recommended it.

- **Source-register transplant** (file-only elicitation): verbatim copying of source-file content with register mismatch. Example from a styleguide run — the "Edit ruthlessly. AI prose tends to be longer..." bullet was lifted unchanged from `revision-notes.md` into the published guide, preserving the internal-memo register.

- **Justification leak** (file-only elicitation): the *reason for a revision* leaks from the change memo into the artifact as defense. Example from a code-review playbook — *"Without tests we can't know the rest."* appended to the Tests bullet, lifted from the memo's rationale for promoting Tests above Correctness.

- **Defensive-rule residue** (bootstrap-time, when the artifact's reader is Claude): rules added because the model was *worried about* a behavior during authoring, not because a fresh-loading reader would naturally drift toward it. Example from a SKILL.md — *"Don't run `git commit` or `git add`. Drafting only."* — guards a behavior nothing else in the skill prompts; only present because the authoring conversation was around commit-vs-draft scope.

- **Souvenir example** (bootstrap-time): a specific in-conversation invented phrasing that propagates verbatim into the artifact as an example. Example from the SKILL.md — *"I assumed this is a bug fix rather than intentional behavior change — confirm before committing."* — invented during authoring as illustrative, but reads as a literal template a future Claude might copy verbatim.

## Why test phrases

The rule from `edit-leakage.md` covers the phenomenon in prose-rule form. To deploy as a directive — *"apply directive X"* in a review prompt, or as a one-line CLAUDE.md tag — it needs a name. Different candidate names carry different concept maps in the model's head; the wrong name makes the directive misfire.

## Question

1. **Phrase.** Which directive phrase, given alone, leads the model to flag the right things?
2. **Context.** Does the evaluation context (fresh session with only the artifact, vs branched fork of the elicitation session) change detection?
3. **Substrate.** Does the artifact's topic interact with the phrase's interpretation?

## Setup

Two test types.

**Concept-recall.** Fresh `claude -p` with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`, `--tools ""`, `--no-session-persistence`, `--model opus`. Prompt: *"If I gave you the directive '<phrase>' while writing prose (docs, comments, or other artifacts), what would you attend to or avoid? Be concrete."* Manual judgment on whether the response lands on the target concept.

**Edit-pass.** Elicit an artifact via a multi-turn or file-only session, then evaluate via:
- *Fresh:* one-shot `claude -p` with the artifact pasted into the prompt and the directive line included, isolation flags as above. The evaluator sees only the artifact — no session, no source files.
- *Branched:* `--resume <elicitation-session-id> --fork-session`. The evaluator inherits the full conversation that produced the artifact.

Score recall (catches known bleed targets, identified by the experimenter from the elicitation history) and precision (doesn't over-flag clean prose).

**Substrates** (each picked for likely bleed shape):
1. tidytable Python lib DESIGN.md (multi-turn chat with motivated drifts) → doc-history bleed
2. Design-review blog post (multi-turn chat with motivated drifts) → phantom-counterpoint bleed
3. Engineering style guide (file-only: bootstrap, then memo-driven revision) → source-register bleed
4. Code-review playbook (file-only: bootstrap, then memo-driven revision) → justification-leak bleed
5. SKILL.md for a commit-message skill (file-only: bootstrap, then memo-driven revision; **artifact's intended reader is Claude itself**) → bootstrap-time bleed (defensive rules, souvenir examples, canonical Y-not-X in the bootstrap)

## Variants

Phrases tested in concept-recall:

- `addressee collapse`
- `co-presence assumption`
- `indexical leak`
- `session as shared context`
- `reader-frame unawareness`
- `common-ground bleed`
- `session leakage`
- `claude code session leakage`

Phrases carried into edit-pass: `reader-frame unawareness`, `indexical leak`, `session leakage`, `claude code session leakage`. Plus baseline (no directive — generic *"review the prose, list what you'd change"*).

## Results

### Concept-recall

| Phrase | Lands on right concept unaided? | Notes |
|---|---|---|
| `session leakage` | ✅ direct hit | Names the canonical surface forms unprompted: *"we decided to…", "as requested", "added for the X migration", session IDs, tool/process residue.* Diagnostic: *"if removing the line just loses a breadcrumb from this conversation, cut it."* |
| `claude code session leakage` | ✅ direct hit, more specific | Disambiguates the HTTP-session reading. Names Claude/agent/model identifiers, tool names, prompt artifacts, session IDs, scratch dirs. Slightly narrower. |
| `reader-frame unawareness` | ✅ but interpretation drifts | Picks up "writing that fails to model what the reader doesn't share." Drifts toward jargon/forward-refs in fresh context; snaps to "author-frame vs reader-frame" with session context. |
| `indexical leak` | ✅ narrow but clean | Resolves to deixis: temporal/positional/reference-population indexicals. Catches doc-history bleed surgically; misses non-indexical bleed shapes. |
| `common-ground bleed` | ✅ acceptable | Names assumptions from one context bleeding into prose where the reader doesn't share that ground. |
| `co-presence assumption` | ⚠️ inverted | Read as a goal ("write co-presently") rather than a failure mode. Lists deixis under *attend to*, not *avoid*. |
| `session as shared context` | ❌ inverted | Read as a directive to *use* the session as shared context. Endorsed "skip recap of things we both already know" — the failure mode itself, presented as guidance. |
| `addressee collapse` | ❌ wrong concept | Read as "strip second-person voice." Unrelated to session-leakage. |

Pattern: phrases that *describe the failure* (`leak`, `bleed`, `unawareness`) interpret in the right direction. Phrases that *describe the state* (`co-presence assumption`, `session as shared context`) get read as goals — LLMs default-interpret neutral nominalizations as desirable.

### Edit-pass — DESIGN.md (doc-history bleed)

Bleed targets: 6 clauses in the *"Earlier versions also listed..."* parenthetical.

| Directive | Fresh | Branched |
|---|---|---|
| baseline | ✅ caught as *"historical changelog; cut from design doc"* | ✅ + flagged *"every caller"* as hyperbole (knew it was one user) |
| reader-frame | ⚠️ caught as 1 of 20 jargon issues | ✅ snapped to right concept; *"writing that addresses author's concerns... rather than the reader's situation"* |
| indexical leak | ✅ surgical: 5 separate hits on `now`, `Earlier`, `turned out`, `below`, `every caller` | ✅ broader scope including "we" voice |
| session leakage | ✅ broad coverage (24 findings including all bleed) | ✅ most incisive — caught the parenthetical *plus* `version = "0.3.0"` (3 bumps in one session for unreleased lib) and *"10k-row"* invented flavor |

### Edit-pass — essay (phantom-counterpoint bleed)

Bleed targets: refutation of the discarded "send-doc-ahead" practice (E1–E4); *"async-first orgs"* trace (E6).

| Directive | Fresh | Branched |
|---|---|---|
| baseline | ⚠️ flagged sentences for stylistic reasons | ⚠️ general editor mode |
| reader-frame | ❌ jargon focus, missed bleed | partial — flagged "send-ahead" as overclaim; explicitly cited "the user's own pushback in this conversation" as reason to add a hedge |
| indexical leak | ❌ caught only physical-meeting deixis | ❌ same |
| session leakage | ✅ caught E1, E6, transcript fragment | ✅ **caught E1–E6 explicitly**: *"the 'send it ahead' rebuttal is disproportionate. That length is a residue of the moment in our conversation when send-ahead-vs-silent-read was the live debate."* |

### Edit-pass — playbook (justification-leak bleed)

Bleed targets: *"Without tests we can't know the rest"* (justification leak); *"More PRs are being drafted with..."* (defensive opener); *"A few things to flag specifically"* (bolted-on lead-in).

| Directive | Fresh | Branched |
|---|---|---|
| session leakage | ❌ **security misread** — interpreted as HTTP/auth session bugs; added rules to the playbook *about* session-leakage as a code review hazard rather than flagging the prose's own bleed | ✅ caught all three; sharpened my analysis (noted that *"the rest"* implies tests gate Fit/Readability/Scope, which doesn't follow) |
| claude code session leakage | ❌ **topic misread** — interpreted as AI-artifacts-in-shipped-code; added rules about catching Claude transcripts in PRs rather than flagging prose bleed | (untested) |

The substrate primed interpretation: a code-review playbook is *about* code review, so the directive read as a topic to cover. Both `session leakage` and `claude code session leakage` collapsed into the topic interpretation, just with different topics.

### Edit-pass — SKILL.md (bootstrap-time bleed; reader is Claude)

Bleed targets: canonical Y-not-X in the description (*"— not when they ask you to actually commit"*); defensive rule (*"Don't run `git commit` or `git add`"*); temporal-scope ambiguity in *"on this commit"* / *"the user asked"*; souvenir example; structural redundancy (header duplicates description; unused `allowed-tools`).

| Directive | Fresh | Branched |
|---|---|---|
| session leakage | ✅ caught the canonical Y-not-X, the temporal "this commit", the souvenir example, "the user" framings throughout. Some over-eager flags on normal SKILL.md second-person framings ("say so", "point that out"). Did **not** catch defensive-rule residue, header duplication, unused `allowed-tools`. | ✅ caught all of fresh's true positives plus the defensive-rule residue (*"only present because I was worried about it during authoring, not because a fresh invocation would naturally drift there"*), structural duplications, and the unused tools. Disambiguated "session" up top before evaluating. |

Important: **most of the SKILL.md bleed was in the bootstrap, not the revision.** The model writing its own initial SKILL.md inserted Y-not-X scope clauses, defensive rules, and souvenir examples — all from authoring-time concerns, not from drift across edits. The revision phase added comparatively little.

This substrate did **not** trigger substrate-induced mode confusion. A SKILL.md is for Claude to load, but its *topic* (drafting commits) is not session-leakage, so the directive landed as an editorial concern rather than a subject the doc should cover. The mode confusion in the playbook case was specifically because the playbook's *topic* could plausibly be session-leakage-as-a-thing-to-catch.

## Takeaways

**1. `session leakage` is the strongest phrase across substrates and bleed shapes — in branched context.** It catches every bleed shape (doc-history, phantom-counterpoint, justification-leak) and finds bleed a manual scan misses (verbatim source-bullet copies, version numbers, invented numerical flavor). In branched runs the model also explicitly cites the session moment that produced each bleed instance.

**2. Fresh-context evaluation is structurally limited for session-leakage detection.** A fresh evaluator has no session — by definition, can't directly identify what came from the session. Detection works in fresh context only via surface heuristics ("this looks defensive," "this reads like a transcript"). Branched evaluation (`--fork-session` from the elicitation session) is the correct deployment scenario.

**3. The substrate primes interpretation, especially in fresh context.** When the artifact's topic plausibly *is* about the directive's apparent subject, the directive reads as a *topic to address* rather than as an *editorial concern about the prose*. This isn't fully fixed by adding qualifiers (`claude code session leakage` still misfires on code-review substrates, just toward a different topic). The trigger is *topic match*, not *code-adjacency in general* — a SKILL.md (also code-adjacent, also Claude-loaded) didn't trigger the misread because its topic (drafting commits) is unrelated to session-leakage.

**4. File-only revision rarely produces the canonical "Y not X" pattern; bootstrap can.** File-only revision elicitation (apply `revisions.md` to existing artifact) reliably produces source-register transplant and justification-leak, but not the canonical *"Y not X"* / *"stays X"* form. The bootstrap turn — especially when the artifact's intended reader is Claude — does produce Y-not-X (e.g., the SKILL.md description's *"— not when they ask you to actually commit"*), defensive rules, and souvenir examples. The bleed is shaped by *who's authoring under what concern*, not just by whether chat or file drove the change.

**5. Branched session-leakage eval reliably catches more than the experimenter does.** Across three of the four substrates with manual ground truth (DESIGN.md, playbook, SKILL.md), the branched eval surfaced bleed instances I missed in my own scan — version-number bumps as session artifact, defensive rules from authoring anxiety, structural duplications, the canonical Y-not-X in the SKILL.md bootstrap. This is a deployment-relevant finding: in-session model self-review is *not* just a verification check on a manual scan, it's a **better detector** than the experimenter armed with full session knowledge. Plan for branched self-review as the primary detection mechanism, not as a confirmation of human review.

**6. Phrase rhetorical shape matters: name the failure, not the state.** Phrases that name the failure mode (`leak`, `bleed`, `unawareness`) interpret correctly. Phrases that name the state being-leaked (`co-presence assumption`, `session as shared context`) get read as descriptions of a goal rather than a failure to avoid.

## Caveats

- N=1 to ~3 per cell. Within-condition outputs were qualitatively consistent but not statistically characterized.
- Manual scoring. Bleed identification depends on the experimenter knowing the elicitation history. The branched-eval finding (model catches what manual scan missed) is itself the strongest argument for in-session evaluation; equivalently, it's a check that the manual ground truth was incomplete.
- Substrate selection is purposive (4 substrates picked for likely bleed shapes), not random. The substrate-induced mode confusion finding was observed clearly on one code-review-related substrate; broader sweep would strengthen it.
- The phantom-counterpoint shape was not separately suppression-tested. The `edit-leakage.md` rule covers it in principle (*"no concessions to prior framings"*), but no A/B run was done.
- File-only *revision* did not reproduce the canonical "stays X" surface form even with explicit *"keep as is"* framings in the source `revisions.md`. The canonical Y-not-X *did* appear in the SKILL.md bootstrap, but bootstrap-stage authoring is not the same workflow that surfaces "stays X" in real use; that pattern likely needs chat-side priming during interactive editing. Inconclusive whether file-only could ever produce "stays X" under different conditions.
- `claude code session leakage` was tested in fresh context on one substrate only; the topic-misread finding generalizes from `session leakage`'s pattern but isn't independently validated across substrates.
- The "branched eval catches more than the experimenter" finding (takeaway 5) is itself manually scored against my own initial reads. A more rigorous test would have an independent human reviewer score the branched eval's findings against ground truth set by a third party — none of that was done. The qualitative observation is consistent across three substrates, though.

## Eliciting heavy leakage (this session's setup)

**Domain.** Updating a SKILL.md file (the `claude-use` skill — meta-orchestration for spawning `claude -p` children) — specifically the Isolation section documenting clean-room isolation flags. SKILL.md is loaded by Claude as instructions, so the author and reader are both Claude in different sessions. The writing Claude has the full session context; the reading Claude has none.

**Trial-and-error sequence.** ~5 failed approaches before landing on the working recipe, each with a distinct error state:
- empty `CLAUDE_CONFIG_DIR` → "Not logged in"
- symlinked partial mirror of `~/.claude` → "Not logged in"
- `rsync` full copy → "Not logged in"
- `ANTHROPIC_API_KEY="$CC_TOKEN"` (OAuth token in API-key slot) → "Invalid API key"
- `CLAUDE_CODE_OAUTH_TOKEN="$CC_TOKEN"` + scratch `CLAUDE_CONFIG_DIR` → auth works; response leaked kaomoji (from global CLAUDE.md) + `ai-lint` references (from project CLAUDE.md and skill catalog)
- + `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` + `cd /tmp` → clean

**Gotchas accumulated** along the way (each a potential "warning to future readers"):
- `CLAUDE_CONFIG_DIR` override loses keychain auth.
- OAuth tokens and API keys live in distinct env-var slots.
- Project `CLAUDE.md` auto-discovery from cwd is independent of `CLAUDE_CONFIG_DIR`.
- `--disable-slash-commands` doesn't strip the skill catalog from the system prompt.
- Auth resolution appears path-keyed in the macOS keychain.

**Trigger.** Immediate transition from saturated discovery context to writing the SKILL.md Isolation section. No cooling period; no register switch from prose-of-explanation to flag-by-flag reference.

**Output.** Heavy leak. Verbatim from the first edit:
- *"Even with `--disable-slash-commands` + `CLAUDE_CODE_DISABLE_*` env vars, skill names from `~/.claude/skills/` stay visible..."* (concession to prior framing)
- *"Without it, fresh probes pull skill names from the catalog into responses unprompted (e.g., probes for the term 'prose quality' surfaced `ai-lint` by name)"* (counterfactual motivation + specific session-incident example)
- *"Does NOT strip the skill catalog from the system prompt"* (capitalized negation)
- *"Each piece handles a different leak:"* (narrative framing as list intro)
- *"(the keychain entry is keyed to the literal config-dir path)"* (speculative mechanism parenthetical)
- *"so OAuth-subscription users still need the multi-env-var recipe above"* / *"Skills still resolve via `/skill-name` under `--bare`"* (concessive "still")

## Fix-pass dynamics

Applying the directive iteratively on the same artifact ("fix all session leakage") surfaces fractal layers:

- **Round 1**: specific session-incident examples — verbatim quotes, names, scenarios.
- **Round 2**: concessions to prior framings — *"still"*, *"even with X"*, *"not sufficient on their own"*.
- **Round 3**: capitalized negations (*"Does NOT X"*), empirical motivations (*"Without X, fresh probes Y"*), speculative mechanism parentheticals.
- **Round 4**: narrative framings (*"Each piece handles a different leak"*) that scaffold the bullet structure itself.

Eventually the section's *purpose in the writing* is the leak: e.g., "explain why each piece is needed in light of what we found doesn't work." That purpose IS the discovery narrative. Every phrasing reaching for it carries the same shape; patching phrasing alone doesn't change the purpose.

**Intentionality, not category.** Session-leakage is not "session-derived content" per se — it is *reflex* inclusion of session-derived content. A doc can be entirely session-derived (a writeup, a postmortem, this very note) and clean if every inclusion is deliberate.

**Loop design.**
- Default to aggressive removal. Re-adding is cheap; anything re-added is intentional by definition.
- Log removed items for human review and deliberate re-addition.
- Flag at the *structural* level (not item-level) when iterating surfaces deeper layers — that signals the doc's structure or purpose needs rethinking, not more phrasing patches. The flag is meta: "we're in a fractal trap," not "this line might be worth keeping."

**Structural escape.** When session-derived content is load-bearing for future readers, give it a designated home (e.g., a "Gotchas" section in a tools/instructions doc) where the reader expects discovery-origin. The legitimization happens at the doc-structure level, not by softening the prose.

## Landed rule

No new rule landed. The existing rule from [edit-leakage.md](edit-leakage.md) covers the phenomenon in prose form. The takeaway is about *deployment*:

- **For in-session self-review** (the typical Claude Code case): pair the rule with `session leakage` as the directive name. Use a fork of the working session as the reviewer (`--resume <id> --fork-session`), not a fresh call. The branched setup catches more than a careful human scan, not just as much — treat it as the primary detector, not a confirmation step.
- **For fresh-context review of standalone artifacts**: do not use `session leakage` alone, especially on code-adjacent substrates. Either use a different phrase that names a surface property the artifact-only reader can recognize (e.g., *"reads like a transcript"*, *"defensive justification of revisions"*), pair with role-anchoring ("the prose has session-leakage to remove from itself, not topics to add"), or fall back to generic editorial review.
- **As a CLAUDE.md tag in the rule itself**: "session leakage" is a fine name internally; the deployment caveat is about external/standalone use.

Detection paradox worth naming: it is structurally wrong to ask a fresh session to detect session-leakage. The fresh session lacks the session that would produce or reveal the leakage. Branched evaluation is the only direct test; fresh evaluation is at best a fallback for surface-form heuristics.

## Prior art

See [edit-leakage.md](edit-leakage.md) for coverage on the underlying phenomenon (negative parallelism, curse of knowledge, structural priming in LLMs, copy bias in ICL, translationese / *shining through*).

No additional adjacent literature surfaced from this experiment specifically about *naming* the directive or about substrate-induced interpretation drift on technically-overloaded prompts.
