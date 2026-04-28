#!/usr/bin/env python3
"""Generate threads.md for a recursive-dialectic round.

Reads round-<n>/{synth-threads.md, auditor.md, moderator.md} plus
round-<n-1>/threads.md (if present), computes the live thread set, mints
T-IDs, and writes round-<n>/threads.md per the moderator role spec.

Usage: gen-threads.py <round-dir>

Run after the moderator has written its classifications to moderator.md.
"""

import re
import sys
from pathlib import Path


def read_file(path):
    try:
        return path.read_text()
    except (FileNotFoundError, IsADirectoryError):
        return None


def split_sections(text, level):
    """Split markdown by headings at the given level. Returns [(heading, body), ...]."""
    if not text:
        return []
    pattern = re.compile(rf'^{"#" * level} (.+?)\s*$', re.MULTILINE)
    matches = list(pattern.finditer(text))
    out = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((m.group(1).strip(), text[start:end].strip()))
    return out


def parse_bullet(body, key):
    """Match `- key: value` on a single line. The [ \\t] class keeps the regex
    from spanning newlines, which would let an empty `- key:` slurp the next
    paragraph in MULTILINE mode."""
    m = re.search(rf'^- {re.escape(key)}:[ \t]*(.+?)[ \t]*$', body, re.MULTILINE)
    return m.group(1).strip() if m else None


def parse_synth_threads(path):
    """Return (new_threads, dispositioned).

    new_threads: list of {sid, label, content, succeeds} dicts in declaration
        order. sid is the `r<n>-S-th<k>` declaration ID (used as origin in
        threads.md when the moderator mints a T-ID).
    dispositioned: set of T-IDs the synth disposed this round.
    """
    text = read_file(path)
    if text is None:
        sys.exit(f"Missing {path}")
    new_threads = []
    dispositioned = set()
    for heading, body in split_sections(text, 2):
        h = heading.lower()
        if h.startswith('new threads'):
            for sub_heading, sub_body in split_sections(body, 3):
                if not re.match(r'^r\d+-S-th\d+$', sub_heading):
                    continue
                new_threads.append({
                    'sid': sub_heading,
                    'label': parse_bullet(sub_body, 'label') or '',
                    'content': extract_prose(sub_body),
                    'succeeds': parse_bullet(sub_body, 'succeeds'),
                })
        elif h.startswith('disposition'):
            for sub_heading, _ in split_sections(body, 3):
                m = re.match(r'(T\d+)', sub_heading)
                if m:
                    dispositioned.add(m.group(1))
    return new_threads, dispositioned


def extract_prose(sub_body):
    """Strip - key: value bullet lines; return what's left (the prose argument)."""
    lines = sub_body.splitlines()
    prose_lines = [ln for ln in lines if not re.match(r'^-\s+\w+:', ln)]
    return '\n'.join(prose_lines).strip()


def parse_auditor(path):
    """Return (promoting, tracked_drops).

    promoting: {O-ID: {label, content, succeeds}} for promoting objections —
        these mint a new T-ID when classified LIVE. `content` is the prose
        argument, transcribed verbatim as the new thread's content.
    tracked_drops: {O-ID: T-ID} for drops anchored on tracked threads —
        these don't mint new T-IDs but, when classified LIVE, override the
        synth's disposition of that thread (the thread stays live).
    """
    text = read_file(path)
    if text is None:
        sys.exit(f"Missing {path}")
    promoting = {}
    tracked_drops = {}
    for heading, body in split_sections(text, 2):
        if not heading.lower().startswith('objections'):
            continue
        for sub_heading, sub_body in split_sections(body, 3):
            m = re.match(r'(O\d+)', sub_heading)
            if not m:
                continue
            oid = m.group(1)
            kind = parse_bullet(sub_body, 'kind')
            anchor = parse_bullet(sub_body, 'anchor')
            if kind == 'drop' and anchor and re.match(r'^T\d+$', anchor.strip()):
                tracked_drops[oid] = anchor.strip()
                continue
            is_promoting = (
                kind in {'smuggle', 'self_defeat'}
                or (kind == 'drop' and anchor)
            )
            if not is_promoting:
                continue
            promoting[oid] = {
                'label': parse_bullet(sub_body, 'label'),
                'content': extract_prose(sub_body),
                'succeeds': parse_bullet(sub_body, 'succeeds'),
            }
    return promoting, tracked_drops


def parse_moderator(path):
    text = read_file(path)
    if text is None:
        sys.exit(f"Missing {path} — write moderator.md classifications before running this script")
    classifications = {}
    for heading, body in split_sections(text, 2):
        if not heading.lower().startswith('classifications'):
            continue
        for sub_heading, sub_body in split_sections(body, 3):
            m = re.match(r'(O\d+)', sub_heading)
            if not m:
                continue
            status = parse_bullet(sub_body, 'status')
            if status:
                classifications[m.group(1)] = status.strip()
    return classifications


def parse_prior_threads(path):
    """Return (next_t_id, {T-ID: {body}}). (1, {}) if path missing.

    Body is the entire entry content (bullets + content paragraph), preserved
    verbatim for re-emission in the next round's threads.md.
    """
    text = read_file(path)
    if text is None:
        return 1, {}
    nm = re.search(r'^- next_t_id:\s*T(\d+)\s*$', text, re.MULTILINE)
    prior = {}
    for heading, body in split_sections(text, 3):
        hm = re.match(r'^(T\d+)\s*$', heading)
        if not hm:
            continue
        prior[hm.group(1)] = {'body': body.strip()}
    if nm:
        next_t_id = int(nm.group(1))
    elif prior:
        next_t_id = max(int(t[1:]) for t in prior) + 1
    else:
        next_t_id = 1
    return next_t_id, prior


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: gen-threads.py <round-dir>")
    round_dir = Path(sys.argv[1]).resolve()
    if not round_dir.is_dir():
        sys.exit(f"Not a directory: {round_dir}")
    rm = re.search(r'round-(\d+)', round_dir.name)
    if not rm:
        sys.exit(f"Round dir must be named round-N: {round_dir}")
    n = int(rm.group(1))
    prior_dir = round_dir.parent / f'round-{n - 1}'

    new_threads, dispositioned = parse_synth_threads(round_dir / 'synth-threads.md')
    promoting, tracked_drops = parse_auditor(round_dir / 'auditor.md')
    classifications = parse_moderator(round_dir / 'moderator.md')
    next_id, prior_threads = parse_prior_threads(prior_dir / 'threads.md')

    # A LIVE drop anchored on a dispositioned thread overrides the disposition.
    kept_live = {
        t for oid, t in tracked_drops.items()
        if classifications.get(oid) == 'LIVE'
    }
    live = set(prior_threads.keys()) - (dispositioned - kept_live)

    # Mint T-IDs: synth-introduced first (declaration order), then LIVE-promoting
    # objections in O-ID order. RESOLVED-promoting objections get no T-ID.
    minted = []
    for nt in new_threads:
        minted.append((f'T{next_id}', 'synth', nt))
        next_id += 1
    live_promoting = sorted(
        (oid for oid in promoting if classifications.get(oid) == 'LIVE'),
        key=lambda x: int(x[1:]),
    )
    for oid in live_promoting:
        minted.append((f'T{next_id}', 'auditor', {'oid': oid, **promoting[oid]}))
        next_id += 1

    entries = {}
    for t in live:
        entries[t] = f'### {t}\n\n{prior_threads[t]["body"]}'
    for t, src, d in minted:
        origin = d['sid'] if src == 'synth' else f'r{n}-O-{d["oid"][1:]}'
        lines = [
            f'### {t}',
            '',
            f'- label: {d["label"]}',
            f'- origin: {origin}',
            f'- introduced: r{n}',
        ]
        if d.get('succeeds'):
            lines.append(f'- succeeds: {d["succeeds"]}')
        lines += ['', d['content']]
        entries[t] = '\n'.join(lines)

    ordered = sorted(entries.keys(), key=lambda t: int(t[1:]))
    out_lines = [f'- next_t_id: T{next_id}', '']
    for t in ordered:
        out_lines.append(entries[t])
        out_lines.append('')
    output = '\n'.join(out_lines).rstrip() + '\n'

    out_path = round_dir / 'threads.md'
    out_path.write_text(output)
    print(f"Wrote {out_path} ({len(ordered)} live threads, next_t_id: T{next_id})")


if __name__ == '__main__':
    main()
