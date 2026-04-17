# ai-lint

Subtractive linter for AI-generated writing. Edits existing text to remove compulsive AI-writing patterns. Strictly subtractive — does not add voice, personality, rhythm, or content.

## Scope

`ai-lint` is a linter, not a style guide. It targets patterns that LLMs compulsively produce, catalogued from observation of real AI output. It does not teach writing; it removes specific tics. Legitimate, deliberate, or structural uses of the same patterns are preserved.

## Attribution

This skill is derived from [blader/humanizer](https://github.com/blader/humanizer) (MIT), which is itself based on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup.

## License

MIT, matching upstream.

## Relationship to upstream (humanizer)

Rule numbering (1–29) matches humanizer for mechanical diffability against future upstream releases.

### Rules omitted

| # | Rule | Reason |
|---|---|---|
| 17 | Title case in headings | Pure style-guide convention (sentence case vs. title case). Not a writing-quality issue. |
| 19 | Curly quotation marks | Typographically correct in professional publishing. Flagged upstream only as an AI-origin tell, not a quality issue. |
| 26 | Hyphenated compound-modifier removal | Upstream recommends de-hyphenating compound modifiers (e.g., "cross-functional" → "cross functional") as a human-sounding tell. This violates standard grammar (Chicago §7.85, AP, AMA). Evasion-oriented; degrades correctness. |

### Rules narrowed

Upstream rules kept in `ai-lint` but scoped more tightly, targeting only the compulsive, empty, or mechanical version:

| # | Upstream target | ai-lint target |
|---|---|---|
| 6 | "Challenges / Future Prospects sections" | vague filler version only; specific limitations/objections sections preserved |
| 8 | Copula avoidance generally | cases where `is` would suffice; mechanism-verbs ("serves as a biomarker") preserved |
| 13 | Passive voice and subjectless fragments | subjectless fragments only; passive voice is not a rule |
| 15 | Boldface overuse | non-structural/decorative bolding; first-use bolding of defined terms preserved |
| 16 | Inline-header vertical lists | mechanical use in essay-style prose; release notes, reference docs, feature matrices preserved |
| 21 | Knowledge-cutoff disclaimers | vague disclaimers; calibrated specificity (n, CI, date, source) preserved |
| 28 | Signposting | empty/vacuous signposting; substantive academic/tutorial signposting preserved |

### Rules added (flag-only behaviors)

Upstream removes patterns. `ai-lint` also *flags* patterns whose fix requires information the text does not supply:

- **Unsourced claims** (extends #5): factual or contested claims without attribution are flagged for the author to supply citations.
- **Uncalibrated hedges** (extends #21): vague uncertainty without count, date, confidence, or source is flagged.

Flags are reported in a dedicated `Flags` section of the output. The linter does not fabricate sources or numbers.

### Sections omitted

- `PERSONALITY AND SOUL` — upstream adds voice, opinions, first-person, rhythm variation. Out of scope for a subtractive linter. `ai-lint` does not inject content.
- `Voice Calibration` — same reason. This is generation-time style, not editing.

## Versioning

`ai-lint` tracks its own version independent of upstream. Upstream humanizer version at the time of fork: 2.5.1.

## Updating against upstream

When humanizer releases updates:

1. Diff the new upstream `SKILL.md` against the last-synced version.
2. For each added rule: decide whether it fits `ai-lint`'s subtractive scope. If yes, add under the same number. If it's evasion-only or style-only, omit and note in this README.
3. For each modified rule: apply the same tightening/framing decisions.
4. Update version and note the upstream version synced against.
