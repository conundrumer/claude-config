"""
Patch patterns for Claude Code 2.1.87.

Architecture:
  The file watcher (o2$) polls ~/.claude.json every 1s and updates the config
  cache (qB). The ThemeProvider reads theme into React state once at mount.
  These patches bridge the two: the effect exposes the React setState as a
  global, and the watcher calls it when the config file changes.

  ThemeProvider: E0_
    State: $ (theme setting), K (setter), O (preview), T (preview setter)
    Config read: z_().theme
    Hook: E_H() = useContext(InternalStdinContext)
    No-op effect: useEffect(()=>{}, [f,w])

  File watcher: o2$
    After re-reading config: qB = {config: ..., mtime: ...}, It = {mtime: ..., size: ...}
    $ in watcher scope = parsed JSON config object (NOT the same $ as ThemeProvider state)

Byte budget: patches sum to +0 across all 6 sites.
Each pattern appears exactly 2x (two copies of JS in __BUN section).
"""

PATCHES = [
    (
        "watcher global callback",
        # After the file watcher updates the config cache, call the global setter
        # if it exists and the config has a theme value.
        # $.theme here is from the parsed JSON — the new theme from the file.
        b'qB={config:m46({...h4H(TS),...$}),mtime:_.mtimeMs},It={mtime:_.mtimeMs,size:_.size}}).catch',
        b'qB={config:m46({...h4H(TS),...$}),mtime:_.mtimeMs},It={mtime:_.mtimeMs,size:_.size},globalThis._t&&$.theme&&globalThis._t($.theme)}).catch',
    ),
    (
        "effect + ThemeProvider narrowing",
        # Replaces no-op useEffect with one that exposes K (React setState) as
        # globalThis._t. Empty deps [] so it registers once on mount.
        # Also narrows 3x === to == and 2x !== to != (string/null comparisons).
        b',{internal_querier:w}=E_H();KG.useEffect(()=>{},[f,w]);let Y=f==="auto"?z:f,D=KG.useMemo(()=>({themeSetting:$,setThemeSetting:(j)=>{if(K(j),T(null),j==="auto")A(IFH());q?.(j)},setPreviewTheme:(j)=>{if(T(j),j==="auto")A(IFH())},savePreview:()=>{if(O!==null)K(O),T(null),q?.(O)},cancelPreview:()=>{if(O!==null)T(null)}',
        b',w=E_H();KG.useEffect(()=>{globalThis._t=K},[]);let Y=f=="auto"?z:f,D=KG.useMemo(()=>({themeSetting:$,setThemeSetting:(j)=>{if(K(j),T(null),j=="auto")A(IFH());q?.(j)},setPreviewTheme:(j)=>{if(T(j),j=="auto")A(IFH())},savePreview:()=>{if(O!=null)K(O),T(null),q?.(O)},cancelPreview:()=>{if(O!=null)T(null)}',
    ),
    (
        "Aq hook narrowing",
        # !== to != in useTheme hook cache check (compares React elements, safe)
        b'if(H[0]!==_||H[1]!==q)$=[_,q],H[0]=_,H[1]=q,H[2]=$;else $=H[2];return $}function G0H',
        b'if(H[0]!=_||H[1]!=q)$=[_,q],H[0]=_,H[1]=q,H[2]=$;else $=H[2];return $}function G0H',
    ),
    (
        "$G_ hook narrowing",
        # !== to != in usePreviewTheme hook cache check
        b'if(H[0]!==$||H[1]!==q||H[2]!==_)K={setPreviewTheme',
        b'if(H[0]!=$||H[1]!=q||H[2]!=_)K={setPreviewTheme',
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
        b'`Failed to save config with lock: ${$}`',
        b'`Config save err: ${$}`',
    ),
]
