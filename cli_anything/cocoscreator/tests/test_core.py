from pathlib import Path

from cli_anything.cocoscreator.core.project import list_assets
from cli_anything.cocoscreator.utils.cocoscreator_backend import build_args


def test_list_assets_excludes_meta(tmp_path):
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "main.ts").write_text("")
    (assets / "main.ts.meta").write_text("")
    assert list_assets(tmp_path) == ["main.ts"]


def test_build_args(tmp_path):
    args = build_args(tmp_path, "web-mobile", debug=True, build_config={"md5Cache": "true"})
    assert args[0] == "--project"
    assert str(tmp_path) in args
    assert args[-1] == "platform=web-mobile;debug=true;md5Cache=true"
