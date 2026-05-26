# cli-anything-cocoscreator

CLI-Anything harness for Cocos Creator 3.8.8. It wraps the real Cocos Creator editor executable instead of reimplementing editor behavior.

## Install

```bash
cd ~/Downloads/cocos-engine-v3.8.8/editor/agent-harness
pip install -e .
```

## Backend

Default backend:

```text
/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/MacOS/CocosCreator
```

Override with `COCOS_CREATOR` or `--creator-path`.

## Examples

```bash
cli-anything-cocoscreator info
cli-anything-cocoscreator --json project info /path/to/project
cli-anything-cocoscreator project assets /path/to/project --limit 20
cli-anything-cocoscreator build /path/to/project --platform web-mobile --debug --dry-run
cli-anything-cocoscreator --json run -- --help
```
