---
name: cli-anything-cocoscreator
description: Use Cocos Creator 3.8.8 from the command line for project inspection and builds.
---

# cli-anything-cocoscreator

Use this skill when automating Cocos Creator 3.8.8 projects. The CLI wraps the real editor executable and supports JSON output via `--json`.

## Commands

```bash
cli-anything-cocoscreator info
cli-anything-cocoscreator project info <project-path>
cli-anything-cocoscreator project assets <project-path> --limit 50
cli-anything-cocoscreator build <project-path> --platform web-mobile --debug --dry-run
cli-anything-cocoscreator run -- --help
```

Use `build --dry-run` before real builds to inspect the native CocosCreator invocation.
