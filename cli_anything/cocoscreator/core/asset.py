import json
import re
from pathlib import Path

UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE)
_B64URL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

# @ccclass('ClassName') 或 @ccclass("ClassName")
_CCCLASS_RE = re.compile(r'@ccclass\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)')
# export class ClassName / export default class ClassName
_EXPORT_CLASS_RE = re.compile(r'export\s+(?:default\s+)?class\s+(\w+)')

SCRIPT_EXTENSIONS = {".ts", ".js"}
# 只扫 prefab/scene/fire 找脚本类名引用
SCRIPT_REF_EXTENSIONS = {".prefab", ".scene", ".fire"}

TEXT_EXTENSIONS = {
    ".anim",
    ".controller",
    ".effect",
    ".fire",
    ".json",
    ".material",
    ".mtl",
    ".prefab",
    ".scene",
    ".ts",
    ".js",
    ".txt",
}

SEARCH_DIRS = ("assets", "settings", "packages")


def extract_script_classnames(asset_path):
    """Extract @ccclass names and export class names from a .ts/.js file."""
    try:
        content = Path(asset_path).read_text(errors="ignore")
    except Exception:
        return []
    names = _CCCLASS_RE.findall(content)
    if not names:
        names = _EXPORT_CLASS_RE.findall(content)
    return list(dict.fromkeys(names))  # deduplicate, preserve order


def compress_uuid(uuid_str):
    """Convert full UUID to Cocos Creator 3.x compact form (23-char string).

    Algorithm: first 20 bits -> 5 hex prefix, remaining 108 bits -> 18 base64url chars.
    """
    hex_str = uuid_str.replace("-", "").lower()
    if len(hex_str) != 32:
        return None
    try:
        val = int(hex_str, 16)
    except ValueError:
        return None
    prefix = hex_str[:5]
    remaining = val & ((1 << 108) - 1)
    b64 = "".join(_B64URL[(remaining >> (i * 6)) & 0x3F] for i in range(17, -1, -1))
    return prefix + b64


def resolve_asset_path(project, asset):
    project_path = Path(project).expanduser().resolve()
    asset_path = Path(asset).expanduser()
    if not asset_path.is_absolute():
        asset_path = project_path / asset_path
    return project_path, asset_path.resolve()


def meta_path_for(asset_path):
    return Path(f"{asset_path}.meta")


def read_asset_meta(project, asset):
    project_path, asset_path = resolve_asset_path(project, asset)
    meta_path = meta_path_for(asset_path)
    if not asset_path.exists():
        raise RuntimeError(f"Asset not found: {asset_path}")
    if not meta_path.exists():
        raise RuntimeError(f"Meta file not found: {meta_path}")
    try:
        meta = json.loads(meta_path.read_text())
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid meta JSON: {meta_path}: {exc}") from exc
    return {
        "project": str(project_path),
        "asset": str(asset_path),
        "asset_relative": _relative_to_project(project_path, asset_path),
        "meta": str(meta_path),
        "uuid": meta.get("uuid"),
        "raw": meta,
    }


def read_asset_uuid(project, asset):
    data = read_asset_meta(project, asset)
    uuid = data.get("uuid")
    if not uuid:
        raise RuntimeError(f"Meta file has no uuid: {data['meta']}")
    return uuid


def find_asset_refs(project, asset=None, uuid=None, include_meta=False):
    project_path = Path(project).expanduser().resolve()
    if not project_path.exists():
        raise RuntimeError(f"Project path not found: {project_path}")

    asset_path = None
    if asset:
        _, asset_path = resolve_asset_path(project_path, asset)

    # Detect script assets (.ts/.js): Cocos 3.x references them by class name, not uuid
    is_script = asset_path is not None and asset_path.suffix in SCRIPT_EXTENSIONS
    classnames = []
    if is_script:
        classnames = extract_script_classnames(asset_path)
        # Also resolve uuid if available (for completeness)
        try:
            uuid = uuid or read_asset_uuid(project_path, asset_path)
        except Exception:
            pass
    else:
        if not uuid:
            if not asset:
                raise RuntimeError("Either asset or uuid is required")
            uuid = read_asset_uuid(project_path, asset)

    references = []
    seen_files = {}  # file -> uuid

    for file_path in _iter_search_files(project_path, include_meta):
        try:
            lines = file_path.read_text(errors="ignore").splitlines()
        except Exception:
            continue
        rel = _relative_to_project(project_path, file_path)

        # uuid-based search (full uuid + compact form both)
        if uuid:
            compact = compress_uuid(uuid) or ""
            for line_no, text in enumerate(lines, 1):
                if uuid in text or (compact and compact in text):
                    references.append({"file": rel, "line": line_no, "text": text.strip(), "match_type": "uuid"})
                    seen_files.setdefault(rel, uuid)

        # classname-based search for script files
        if classnames and file_path.suffix in SCRIPT_REF_EXTENSIONS:
            for line_no, text in enumerate(lines, 1):
                for cname in classnames:
                    if cname in text:
                        references.append({"file": rel, "line": line_no, "text": text.strip(), "match_type": "classname"})
                        seen_files.setdefault(rel, uuid or cname)
                        break  # one match per line per file is enough

    files = [{"file": f, "uuid": u} for f, u in seen_files.items()]
    return {
        "project": str(project_path),
        "asset": asset,
        "uuid": uuid,
        "classnames": classnames,
        "files": files,
        "file_count": len(files),
        "references": references,
        "reference_count": len(references),
    }


def build_uuid_map(project):
    """Build a uuid -> relative asset path map from all .meta files in the project."""
    project_path = Path(project).expanduser().resolve()
    uuid_map = {}
    assets_dir = project_path / "assets"
    if not assets_dir.exists():
        return uuid_map
    for meta_file in assets_dir.rglob("*.meta"):
        try:
            meta = json.loads(meta_file.read_text(errors="ignore"))
        except Exception:
            continue
        uuid = meta.get("uuid")
        if not uuid:
            continue
        # The actual asset is the path without .meta suffix
        asset_file = Path(str(meta_file)[:-5])
        uuid_map[uuid.lower()] = _relative_to_project(project_path, asset_file)
    return uuid_map


def find_asset_deps(project, asset, include_unresolved=True):
    """Find all assets that this asset (prefab/scene/anim/etc) depends on."""
    project_path, asset_path = resolve_asset_path(project, asset)
    if not asset_path.exists():
        raise RuntimeError(f"Asset not found: {asset_path}")

    # Get this asset's own uuid so we can exclude self-references
    own_uuid = None
    meta_path = meta_path_for(asset_path)
    if meta_path.exists():
        try:
            own_meta = json.loads(meta_path.read_text())
            own_uuid = (own_meta.get("uuid") or "").lower()
        except Exception:
            pass

    content = asset_path.read_text(errors="ignore")
    found_uuids = {u.lower() for u in UUID_RE.findall(content)}
    if own_uuid:
        found_uuids.discard(own_uuid)

    uuid_map = build_uuid_map(project_path)
    dependencies = []
    unresolved = []
    for uuid in sorted(found_uuids):
        resolved = uuid_map.get(uuid)
        if resolved:
            dependencies.append({"uuid": uuid, "file": resolved})
        elif include_unresolved:
            unresolved.append({"uuid": uuid, "file": None, "note": "not found in project (may be engine built-in)"})

    return {
        "project": str(project_path),
        "asset": _relative_to_project(project_path, asset_path),
        "uuid": own_uuid,
        "dependencies": dependencies,
        "unresolved": unresolved,
        "count": len(dependencies),
        "unresolved_count": len(unresolved),
    }


def _iter_search_files(project_path, include_meta):
    for dirname in SEARCH_DIRS:
        root = project_path / dirname
        if not root.exists():
            continue
        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.name.endswith(".meta") and not include_meta:
                continue
            if file_path.suffix in TEXT_EXTENSIONS or file_path.name.endswith(".meta"):
                yield file_path


def _relative_to_project(project_path, path):
    try:
        return str(path.relative_to(project_path))
    except ValueError:
        return str(path)
