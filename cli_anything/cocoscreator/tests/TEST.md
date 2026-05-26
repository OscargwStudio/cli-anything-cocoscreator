# Test Plan

## Unit
- Verify project asset listing excludes `.meta` files.
- Verify build command construction validates project path.

## E2E
- Verify installed command exposes `--help`.
- Verify backend executable can be discovered.
- Use `build --dry-run` for safe command generation validation.

Real project build tests are intentionally not run automatically because they require a caller-supplied Cocos project and may take significant time.
