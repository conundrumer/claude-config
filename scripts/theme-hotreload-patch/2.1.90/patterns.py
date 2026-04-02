"""
Patch patterns for Claude Code 2.1.90.

Architecture:
  The file watcher (pZ4) polls ~/.claude.json every 1s and updates the config
  cache (Gd). The ThemeProvider reads theme into React state once at mount.
  These patches bridge the two: the effect exposes the React setState as a
  global, and the watcher calls it when the config file changes.

  ThemeProvider: hZ_
    State: K (theme setting), $ (setter), O (preview), T (preview setter)
    Config read: T_().theme
    Hook: ju() = useContext(InternalStdinContext)
    No-op effect: useEffect(()=>{}, [w,f])

  File watcher: pZ4
    After re-reading config: Gd = {config: ..., mtime: ...}, I6H = {mtime: ..., size: ...}
    K in watcher scope = parsed JSON config object (NOT the same K as ThemeProvider state)

Byte budget: patches sum to +0 across all 6 sites.
Each pattern appears exactly 2x (two copies of JS in __BUN section).
"""

PATCHES = [
    (
        "watcher global callback",
        # After the file watcher updates the config cache, call the global setter
        # if it exists and the config has a theme value.
        # K.theme here is from the parsed JSON — the new theme from the file.
        b'Gd={config:nv6({...Nn(),...K}),mtime:_.mtimeMs},I6H={mtime:_.mtimeMs,size:_.size}}).catch',
        b'Gd={config:nv6({...Nn(),...K}),mtime:_.mtimeMs},I6H={mtime:_.mtimeMs,size:_.size},globalThis._t&&K.theme&&globalThis._t(K.theme)}).catch',
    ),
    (
        "effect + ThemeProvider narrowing",
        # Replaces no-op useEffect with one that exposes $ (React setState) as
        # globalThis._t. Empty deps [] so it registers once on mount.
        # Also narrows 3x === to == and 2x !== to != (string/null comparisons).
        b',{internal_querier:f}=ju();HZ.useEffect(()=>{},[w,f]);let Y=w==="auto"?z:w,j=HZ.useMemo(()=>({themeSetting:K,setThemeSetting:(D)=>{if($(D),T(null),D==="auto")A(NQH());q?.(D)},setPreviewTheme:(D)=>{if(T(D),D==="auto")A(NQH())},savePreview:()=>{if(O!==null)$(O),T(null),q?.(O)},cancelPreview:()=>{if(O!==null)T(null)}',
        b',f=ju();HZ.useEffect(()=>{globalThis._t=$},[]);let Y=w=="auto"?z:w,j=HZ.useMemo(()=>({themeSetting:K,setThemeSetting:(D)=>{if($(D),T(null),D=="auto")A(NQH());q?.(D)},setPreviewTheme:(D)=>{if(T(D),D=="auto")A(NQH())},savePreview:()=>{if(O!=null)$(O),T(null),q?.(O)},cancelPreview:()=>{if(O!=null)T(null)}',
    ),
    (
        "jq hook narrowing",
        # !== to != in useTheme hook cache check (compares React elements, safe)
        b'if(H[0]!==_||H[1]!==q)K=[_,q],H[0]=_,H[1]=q,H[2]=K;else K=H[2];return K}function EGH',
        b'if(H[0]!=_||H[1]!=q)K=[_,q],H[0]=_,H[1]=q,H[2]=K;else K=H[2];return K}function EGH',
    ),
    (
        "yZ_ hook narrowing",
        # !== to != in usePreviewTheme hook cache check
        b'if(H[0]!==K||H[1]!==q||H[2]!==_)$={setPreviewTheme',
        b'if(H[0]!=K||H[1]!=q||H[2]!=_)$={setPreviewTheme',
    ),
    (
        "error string #1",
        # Shorten config save error message (frees bytes for watcher patch)
        b'`Failed to save config with lock: ${q}`',
        b'`Config save error: ${q}`',
    ),
    (
        "error string #2",
        # Shorten config save error message (frees bytes for watcher patch)
        b'`Failed to save config with lock: ${K}`',
        b'`Config save err: ${K}`',
    ),
]
