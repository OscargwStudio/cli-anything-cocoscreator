from pathlib import Path


def list_assets(project, limit=100):
    assets = Path(project).expanduser().resolve() / "assets"
    if not assets.exists():
        return []
    files = []
    for path in assets.rglob("*"):
        if path.is_file() and not path.name.endswith(".meta"):
            files.append(str(path.relative_to(assets)))
            if len(files) >= limit:
                break
    return files
