---
name: cli-anything-cocoscreator
description: Use Cocos Creator 3.8.8 from the command line for project inspection, asset analysis, and builds.
---

# cli-anything-cocoscreator

Use this skill when automating Cocos Creator 3.8.8 projects. The CLI wraps the real editor executable and supports JSON output via `--json`.

## Global Flags

| Flag | Description |
|------|-------------|
| `--json` | Output machine-readable JSON |
| `--creator-path PATH` | Path to CocosCreator executable (overrides `COCOS_CREATOR` env var) |

## Commands

### Info

```bash
cli-anything-cocoscreator info
```

### Project

```bash
cli-anything-cocoscreator project info <project-path>
cli-anything-cocoscreator project assets <project-path> --limit 50
```

### Asset

```bash
# Read the .meta file for an asset
cli-anything-cocoscreator asset meta <project-path> <asset-path>

# Print the UUID from an asset's .meta file
cli-anything-cocoscreator asset uuid <project-path> <asset-path>

# Find all assets this asset depends on (outgoing references)
cli-anything-cocoscreator asset deps <project-path> <asset-path> [--hide-unresolved]

# Find all project files that reference an asset
# Supports .ts/.js scripts (searches compact UUID in prefab/scene files)
cli-anything-cocoscreator asset refs <project-path> <asset-path> [--verbose] [--include-meta]
cli-anything-cocoscreator asset refs <project-path> --uuid <uuid> [--verbose]
```

`asset refs` default output: file list with UUID. Use `--verbose` for line numbers and matched text.

### Build

```bash
cli-anything-cocoscreator build <project-path> --platform web-mobile [--debug] [--dry-run] [--timeout 300]
cli-anything-cocoscreator build <project-path> --platform android --option key=value
```

Use `--dry-run` to inspect the native CocosCreator invocation before running.

### Run (passthrough)

```bash
cli-anything-cocoscreator run -- --help
cli-anything-cocoscreator run -- --project /path/to/proj --build platform=web-mobile
```

## Notes

- Asset paths can be absolute or relative to the project root.
- Cocos Creator 3.x stores script component references as compact UUIDs (23-char) in prefab/scene files; `asset refs` handles this automatically.
- `asset deps` scans the asset file content for UUID references and resolves them against `.meta` files.
