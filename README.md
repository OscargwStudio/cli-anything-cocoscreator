# cli-anything-cocoscreator

Command-line tool for inspecting and building [Cocos Creator 3.8.8](https://www.cocos.com/creator) projects. Designed for use with AI agents and automation scripts.

## Installation

```bash
git clone git@github.com:OscargwStudio/cli-anything-cocoscreator.git
cd cli-anything-cocoscreator
pip install -e .
```

Requires Python 3.10+.

## Cocos Creator Executable

The tool locates the editor in this order:

1. `--creator-path PATH` flag
2. `COCOS_CREATOR` environment variable
3. macOS default: `/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/MacOS/CocosCreator`
4. `CocosCreator` on system `PATH`

For Windows, set the environment variable:

```powershell
[System.Environment]::SetEnvironmentVariable("COCOS_CREATOR", "C:\CocosDashboard\resources\.editors\Creator\3.8.8\CocosCreator.exe", "User")
```

> Asset inspection commands (`asset meta/uuid/deps/refs`, `project assets`) do **not** require the editor to be installed.

## Commands

### `info`

Show harness and backend information.

```bash
cli-anything-cocoscreator info
cli-anything-cocoscreator info --json
```

---

### `project info`

Inspect project directory structure.

```bash
cli-anything-cocoscreator project info /path/to/project
```

---

### `project assets`

List all assets (excluding `.meta` files).

```bash
cli-anything-cocoscreator project assets /path/to/project --limit 50
```

---

### `asset meta`

Read the `.meta` sidecar file for an asset.

```bash
cli-anything-cocoscreator asset meta /path/to/project assets/MySprite.png
```

---

### `asset uuid`

Print the UUID of an asset.

```bash
cli-anything-cocoscreator asset uuid /path/to/project assets/MyScript.ts
```

---

### `asset deps`

Find all assets this file depends on (outgoing UUID references).

```bash
cli-anything-cocoscreator asset deps /path/to/project assets/prefab/MyPrefab.prefab
cli-anything-cocoscreator asset deps /path/to/project assets/prefab/MyPrefab.prefab --hide-unresolved
```

---

### `asset refs`

Find all project files that reference an asset.

For `.ts`/`.js` scripts, Cocos Creator 3.x stores references as compact UUIDs in prefab/scene files — this is handled automatically.

```bash
# Default: list files + UUID
cli-anything-cocoscreator asset refs /path/to/project assets/script/MyComponent.ts

# Verbose: include line numbers and matched text
cli-anything-cocoscreator asset refs /path/to/project assets/script/MyComponent.ts --verbose

# Search by UUID directly
cli-anything-cocoscreator asset refs /path/to/project --uuid 45987cf6-555a-4248-8005-8a04fa602d01

# Include .meta files in scan
cli-anything-cocoscreator asset refs /path/to/project assets/MyTexture.png --include-meta
```

---

### `build`

Build the project using the CocosCreator editor backend.

```bash
# Dry-run: print the command without executing
cli-anything-cocoscreator build /path/to/project --platform web-mobile --dry-run

# Debug build
cli-anything-cocoscreator build /path/to/project --platform web-mobile --debug

# Release build with extra options
cli-anything-cocoscreator build /path/to/project --platform android --option outputName=myapp

# With timeout (seconds)
cli-anything-cocoscreator build /path/to/project --platform ios --timeout 600
```

Supported platforms: `web-mobile`, `web-desktop`, `android`, `ios`, `mac`, `windows`, etc.

---

### `run`

Pass arbitrary arguments directly to the CocosCreator executable.

```bash
cli-anything-cocoscreator run -- --help
cli-anything-cocoscreator run -- --project /path/to/project --build platform=web-mobile
```

## Global Flags

| Flag | Description |
|------|-------------|
| `--json` | Output machine-readable JSON |
| `--json-output` | Alias for `--json` |
| `--creator-path PATH` | Path to CocosCreator executable |

## Asset Path Convention

Asset paths can be **absolute** or **relative to the project root**:

```bash
# Absolute
cli-anything-cocoscreator asset uuid /Users/me/MyGame /Users/me/MyGame/assets/Hero.ts

# Relative (recommended)
cli-anything-cocoscreator asset uuid /Users/me/MyGame assets/Hero.ts
```
