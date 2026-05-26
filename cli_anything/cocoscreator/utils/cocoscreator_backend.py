import json
import os
import shutil
import subprocess
from pathlib import Path

DEFAULT_MAC_APP = Path("/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/MacOS/CocosCreator")


def find_executable(explicit_path=None):
    candidates = []
    if explicit_path:
        candidates.append(Path(explicit_path).expanduser())
    env_path = os.environ.get("COCOS_CREATOR")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.append(DEFAULT_MAC_APP)
    which_path = shutil.which("CocosCreator") or shutil.which("cocoscreator")
    if which_path:
        candidates.append(Path(which_path))
    for candidate in candidates:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise RuntimeError("Cocos Creator executable not found. Set COCOS_CREATOR or pass --creator-path.")


def run_creator(args, creator_path=None, timeout=None):
    exe = find_executable(creator_path)
    cmd = [exe] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return {
        "command": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def build_args(project, platform, debug=False, build_config=None):
    project_path = Path(project).expanduser().resolve()
    if not project_path.exists():
        raise RuntimeError(f"Project path not found: {project_path}")
    options = {"platform": platform, "debug": str(bool(debug)).lower()}
    if build_config:
        options.update(build_config)
    build_value = ";".join(f"{key}={value}" for key, value in options.items())
    return ["--project", str(project_path), "--build", build_value]


def project_info(project):
    project_path = Path(project).expanduser().resolve()
    package_json = project_path / "package.json"
    assets = project_path / "assets"
    settings = project_path / "settings"
    data = {
        "project": str(project_path),
        "exists": project_path.exists(),
        "package_json": package_json.exists(),
        "assets_dir": assets.exists(),
        "settings_dir": settings.exists(),
    }
    if package_json.exists():
        try:
            data["package"] = json.loads(package_json.read_text())
        except Exception as exc:
            data["package_error"] = str(exc)
    return data
