# Nested Style

- Write in Global Style.
- Structure as nested lists.
- Split among H2 blocks.
- Quoted content go in block quotes within the list.
  > Sphinx of black quartz, judge my vow.
- Do not include commentary in quoted content.
  - Bad:
    > > "I'm confident this is accurate" is weak evidence.
  - Good:
    > - Weak evidence:
    >   > I'm confident this is accurate
- Each point is one short clause at most.
- Break up compound predicates.
  - Bad:
    > - Good technical writing knows its reader, guides action, and improves over time.
  - Good:
    > - Good technical writing
    >   - knows its reader.
    >   - guides action.
    >   - improves over time.
- Avoid item count lead-ins.
  - Bad:
    > - The form comes with two things.
    >   - ...
  - Good:
    > - The form comes with
    >   - ...
- Punctuation:
  - End ideas with periods.
  - End labels with colons.
  - End fragments with nothing.

## Inline Form

- Descend with `{`.
- Separate siblings with `|`.
- Close with `}`.
- Examples:
  > Good technical writing { knows its reader. | guides action. | improves over time. }
  > Instructions as reasoning: { Trust framing finds more. { > 59% more hidden issues } | Fear framing does nothing. }
- Single line code comments should be written in this form.

## Motivation

- Ordinary paragraphs hide their structure.
  - Sequential clauses flatten the hierarchy.
  - Glosses inline fine details.
  - Interruptions break up clauses.
- A fully expanded outline makes structure first-class.
  - Each point is one idea.
- This pays off on the first write.
  - It puts information first.
  - It strips down narration.
- The form comes with
  - progressive disclosure.
  - summarization.
- It streamlines line editing.
  - Each point is an idea you engage directly.
  - Points are easy to add, remove, and rearrange.
