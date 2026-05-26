# Cocos Creator Harness Notes

This harness uses `cocos-engine@v3.8.8/editor` as source context and invokes the installed Cocos Creator 3.8.8 application as the real backend. The editor source directory contains inspector, exports, assets, i18n, and editor extension modules; the shippable command-line behavior is provided by the installed macOS executable.

Backend executable:

```text
/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/MacOS/CocosCreator
```

The build command emits Cocos Creator's native `--project <path> --build key=value;...` invocation. Use `--dry-run` first to inspect commands before running a real build.
