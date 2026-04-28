#!/usr/bin/env python3
"""Validate dialectic markdown artifacts against current spec.

Usage:
    validate.py <role> <file-path> [--letter A|B] [--round N]

Roles: advocate, advocate-moves
(More roles added as the trial uncovers them.)

Exits 0 on PASS, 1 on FAIL with violations to stdout.
"""
import argparse
import re
import sys

ADVOCATE_TITLE = re.compile(r"^# Advocate (A|B) — Round (\d+)$")
ADVOCATE_MOVES_TITLE = re.compile(r"^# Advocate (A|B) Moves — Round (\d+)$")
SYNTH_TITLE = re.compile(r"^# Synthesizer — Round (\d+)$")
SYNTH_THREADS_TITLE = re.compile(r"^# Synth Threads — Round (\d+)$")
SYNTH_MOVES_TITLE = re.compile(r"^# Synth Moves — Round (\d+)$")
AUDITOR_TITLE = re.compile(r"^# Auditor — Round (\d+)$")
AUDITOR_MOVES_TITLE = re.compile(r"^# Auditor Moves — Round (\d+)$")
MODERATOR_TITLE = re.compile(r"^# Moderator — Round (\d+)$")
SYNTH_THREAD_INTRO_ID = re.compile(r"^r(\d+)-S-th(\d+)$")
MOVE_ID = re.compile(r"^r(\d+)-(A|B)-mv(\d+)$")
PARAGRAPH_ID = re.compile(r"^r(\d+)-(A|B)-(\d+)\.(\d+)$")
CLAIM_ID = re.compile(r"^r(\d+)-S-(\d+)$")
THREAD_ID = re.compile(r"^T(\d+)$")
OBJECTION_ID = re.compile(r"^O(\d+)$")
OBJECTION_REF = re.compile(r"^r(\d+)-O-(\d+)$")
SECTION_ID = re.compile(r"^r(\d+)-(A|B)-(\d+)$")
NUMBERED_HEADING = re.compile(r"^(\d+)\.\s+(.+)$")


def first_nonempty(lines):
    for line in lines:
        if line.strip():
            return line.strip()
    return None


def parse_h2_h3_tree(lines):
    """Return list of {name, h3s: [{name, prose_lines, prose, bullets: {k:v}}], prose_lines, prose, bullets}."""
    sections = []
    cur_h2 = None
    cur_h3 = None
    in_code = False
    for line in lines:
        if re.match(r"^```", line):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^## (.+)$", line)
        if m:
            cur_h2 = {"name": m.group(1).strip(), "h3s": [], "prose_lines": 0, "prose": "", "bullets": {}}
            sections.append(cur_h2)
            cur_h3 = None
            continue
        m = re.match(r"^### (.+)$", line)
        if m and cur_h2 is not None:
            cur_h3 = {"name": m.group(1).strip(), "prose_lines": 0, "prose": "", "bullets": {}}
            cur_h2["h3s"].append(cur_h3)
            continue
        m = re.match(r"^-\s+([\w_]+):\s*(.*)$", line)
        if m:
            target = cur_h3 if cur_h3 is not None else cur_h2
            if target is not None:
                target["bullets"][m.group(1)] = m.group(2).strip()
            continue
        if line.strip():
            target = cur_h3 if cur_h3 is not None else cur_h2
            if target is not None:
                target["prose_lines"] += 1
                target["prose"] += line + "\n"
    return sections


def split_csv(s):
    return [p.strip() for p in s.split(",") if p.strip()]


def split_id_csv(s):
    """Split a comma-separated list of IDs that may carry trailing parenthetical
    glosses, e.g. `r1-A-mv2 (some, gloss)`. Returns (bare_ids, glossed_count).
    Respects parens so commas inside a gloss don't split the value."""
    parts = []
    cur = ""
    depth = 0
    for ch in s:
        if ch == "(":
            depth += 1
            cur += ch
        elif ch == ")":
            depth = max(0, depth - 1)
            cur += ch
        elif ch == "," and depth == 0:
            if cur.strip():
                parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    bare = []
    glossed = 0
    for p in parts:
        m = re.match(r"^(\S+?)\s*\(.*\)\s*$", p)
        if m:
            bare.append(m.group(1))
            glossed += 1
        else:
            bare.append(p)
    return bare, glossed


def validate_advocate(text, expected_letter=None, expected_round=None):
    V = []
    lines = text.splitlines()
    title = first_nonempty(lines)
    if not title:
        return ["file is empty"]
    m = ADVOCATE_TITLE.match(title)
    if not m:
        return [f"title malformed: expected '# Advocate <A|B> — Round <n>', got {title!r}"]
    letter, round_n = m.group(1), int(m.group(2))
    if expected_letter and letter != expected_letter:
        V.append(f"title says Advocate {letter}, expected {expected_letter}")
    if expected_round and round_n != expected_round:
        V.append(f"title says Round {round_n}, expected {expected_round}")

    sections = parse_h2_h3_tree(lines)
    if not sections:
        V.append("no ## H2 sections")
        return V
    if sections[-1]["name"] != "Root":
        V.append(f"last ## section must be 'Root', got {sections[-1]['name']!r}")
    root = sections[-1]
    if root["h3s"]:
        V.append(f"## Root must not have ### subsections (has {len(root['h3s'])})")
    if root["prose_lines"] == 0:
        V.append("## Root has no prose")

    body_sections = sections[:-1]
    if not body_sections:
        V.append("no body H2 before ## Root")
    for h2 in body_sections:
        if not h2["h3s"]:
            V.append(f"## {h2['name']!r}: no ### numbered subsections")
            continue
        for k, h3 in enumerate(h2["h3s"], start=1):
            mh3 = NUMBERED_HEADING.match(h3["name"])
            if not mh3:
                V.append(f"### {h3['name']!r}: not numbered '{k}. <title>'")
                continue
            if int(mh3.group(1)) != k:
                V.append(f"### {h3['name']!r}: number {mh3.group(1)} out of sequence (expected {k})")
            if h3["prose_lines"] == 0:
                V.append(f"### {h3['name']!r}: no prose")
    return V


def validate_advocate_moves(text, expected_letter=None, expected_round=None):
    V = []
    W = []
    lines = text.splitlines()
    title = first_nonempty(lines)
    if not title:
        return ["file is empty"], W
    m = ADVOCATE_MOVES_TITLE.match(title)
    if not m:
        return [f"title malformed: expected '# Advocate <A|B> Moves — Round <n>', got {title!r}"], W
    letter, round_n = m.group(1), int(m.group(2))
    if expected_letter and letter != expected_letter:
        V.append(f"title says Advocate {letter}, expected {expected_letter}")
    if expected_round and round_n != expected_round:
        V.append(f"title says Round {round_n}, expected {expected_round}")

    sections = parse_h2_h3_tree(lines)
    moves_sec = next((s for s in sections if s["name"] == "Moves"), None)
    if not moves_sec:
        V.append("missing ## Moves")
        return V, W
    if not moves_sec["h3s"]:
        V.append("## Moves: no ### entries")
        return V, W

    for k, h3 in enumerate(moves_sec["h3s"], start=1):
        eid = h3["name"]
        m = MOVE_ID.match(eid)
        if not m:
            V.append(f"move id malformed: {eid!r}")
            continue
        n, l, mvk = int(m.group(1)), m.group(2), int(m.group(3))
        if expected_round and n != expected_round:
            V.append(f"{eid}: round mismatch (expected r{expected_round}-...)")
        if expected_letter and l != expected_letter:
            V.append(f"{eid}: letter mismatch (expected {expected_letter})")
        if mvk != k:
            V.append(f"{eid}: mv-index out of sequence (expected mv{k})")

        bul = h3["bullets"]
        if not bul.get("label"):
            V.append(f"{eid}: missing - label:")
        if not bul.get("spans"):
            V.append(f"{eid}: missing - spans:")
        else:
            for s in split_csv(bul["spans"]):
                ms = PARAGRAPH_ID.match(s)
                if not ms:
                    V.append(f"{eid}: spans element {s!r} not a paragraph id")
                    continue
                sn, sl = int(ms.group(1)), ms.group(2)
                if expected_round and sn != expected_round:
                    V.append(f"{eid}: spans element {s!r} round mismatch")
                if expected_letter and sl != expected_letter:
                    V.append(f"{eid}: spans element {s!r} letter mismatch")
        if expected_round == 1:
            if "derives_from" in bul:
                V.append(f"{eid}: derives_from on round-1 move (no prior round)")
            if "responds_to" in bul:
                V.append(f"{eid}: responds_to on round-1 move (no prior round)")
            if "engages" in bul:
                V.append(f"{eid}: engages on round-1 move (no prior threads)")
        else:
            for key in ("derives_from", "responds_to"):
                if key not in bul:
                    continue
                refs, glossed = split_id_csv(bul[key])
                if glossed:
                    W.append(f"{eid}: {key} has {glossed} inline gloss(es); bare ids only — put explanation in the rationale paragraph")
                for ref in refs:
                    if key == "derives_from":
                        mr = MOVE_ID.match(ref)
                        if not mr:
                            V.append(f"{eid}: derives_from element {ref!r} not a move id")
                            continue
                        rn, rl = int(mr.group(1)), mr.group(2)
                        if rn >= round_n:
                            V.append(f"{eid}: derives_from {ref!r} must be a prior-round move (round_n={round_n})")
                        if rl != letter:
                            V.append(f"{eid}: derives_from {ref!r} must be same advocate")
                    else:  # responds_to — accepts move-id (opposite advocate) or claim-id, dispatched by shape
                        mr = MOVE_ID.match(ref)
                        cm = CLAIM_ID.match(ref)
                        if mr:
                            rn, rl = int(mr.group(1)), mr.group(2)
                            if rn >= round_n:
                                V.append(f"{eid}: responds_to {ref!r} must be a prior-round move (round_n={round_n})")
                            if rl == letter:
                                V.append(f"{eid}: responds_to {ref!r} must be opposite advocate")
                        elif cm:
                            rn = int(cm.group(1))
                            if rn >= round_n:
                                V.append(f"{eid}: responds_to {ref!r} must be a prior-round claim (round_n={round_n})")
                        else:
                            V.append(f"{eid}: responds_to element {ref!r} not a move id or claim id")
            if "engages" in bul:
                refs, glossed = split_id_csv(bul["engages"])
                if glossed:
                    W.append(f"{eid}: engages has {glossed} inline gloss(es); bare T-ids only — put explanation in the rationale paragraph")
                for ref in refs:
                    if not THREAD_ID.match(ref):
                        V.append(f"{eid}: engages element {ref!r} not a T-id")
    return V, W


def validate_synth(text, expected_letter=None, expected_round=None):
    del expected_letter  # not applicable to synth roles
    V = []
    lines = text.splitlines()
    title = first_nonempty(lines)
    m = SYNTH_TITLE.match(title or "")
    if not m:
        return [f"title malformed: expected '# Synthesizer — Round <n>', got {title!r}"]
    round_n = int(m.group(1))
    if expected_round and round_n != expected_round:
        V.append(f"title says Round {round_n}, expected {expected_round}")

    sections = parse_h2_h3_tree(lines)
    sm = next((s for s in sections if s["name"] == "Structural move"), None)
    if not sm:
        V.append("missing ## Structural move")
    else:
        if len(sm["h3s"]) != 1:
            V.append(f"## Structural move: must have exactly 1 entry, got {len(sm['h3s'])}")
        if sm["h3s"]:
            h3 = sm["h3s"][0]
            expected_id = f"r{round_n}-S-0"
            if h3["name"] != expected_id:
                V.append(f"## Structural move: entry must be {expected_id!r}, got {h3['name']!r}")
            if not h3["bullets"].get("move_label"):
                V.append("## Structural move: missing - move_label:")
            if h3["prose_lines"] == 0:
                V.append("## Structural move: missing prose")

    nc = next((s for s in sections if s["name"] == "New claims"), None)
    if not nc:
        V.append("missing ## New claims")
    else:
        if not nc["h3s"]:
            V.append("## New claims: no entries")
        for k, h3 in enumerate(nc["h3s"], start=1):
            cm = CLAIM_ID.match(h3["name"])
            if not cm:
                V.append(f"## New claims: malformed claim id {h3['name']!r}")
                continue
            n, idx = int(cm.group(1)), int(cm.group(2))
            if expected_round and n != expected_round:
                V.append(f"## New claims/{h3['name']}: round mismatch")
            if idx != k:
                V.append(f"## New claims/{h3['name']}: index out of sequence (expected r{round_n}-S-{k})")
            if h3["prose_lines"] == 0:
                V.append(f"## New claims/{h3['name']}: missing prose")
    return V


def validate_synth_threads(text, expected_letter=None, expected_round=None):
    del expected_letter
    V = []
    lines = text.splitlines()
    title = first_nonempty(lines)
    m = SYNTH_THREADS_TITLE.match(title or "")
    if not m:
        return [f"title malformed: expected '# Synth Threads — Round <n>', got {title!r}"]
    round_n = int(m.group(1))
    if expected_round and round_n != expected_round:
        V.append(f"title says Round {round_n}, expected {expected_round}")

    sections = parse_h2_h3_tree(lines)
    section_names = [s["name"] for s in sections]
    if "New threads" not in section_names:
        V.append("missing ## New threads")
    nt = next((s for s in sections if s["name"] == "New threads"), None)
    if nt:
        for k, h3 in enumerate(nt["h3s"], start=1):
            tid = h3["name"]
            tm = SYNTH_THREAD_INTRO_ID.match(tid)
            if not tm:
                V.append(f"## New threads: malformed synth-thread id {tid!r} (expected r<n>-S-th<k>)")
                continue
            n, idx = int(tm.group(1)), int(tm.group(2))
            if expected_round and n != expected_round:
                V.append(f"## New threads/{tid}: round mismatch")
            if idx != k:
                V.append(f"## New threads/{tid}: index out of sequence (expected r{round_n}-S-th{k})")
            if not h3["bullets"].get("label"):
                V.append(f"## New threads/{tid}: missing - label:")
            if h3["prose_lines"] == 0:
                V.append(f"## New threads/{tid}: missing content paragraph")
            sb = h3["bullets"].get("succeeds")
            if sb is not None:
                for p in split_csv(sb):
                    if not THREAD_ID.match(p):
                        V.append(f"## New threads/{tid}: succeeds {p!r} not a T-ID")
                    elif expected_round == 1:
                        V.append(f"## New threads/{tid}: succeeds {p!r} on round-1 (no prior round)")

    disp = next((s for s in sections if s["name"] == "Disposition"), None)
    if disp:
        if expected_round == 1:
            V.append("## Disposition present in round 1 (no prior threads to dispose)")
        for h3 in disp["h3s"]:
            tid = h3["name"]
            if not THREAD_ID.match(tid):
                V.append(f"## Disposition: malformed T-ID {tid!r}")
            action = h3["bullets"].get("action")
            if action not in {"absorbed", "relocated", "retired"}:
                V.append(f"## Disposition/{tid}: invalid action {action!r}")
            if action == "relocated":
                to_ = h3["bullets"].get("to")
                if not to_:
                    V.append(f"## Disposition/{tid}: relocated without - to:")
                else:
                    for p in split_csv(to_):
                        if not CLAIM_ID.match(p):
                            V.append(f"## Disposition/{tid}: to ref {p!r} not a claim id")
                if h3["prose_lines"] == 0:
                    V.append(f"## Disposition/{tid}: relocated without prose rationale")
            if action == "retired" and h3["prose_lines"] == 0:
                V.append(f"## Disposition/{tid}: retired without prose rationale")
    return V


def validate_synth_moves(text, expected_letter=None, expected_round=None):
    del expected_letter
    V = []
    lines = text.splitlines()
    title = first_nonempty(lines)
    m = SYNTH_MOVES_TITLE.match(title or "")
    if not m:
        return [f"title malformed: expected '# Synth Moves — Round <n>', got {title!r}"]
    round_n = int(m.group(1))
    if expected_round and round_n != expected_round:
        V.append(f"title says Round {round_n}, expected {expected_round}")

    sections = parse_h2_h3_tree(lines)
    pc = next((s for s in sections if s["name"] == "Per-claim"), None)
    if not pc:
        V.append("missing ## Per-claim")
    else:
        for h3 in pc["h3s"]:
            cid = h3["name"]
            if not CLAIM_ID.match(cid):
                V.append(f"## Per-claim: malformed claim id {cid!r}")
                continue
            bul = h3["bullets"]
            for key, regex, label in [
                ("seeded_by", MOVE_ID, "move id"),
                ("supported_by", CLAIM_ID, "claim id"),
                ("replaces", CLAIM_ID, "claim id"),
                ("forced_by", OBJECTION_REF, "objection id"),
            ]:
                if key in bul:
                    for ref in split_csv(bul[key]):
                        if not regex.match(ref):
                            V.append(f"## Per-claim/{cid}: {key} ref {ref!r} not a {label}")
            if expected_round == 1:
                if "replaces" in bul:
                    V.append(f"## Per-claim/{cid}: replaces in round 1 (no prior round)")
                if "forced_by" in bul:
                    V.append(f"## Per-claim/{cid}: forced_by in round 1 (no prior round)")

    pt = next((s for s in sections if s["name"] == "Per-thread"), None)
    if pt:
        for h3 in pt["h3s"]:
            label = h3["name"]
            opened = h3["bullets"].get("opened_by")
            if not opened:
                V.append(f"## Per-thread/{label!r}: missing - opened_by:")
            else:
                for ref in split_csv(opened):
                    if not MOVE_ID.match(ref):
                        V.append(f"## Per-thread/{label!r}: opened_by ref {ref!r} not a move id")
    return V


def validate_auditor(text, expected_letter=None, expected_round=None):
    del expected_letter
    V = []
    W = []
    lines = text.splitlines()
    title = first_nonempty(lines)
    m = AUDITOR_TITLE.match(title or "")
    if not m:
        return [f"title malformed: expected '# Auditor — Round <n>', got {title!r}"], W
    round_n = int(m.group(1))
    if expected_round and round_n != expected_round:
        V.append(f"title says Round {round_n}, expected {expected_round}")

    sections = parse_h2_h3_tree(lines)
    obj = next((s for s in sections if s["name"] == "Objections"), None)
    if not obj:
        V.append("missing ## Objections")
        return V, W
    if not obj["h3s"]:
        V.append("## Objections: no entries")
        return V, W

    for k, h3 in enumerate(obj["h3s"], start=1):
        oid = h3["name"]
        om = OBJECTION_ID.match(oid)
        if not om:
            V.append(f"## Objections: malformed O-id {oid!r}")
            continue
        if int(om.group(1)) != k:
            V.append(f"## Objections/{oid}: index out of sequence (expected O{k})")
        bul = h3["bullets"]
        kind = bul.get("kind")
        if kind not in {"drop", "smuggle", "self_defeat"}:
            V.append(f"## Objections/{oid}: invalid or missing kind {kind!r}")
            continue
        if not bul.get("label"):
            V.append(f"## Objections/{oid}: missing - label:")
        if kind == "drop":
            anchor = bul.get("anchor")
            if not anchor:
                V.append(f"## Objections/{oid}: drop missing - anchor:")
            if "target" in bul or "conflicts" in bul:
                V.append(f"## Objections/{oid}: drop has extraneous locator")
        elif kind == "smuggle":
            target_raw = bul.get("target")
            if not target_raw:
                V.append(f"## Objections/{oid}: smuggle missing - target:")
            else:
                targets, glossed = split_id_csv(target_raw)
                if glossed:
                    W.append(f"## Objections/{oid}: target has inline gloss; bare claim-id only — put explanation in the prose argument")
                if len(targets) != 1:
                    V.append(f"## Objections/{oid}: target must be exactly one claim id, got {len(targets)}")
                elif not CLAIM_ID.match(targets[0]):
                    V.append(f"## Objections/{oid}: target {targets[0]!r} not a claim id")
            if "anchor" in bul or "conflicts" in bul:
                V.append(f"## Objections/{oid}: smuggle has extraneous locator")
        elif kind == "self_defeat":
            conflicts_raw = bul.get("conflicts", "")
            parts, glossed = split_id_csv(conflicts_raw)
            if glossed:
                W.append(f"## Objections/{oid}: conflicts has {glossed} inline gloss(es); bare claim-ids only — put explanation in the prose argument")
            if len(parts) < 2:
                V.append(f"## Objections/{oid}: self_defeat conflicts must list ≥2 claims, got {len(parts)}")
            for p in parts:
                if not CLAIM_ID.match(p):
                    V.append(f"## Objections/{oid}: conflicts ref {p!r} not a claim id")
            if "anchor" in bul or "target" in bul:
                V.append(f"## Objections/{oid}: self_defeat has extraneous locator")
        if h3["prose_lines"] == 0:
            V.append(f"## Objections/{oid}: missing prose argument")
        anchor = bul.get("anchor", "")
        drop_promotes = (kind == "drop" and not THREAD_ID.match(anchor))
        promoting = kind in {"smuggle", "self_defeat"} or drop_promotes
        if "succeeds" in bul:
            if not promoting:
                V.append(f"## Objections/{oid}: succeeds only valid for promoting kinds")
            for p in split_csv(bul["succeeds"]):
                if not THREAD_ID.match(p):
                    V.append(f"## Objections/{oid}: succeeds ref {p!r} not a T-ID")
                elif expected_round == 1:
                    V.append(f"## Objections/{oid}: succeeds in round 1 (no prior round)")
    return V, W


def validate_auditor_moves(text, expected_letter=None, expected_round=None):
    del expected_letter
    V = []
    lines = text.splitlines()
    title = first_nonempty(lines)
    m = AUDITOR_MOVES_TITLE.match(title or "")
    if not m:
        return [f"title malformed: expected '# Auditor Moves — Round <n>', got {title!r}"]
    round_n = int(m.group(1))
    if expected_round and round_n != expected_round:
        V.append(f"title says Round {round_n}, expected {expected_round}")

    sections = parse_h2_h3_tree(lines)
    mv = next((s for s in sections if s["name"] == "Move references"), None)
    if mv is None:
        return V  # empty move references valid — agent skipped if no objections cite advocate moves
    for h3 in mv["h3s"]:
        oid = h3["name"]
        if not OBJECTION_ID.match(oid):
            V.append(f"## Move references: malformed O-id {oid!r}")
            continue
        bul = h3["bullets"]
        for key in ("targets", "opens_via"):
            if key in bul:
                for ref in split_csv(bul[key]):
                    if not MOVE_ID.match(ref):
                        V.append(f"## Move references/{oid}: {key} ref {ref!r} not a move id")
        if not ("targets" in bul or "opens_via" in bul):
            V.append(f"## Move references/{oid}: missing - targets: or - opens_via:")
    return V


def validate_moderator(text, expected_letter=None, expected_round=None):
    del expected_letter
    V = []
    lines = text.splitlines()
    title = first_nonempty(lines)
    m = MODERATOR_TITLE.match(title or "")
    if not m:
        return [f"title malformed: expected '# Moderator — Round <n>', got {title!r}"]
    round_n = int(m.group(1))
    if expected_round and round_n != expected_round:
        V.append(f"title says Round {round_n}, expected {expected_round}")

    sections = parse_h2_h3_tree(lines)
    cls = next((s for s in sections if s["name"] == "Classifications"), None)
    if not cls:
        V.append("missing ## Classifications")
    else:
        if not cls["h3s"]:
            V.append("## Classifications: no entries")
        for h3 in cls["h3s"]:
            oid = h3["name"]
            if not OBJECTION_ID.match(oid):
                V.append(f"## Classifications: malformed O-id {oid!r}")
                continue
            status = h3["bullets"].get("status")
            if status not in {"LIVE", "RESOLVED"}:
                V.append(f"## Classifications/{oid}: invalid or missing status {status!r}")
            if h3["prose_lines"] == 0:
                V.append(f"## Classifications/{oid}: missing rationale prose")

    dec = next((s for s in sections if s["name"] == "Decision"), None)
    if not dec:
        V.append("missing ## Decision")
    else:
        decision = dec["bullets"].get("decision")
        if decision not in {"CONTINUE", "TERMINATE"}:
            V.append(f"## Decision: invalid or missing decision {decision!r}")
        if decision == "TERMINATE" and dec["prose_lines"] == 0:
            V.append("## Decision: TERMINATE without residue prose")
    return V


def validate_threads(text, expected_letter=None, expected_round=None):
    del expected_letter, expected_round
    V = []
    lines = text.splitlines()
    head = first_nonempty(lines)
    if not head:
        return ["file is empty"]
    if not re.match(r"^-\s*next_t_id:\s*T\d+\s*$", head):
        V.append(f"first non-empty line should be '- next_t_id: T<k+1>', got {head!r}")

    in_code = False
    entries = []
    cur = None
    for line in lines:
        if re.match(r"^```", line):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^###\s+(T\d+)\s*$", line)
        if m:
            cur = {"id": m.group(1), "bullets": {}, "prose": ""}
            entries.append(cur)
            continue
        mb = re.match(r"^-\s+(\w+):\s*(.*)$", line)
        if mb and cur is not None:
            cur["bullets"][mb.group(1)] = mb.group(2).strip()
            continue
        if line.strip() and cur is not None:
            cur["prose"] += line + "\n"

    for ent in entries:
        bul = ent["bullets"]
        if not bul.get("label"):
            V.append(f"### {ent['id']}: missing - label:")
        origin = bul.get("origin")
        if not origin:
            V.append(f"### {ent['id']}: missing - origin:")
        elif not (re.match(r"^r\d+-S-th\d+$", origin) or re.match(r"^r\d+-O-\d+$", origin)):
            V.append(f"### {ent['id']}: invalid origin {origin!r}")
        intro = bul.get("introduced")
        if not intro:
            V.append(f"### {ent['id']}: missing - introduced:")
        elif not re.match(r"^r\d+$", intro):
            V.append(f"### {ent['id']}: invalid introduced {intro!r}")
        if not ent["prose"].strip():
            V.append(f"### {ent['id']}: missing content paragraph")
        if "succeeds" in bul:
            for p in split_csv(bul["succeeds"]):
                if not THREAD_ID.match(p):
                    V.append(f"### {ent['id']}: succeeds {p!r} not a T-ID")
    return V


VALIDATORS = {
    "advocate": validate_advocate,
    "advocate-moves": validate_advocate_moves,
    "synth": validate_synth,
    "synth-threads": validate_synth_threads,
    "synth-moves": validate_synth_moves,
    "auditor": validate_auditor,
    "auditor-moves": validate_auditor_moves,
    "moderator": validate_moderator,
    "threads": validate_threads,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("role", choices=sorted(VALIDATORS))
    ap.add_argument("path")
    ap.add_argument("--letter", choices=["A", "B"])
    ap.add_argument("--round", type=int)
    args = ap.parse_args()

    with open(args.path) as f:
        text = f.read()
    fn = VALIDATORS[args.role]
    result = fn(text, args.letter, args.round)
    if isinstance(result, tuple):
        violations, warnings = result
    else:
        violations, warnings = result, []

    print(f"file: {args.path}")
    print(f"role: {args.role}")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")
    if not violations:
        print("PASS" + (" (with warnings)" if warnings else ""))
        return 0
    print(f"FAIL — {len(violations)} violations:")
    for v in violations:
        print(f"  {v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
