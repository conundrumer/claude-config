# Suppressing edit-context leakage via a CLAUDE.md rule

An experiment on whether a short CLAUDE.md-style rule suppresses Claude's tendency to leave residue of the prior version inside an edited artifact.

## The bug

When Claude edits a prose file, the output often contains traces of what was replaced: negative parallels against removed content ("Y, not X"), preserved scaffolding that lost its referent, diff-narration describing the edit from within the artifact. Examples from one real workshopping session of the `second-opinion` skill:

- `**`auditor`** — ... Produces findings; does not decide next round.` — contrast against a newly-introduced `judge` role the reader already sees alongside.
- `**`referee`** — ... Impartial procedural call, not content judgment.` — reintroduced after the user cut the prior "does not decide next round" clause. Same pattern, same turn.
- `No override` — two-word fragment left behind after its explaining parenthetical was cut.
- Whole paragraphs explaining *why* the architecture changed, inside the skill doc a future reader will consult without the diff.

The user who notices this is tracking cruft at a finer grain than the median reader. The pattern is common enough to survive into shipped skills.

## Why

Claude is generating the edit with the prior version sitting in its context. Salience biases toward preservation: content that's in the window is likely to survive generation. "Y, not X" is the diff surfacing inside the artifact. A special case of the curse of knowledge (Pinker, *The Sense of Style*, 2014) — the writer can't un-know what they just read. Same surface form as negative parallelism (ai-lint rule #9), but the trigger is editing context, not RLHF-learned rhetorical habit. No standard name in the writing or prompting literature.

## Question

Can a short instruction — the kind that would live in a CLAUDE.md — suppress it? Does the existing sentence-level negative-parallelism rule (`State claims directly. Only use contrast structures... when ruling out a real alternative`) already cover this, or is a new rule needed?

## Setup

**Seed file.** `composition.md` at v6 from `~/.claude/file-history/d0cf1cff-4061-4d20-ac95-1a0bac92f328/bffc3dd94a7be0b1@v6` — the state just before the session's line-714 edit, with `auditor` defined but no `judge` yet.

**Prompt.** Single turn:

> Let's add a new `judge` role in composition.md that takes the round-continuation decision out of auditor. The judge classifies audit findings — attack on new terrain vs rehash of joints already fought — and says continue or terminate.

**Environment.** `claude -p --model opus --permission-mode auto --allowedTools "Read Edit Write"`, with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Scratch dir in `/tmp/` to keep project CLAUDE.md out. Pre-edit snapshot copy kept outside the scratch dir so the child session doesn't see a `composition.v0.md` and infer "iteration history."

**Measurement.** Manual inspection of the `diff v0 → v1`. Two scores per trial:

1. **New leakage on `auditor`.** Did the edit append a negative parallel to the pre-existing auditor description to contrast against the new `judge` sibling? (Yes = LEAK, no = clean.)
2. **Pre-existing contrast cleanup.** v0's `recurse-until-resolved` block ends with `"... irreducible-primitive residue is audit finding no productive terrain, not a distinct output"`. Did the edit rewrite the `"not a distinct output"` contrast, or preserve it verbatim?

## Variants

**V0 — control.** Global `~/.claude/CLAUDE.md` loads (including the existing sentence-level negative-parallelism rule); no project CLAUDE.md.

**V1 — rule.** Global + a project CLAUDE.md dropped into the scratch dir:

> When editing a file, the output must stand alone. Don't preserve references to removed content: no "does not X" clauses distinguishing the new version from the old, no concessions to prior framings, no diff-narration inside the artifact.
>
> BAD: `// Uses the Merge strategy now, not the Split strategy we used before.`
> (the "not the Split strategy" clause references removed code; the reader of the comment has no reason to know about the prior implementation.)
>
> GOOD: `// Uses the Merge strategy.`

The BAD/GOOD example uses code comments, a different domain from the skill-role editing task. An earlier draft used the exact leakage phrase from the baseline run (`"Does not itself attack or synthesize"`) and had to be replaced — otherwise a clean intervention result couldn't distinguish rule generalization from trivial phrase-avoidance.

## Results

N=3 per condition.

| Condition | New leakage on auditor | v0 "not a distinct output" |
|---|---|---|
| V0 control 1 | LEAK — "Reports findings; does not rule on whether the dialectic continues." | preserved |
| V0 control 2 | LEAK — "Does not decide whether to continue — that is the judge's call." | preserved |
| V0 control 3 | LEAK — "Reports findings; does not decide whether the dialectic continues." | preserved |
| V1 rule 1 | clean | preserved |
| V1 rule 2 | clean | preserved |
| V1 rule 3 | clean | restructured, dropped |

**Primary bug:** V0 3/3 LEAK. V1 0/3 LEAK.
**Pre-existing contrast cleanup:** V0 0/3 cleaned. V1 1/3 cleaned.

### Lexical stability of the control bug

The three V0 outputs are almost lexically identical at the leakage site. Two of three begin with `"Reports findings"`; all three use `"does not decide/rule"` in the same structural position. The failure mode is template-level — the model reaches into the same phrasal template each time, not a randomly-varied cruft generator.

### Real-session precedent

The original session (`d0cf1cff-4061-4d20-ac95-1a0bac92f328.jsonl`) captured the same pattern under natural workshopping: after the user said `"this is not necessary"` about `"Produces findings; does not decide next round."`, the next edit added `"Impartial procedural call, not content judgment."` on the renamed `referee` role. Explicit correction in the prior turn didn't carry forward. Five instances like this in that session, clustering exclusively in skill-file edits.

## Takeaways

**The rule prevents the primary bug reliably.** N=3/3 clean vs 3/3 leak is tight for a single-prompt trial. Global CLAUDE.md alone — which already contains the sentence-level negative-parallelism rule — failed to suppress the edit-context variant. The two patterns are structurally related but the general rule doesn't cover the edit-triggered case.

**Inherited contrast gets cleaned only sometimes.** V1 rewrote v0's preserved `"not a distinct output"` clause in 1/3 trials. The rule's phrasing targets "removed content"; content being kept in the edit is ambiguously in scope. A separate mechanism (ai-lint post-edit pass, explicit revision trigger, or an expanded rule covering adjacent preserved content) would address this.

**Example domain matters.** The initial V1 draft used a BAD example lifted verbatim from the baseline output. That version appeared to suppress leakage, but couldn't distinguish generalization from phrase-avoidance. Moving the example to code comments — same pattern, different domain — showed the rule still suppresses skill-file leakage. The rule generalizes across shape, not just phrase.

**The bug is context-dependent.** Clean-room kombucha one-shots and simple multi-turn file edits ("update to reflect this") didn't reproduce it. Repro needed: structural role-density (definitions in terms of sibling relationships), iterative refinement with rationale in conversation, and skill-file prose shapes. Synthetic prose doesn't have these.

**Chat-commentary leakage is untreated.** In every V1 trial the artifact stayed clean while Claude's chat response still narrated the diff (`"rewrote X so Y"`, `"shifted the continuation call out of auditor"`). The rule targets the file, not the chat. Separate follow-up — probably not suppressible by a rule scoped to editing.

## Caveats

- One seed file, one prompt, one edit shape (role-split with a sibling). Other edit shapes — diff narration in longer prose, cross-span scaffolding, code-comment fixes — weren't tested separately. The seed is a skill file where the bug is most visible; effects on other file types are untested.
- N=3. Within-condition consistency is tight (3/3 on both sides of the primary score), but the between-condition gap isn't statistically characterized and the cleanup-rate comparison (0/3 vs 1/3) is within noise.
- "Control" isn't zero-config. Global CLAUDE.md with the sentence-level negative-parallelism rule loads in both conditions. That's the correct matched control for measuring the project rule's marginal effect, not an absolute baseline.
- Manual scoring. The primary bug is binary and unambiguous across all six trials. The "restructured, dropped" call on V1 trial 3 is a judgment — Claude rewrote the block into a different structure without the contrast clause, which counts as cleanup.
- Not tested: long conversations where the rule's grip may decay across turns, interaction with other CLAUDE.md content, whether the rule regresses on edits that legitimately require contrast.

## Landed rule

Added to `global-claude.md` (syncs to `~/.claude/CLAUDE.md`):

```
When editing a file, the output must stand alone. Don't preserve references to removed content: no "does not X" clauses distinguishing the new version from the old, no concessions to prior framings, no diff-narration inside the artifact.

BAD: "// Uses the Merge strategy now, not the Split strategy we used before."
(the "not the Split strategy" clause references removed code; the reader of the comment has no reason to know about the prior implementation.)

GOOD: "// Uses the Merge strategy."
```

Expected: edits stop introducing negative parallels against replaced content. Pre-existing contrast in preserved content sometimes gets cleaned; inherited cleanup is a separate problem.

## Follow-up — session leakage

A sibling failure mode surfaced later: leakage from the *conversation* that produced the file, not from a prior version of the file. A shipped subagent role file (`skills/second-opinion/roles/advocate.md`) contained:

> No need to list claims, joints, or assign IDs — extraction is post-hoc.

A subagent loaded with only that file has no antecedent for "claims," "joints," "IDs," or "extraction." Those terms live in sibling role files the subagent never sees, and the "no need to" negates an alternative the author considered mid-session, not one the reader is considering. Same surface form as edit-leakage's `does-not-X` clauses; different trigger — chat context rather than prior-artifact context. Fires on writes (no prior version exists) and can co-fire with edit-leakage on edits.

The original rule was scoped to "removed content," which doesn't cover content that was never in the file. Rule generalized to two leak sources sharing one principle — *the reader has neither the prior version nor the conversation that produced it*:

```
When editing or writing a file, the output must stand alone. The reader has neither the prior version nor the conversation that produced it. Don't surface either:

- From the prior version (edits only): no "does not X" clauses against removed content, no concessions to prior framings, no diff-narration.
- From the session: no "no need to X" against alternatives you considered, no vocabulary from sibling files this one doesn't introduce, no meta-commentary about a surrounding system.
```

Not separately experimentally validated. The edit-leakage half was tested at N=3/3; the session-leakage half rides on the same mechanism (in-context content surfacing into output) and the same intervention shape, but doesn't have its own A/B run yet.

## Prior art

No standard name for this specific phenomenon. A research sweep across writing-craft literature (Strunk & White, Williams *Style*, Zinsser *On Writing Well*), cognitive science (Tversky & Kahneman on anchoring, Pinker on *curse of knowledge*), and LLM prompt engineering returned no dedicated term. The surface form is a case of negative parallelism; the causal mechanism is context salience biasing generation toward preservation of in-context content.

A second pass surfaced closer adjacencies than curse of knowledge:

- Translation studies: *shining through* / *translationese* (Teich 2003; Gellerstam 1986) for source-language traces in target-language output. The tightest analog, proposed mechanism is cross-linguistic structural priming (Jacob et al., *Applied Psycholinguistics*).
- Structural priming in LLMs (Sinclair et al., TACL 2022) gives the salience-preserves-context story LLM-specific evidence: cumulative, recency-sensitive, boosted by lexico-semantic overlap.
- Copy bias in ICL (Zhang et al., arXiv 2410.01288, 2024): "copying neurons" preferentially reproduce in-context content — same failure mode at circuit level.
- *Palimpsest* is the closest writing-craft metaphor.

Recent coder discourse (2025–2026) observes the bug but files it under "AI over-commenting." Textbook instance: Cursor forum, *How to tell the model not write unnecessary comments* (June 2025) — Claude renames `Button()` to `ButtonWithAnimation()` and inserts `// drawButton (added Scale Animation)`. HN threads on agentic-code slop cluster the same way. Wikipedia's *Signs of AI writing* (public September 2025, WikiProject AI Cleanup) catalogs ~35 AI-generation tells — em-dashes, clichés, promotional language — without covering edit residue. Code makes the bug visible because diffs get line-by-line review; the prose-editing community has no named complaint for it.
