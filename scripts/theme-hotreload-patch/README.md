# theme-hotreload-patch

Patches the Claude Code binary so running sessions pick up theme changes from `~/.claude.json` in real time. Without this, theme only applies at process startup.

**Developed against version 2.1.88.** The patch patterns are version-specific and will fail safely (abort, no partial writes) on other versions.

## Usage

```bash
python3 patch.py --dry-run   # verify patterns match
python3 patch.py             # patch (creates .bak backup)
python3 patch.py --restore   # restore from backup
```

Restart Claude Code sessions after patching. Pair with `scripts/theme-sync/` (the macOS appearance daemon) for automatic light/dark switching.

## What it patches

Claude Code already watches `~/.claude.json` every 1 second (`fs.watchFile` with 1s poll) and updates its in-memory config cache. But the React ThemeProvider reads theme once at mount into `useState` and never checks the cache again — there's a no-op `useEffect(()=>{}, [w,f])` placeholder that was never implemented.

Two patch sites bridge the gap:

1. **ThemeProvider useEffect** — exposes React's theme setState as `globalThis._t`:
   ```
   useEffect(()=>{globalThis._t=$},[])
   ```

2. **File watcher callback** — after updating the config cache, calls the exposed setter:
   ```
   globalThis._t && K.theme && globalThis._t(K.theme)
   ```

This is event-driven: the watcher fires only when the file changes, and React skips re-renders if the value hasn't changed (`Object.is` check).

## How the binary works

Claude Code is a [Bun](https://bun.sh/) `--compile` binary: a Mach-O arm64 executable with an embedded `__BUN` section (~118MB) containing the full minified JS source. Bun parses and JIT-compiles this source at startup.

Key properties:
- The JS source is stored as **continuous text** inside `__BUN`, not length-prefixed per module
- There are **two copies** of the JS in the section (both must be patched identically)
- Replacements must be **exactly the same byte length** — any size change shifts all subsequent offsets and breaks Bun's internal pointers

## Byte budget technique

The two functional patches add more bytes than they remove (+47b and -12b). To balance to zero, nearby code is shortened:
- `===` narrowed to `==` and `!==` to `!=` where safe (string/null comparisons)
- Error message strings shortened (`"Failed to save config with lock: "` → `"Config save err: "`)

Total across all 6 patch sites × 2 copies = 0 bytes.

## Adapting to a new version

If Claude Code updates and the patch patterns no longer match, here's how to redo it:

### 1. Find the ThemeProvider

```bash
strings ~/.local/share/claude/versions/X.Y.Z | grep -oE '[A-Za-z_$]+[Tt]heme[A-Za-z_$]*' | sort -u
```

Look for: `setThemeSetting`, `useThemeSetting`, `currentTheme`, `onThemeSave`, `setPreviewTheme`.

### 2. Extract the JS context

```python
with open(BINARY_PATH, 'rb') as f:
    data = f.read()
needle = b'setThemeSetting'
pos = data.find(needle)
print(data[pos-500:pos+500].decode('ascii', errors='replace'))
```

### 3. Identify the two patch targets

**ThemeProvider**: Look for `useEffect(()=>{},[...])`. The state variables around it:
- `useState(initialTheme)` → `[stateVar, setterVar]`
- A config-read function (like `z_()`) with a `.theme` property

**File watcher**: Look for `watchFile` nearby with a callback that updates a config cache variable (like `pB={config:...}`). The parsed config object in that callback has a `.theme` property.

### 4. Craft same-length replacements

1. Expose the React setState as a global in the useEffect
2. Call it from the file watcher callback after the config cache update
3. Measure the byte delta
4. Find nearby `===`/`!==` to narrow and/or error strings to shorten
5. Verify total delta is exactly 0

### 5. Verify both copies

The JS appears twice in `__BUN`. Confirm each old pattern has exactly 2 occurrences. `bytes.replace()` will hit both.

### 6. Re-sign

```bash
codesign --force --sign - /path/to/binary
```

macOS won't run unsigned modified binaries.

## Caveats

- **Updates overwrite the binary** — re-run after each Claude Code update
- **Code signing** — re-signed ad-hoc locally; Gatekeeper may prompt on first launch
- **Minifier changes** — variable names shift across versions, so the exact byte patterns need to be redone (the approach stays the same)
