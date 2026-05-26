import shutil
import subprocess


def test_installed_help_available():
    cli = shutil.which("cli-anything-cocoscreator")
    assert cli, "Install with: pip install -e ."
    result = subprocess.run([cli, "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Cocos Creator" in result.stdout
