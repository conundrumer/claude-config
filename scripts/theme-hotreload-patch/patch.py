#!/usr/bin/env python3
"""
Patch Claude Code binary to hot-reload theme from ~/.claude.json changes.

Claude Code has a file watcher that polls ~/.claude.json every 1 second and
updates its in-memory config cache. However, the React ThemeProvider never
re-reads from that cache after mount — there's a no-op useEffect placeholder.

This patch bridges the two: the ThemeProvider exposes its React setState as a
global, and the file watcher calls it when the config changes. Event-driven,
no polling beyond what already exists.

Patch patterns are version-specific (stored in <version>/patterns.py).

USAGE:
  python3 patch.py                  # patches the latest installed version
  python3 patch.py --dry-run        # shows what would be changed
  python3 patch.py --restore        # restores from backup
  python3 patch.py --list           # list available pattern versions
"""

import argparse
import glob
import importlib.util
import os
import shutil
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_binary():
    """Find the latest Claude Code binary."""
    base = os.path.expanduser("~/.local/share/claude/versions")
    versions = sorted(glob.glob(os.path.join(base, "*")), key=os.path.getmtime)
    if not versions:
        sys.exit("No Claude Code versions found in ~/.local/share/claude/versions/")
    path = versions[-1]
    if not os.path.isfile(path):
        sys.exit(f"Expected file, got directory: {path}")
    return path


def detect_version(binary_path):
    """Extract version from binary path (the filename is the version)."""
    return os.path.basename(binary_path)


def available_versions():
    """List version directories that contain patterns.py."""
    versions = []
    for entry in os.listdir(SCRIPT_DIR):
        if os.path.isfile(os.path.join(SCRIPT_DIR, entry, "patterns.py")):
            versions.append(entry)
    return sorted(versions)


def load_patterns(version):
    """Load PATCHES from <version>/patterns.py."""
    pattern_file = os.path.join(SCRIPT_DIR, version, "patterns.py")
    if not os.path.exists(pattern_file):
        avail = available_versions()
        msg = f"No patterns for version {version}."
        if avail:
            msg += f" Available: {', '.join(avail)}"
        msg += "\nSee README.md for how to create patterns for a new version."
        sys.exit(msg)

    spec = importlib.util.spec_from_file_location("patterns", pattern_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PATCHES


def patch(binary_path, dry_run=False):
    version = detect_version(binary_path)
    print(f"Binary:  {binary_path}")
    print(f"Version: {version}")

    patches = load_patterns(version)

    with open(binary_path, "rb") as f:
        data = f.read()

    original_size = len(data)

    # Verify all patterns exist
    for name, old, new in patches:
        count = data.count(old)
        if count == 0:
            sys.exit(f"ABORT: Pattern not found for '{name}'. Binary may already be patched or a different build.")
        if count != 2:
            sys.exit(f"ABORT: Expected 2 occurrences of '{name}', found {count}.")
        delta = len(new) - len(old)
        print(f"  {name}: {count} matches, delta={delta:+d}b")

    # Verify total delta is zero (each pattern hits all occurrences)
    total_delta = sum((len(new) - len(old)) * data.count(old) for _, old, new in patches)
    if total_delta != 0:
        sys.exit(f"ABORT: Total byte delta is {total_delta:+d}, must be 0.")

    if dry_run:
        print("\nDry run — no changes made.")
        return

    # Backup
    backup_path = binary_path + ".bak"
    if not os.path.exists(backup_path):
        shutil.copy2(binary_path, backup_path)
        print(f"\n  Backup: {backup_path}")
    else:
        print(f"\n  Backup already exists: {backup_path}")

    # Apply patches
    patched = data
    for name, old, new in patches:
        patched = patched.replace(old, new)

    assert len(patched) == original_size, "Size changed after patching!"
    assert patched != data, "No changes were made!"

    with open(binary_path, "wb") as f:
        f.write(patched)
    print(f"  Patched: {binary_path}")

    # Re-sign (macOS requires valid signature)
    print("  Re-signing...")
    os.system(f'codesign --force --sign - "{binary_path}" 2>/dev/null')
    print("\nDone. Restart Claude Code sessions for the patch to take effect.")


def restore(binary_path):
    backup_path = binary_path + ".bak"
    if not os.path.exists(backup_path):
        sys.exit(f"No backup found at {backup_path}")
    shutil.copy2(backup_path, binary_path)
    os.system(f'codesign --force --sign - "{binary_path}" 2>/dev/null')
    print(f"Restored: {binary_path}")


def main():
    parser = argparse.ArgumentParser(description="Patch Claude Code for theme hot-reload")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--restore", action="store_true", help="Restore from backup")
    parser.add_argument("--list", action="store_true", help="List available pattern versions")
    parser.add_argument("--binary", help="Path to Claude binary (auto-detected if omitted)")
    args = parser.parse_args()

    if args.list:
        for v in available_versions():
            print(v)
        return

    binary_path = args.binary or find_binary()

    if args.restore:
        restore(binary_path)
    else:
        patch(binary_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
