import json
import shlex

import click

from cli_anything.cocoscreator.core.asset import find_asset_deps, find_asset_refs, read_asset_meta, read_asset_uuid
from cli_anything.cocoscreator.core.project import list_assets
from cli_anything.cocoscreator.utils.cocoscreator_backend import build_args, find_executable, project_info, run_creator


def _format_value(key, value):
    """Pretty-print a single dict value for human output."""
    if isinstance(value, list):
        if not value:
            return f"{key}: (none)"
        lines = [f"{key}:"]
        for item in value:
            if isinstance(item, dict):
                parts = "  ".join(f"{k}={v}" for k, v in item.items())
                lines.append(f"  - {parts}")
            else:
                lines.append(f"  - {item}")
        return "\n".join(lines)
    if isinstance(value, dict):
        lines = [f"{key}:"]
        for k, v in value.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    return f"{key}: {value}"


def emit(data, as_json):
    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    elif isinstance(data, dict):
        parts = [_format_value(k, v) for k, v in data.items()]
        click.echo("\n".join(parts))
    else:
        click.echo(data)


@click.group(invoke_without_command=True)
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.option("--json-output", "as_json", is_flag=True, help="Alias for --json.")
@click.option("--creator-path", default=None, help="Path to CocosCreator executable. Defaults to COCOS_CREATOR or Cocos Creator 3.8.8 macOS app.")
@click.pass_context
def cli(ctx, as_json, creator_path):
    """CLI-Anything harness for Cocos Creator 3.8.8."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = as_json
    ctx.obj["creator_path"] = creator_path
    if ctx.invoked_subcommand is None:
        emit({"name": "cli-anything-cocoscreator", "commands": ["info", "project", "asset", "build", "run"]}, as_json)


@cli.command()
@click.pass_context
def info(ctx):
    """Show harness and backend information."""
    exe = find_executable(ctx.obj.get("creator_path"))
    emit({"name": "cocoscreator", "version": "3.8.8", "executable": exe}, ctx.obj["json"])


@cli.group()
def project():
    """Inspect Cocos Creator projects."""


@project.command("info")
@click.argument("project_path")
@click.pass_context
def project_info_cmd(ctx, project_path):
    """Inspect project structure."""
    emit(project_info(project_path), ctx.obj["json"])


@project.command("assets")
@click.argument("project_path")
@click.option("--limit", default=100, show_default=True, type=int)
@click.pass_context
def project_assets_cmd(ctx, project_path, limit):
    """List project assets excluding .meta files."""
    data = {"project": project_path, "assets": list_assets(project_path, limit)}
    emit(data, ctx.obj["json"])


@cli.group()
def asset():
    """Inspect Cocos Creator asset metadata and references."""


@asset.command("meta")
@click.argument("project_path")
@click.argument("asset_path")
@click.pass_context
def asset_meta_cmd(ctx, project_path, asset_path):
    """Read an asset's .meta file."""
    try:
        emit(read_asset_meta(project_path, asset_path), ctx.obj["json"])
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc


@asset.command("uuid")
@click.argument("project_path")
@click.argument("asset_path")
@click.pass_context
def asset_uuid_cmd(ctx, project_path, asset_path):
    """Print an asset uuid from its .meta file."""
    try:
        uuid = read_asset_uuid(project_path, asset_path)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    emit({"asset": asset_path, "uuid": uuid}, ctx.obj["json"])


@asset.command("deps")
@click.argument("project_path")
@click.argument("asset_path")
@click.option("--hide-unresolved", is_flag=True, help="Hide uuids that cannot be resolved to a project file.")
@click.pass_context
def asset_deps_cmd(ctx, project_path, asset_path, hide_unresolved):
    """Find all assets that this asset depends on (outgoing references)."""
    try:
        emit(find_asset_deps(project_path, asset_path, include_unresolved=not hide_unresolved), ctx.obj["json"])
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc


@asset.command("refs")
@click.argument("project_path")
@click.argument("asset_path", required=False)
@click.option("--uuid", "uuid_value", default=None, help="Search references by uuid instead of asset path.")
@click.option("--include-meta", is_flag=True, help="Include .meta files in the reference scan.")
@click.option("--verbose", is_flag=True, help="Show line numbers and matched text for each reference.")
@click.pass_context
def asset_refs_cmd(ctx, project_path, asset_path, uuid_value, include_meta, verbose):
    """Find project files that reference an asset uuid."""
    try:
        data = find_asset_refs(project_path, asset=asset_path, uuid=uuid_value, include_meta=include_meta)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    if ctx.obj["json"]:
        emit(data, True)
        return
    if verbose:
        emit({
            "project": data["project"],
            "asset": data["asset"],
            "uuid": data["uuid"],
            "references": data["references"],
            "reference_count": data["reference_count"],
        }, False)
    else:
        emit({
            "project": data["project"],
            "asset": data["asset"],
            "uuid": data["uuid"],
            "files": data["files"],
            "file_count": data["file_count"],
        }, False)


@cli.command()
@click.argument("project_path")
@click.option("--platform", required=True, help="Cocos build platform, e.g. web-mobile, android, ios, mac.")
@click.option("--debug/--release", default=False, help="Build debug or release output.")
@click.option("--option", "options", multiple=True, help="Additional build option as key=value. Can be repeated.")
@click.option("--dry-run", is_flag=True, help="Print the CocosCreator command without running it.")
@click.option("--timeout", default=None, type=int, help="Optional subprocess timeout in seconds.")
@click.pass_context
def build(ctx, project_path, platform, debug, options, dry_run, timeout):
    """Build a Cocos Creator project using the real editor backend."""
    extra = {}
    for item in options:
        if "=" not in item:
            raise click.ClickException(f"Invalid --option {item!r}; expected key=value")
        key, value = item.split("=", 1)
        extra[key] = value
    args = build_args(project_path, platform, debug=debug, build_config=extra)
    exe = find_executable(ctx.obj.get("creator_path"))
    command = [exe] + args
    if dry_run:
        emit({"command": command, "shell": " ".join(shlex.quote(part) for part in command)}, ctx.obj["json"])
        return
    emit(run_creator(args, ctx.obj.get("creator_path"), timeout=timeout), ctx.obj["json"])


@cli.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.pass_context
def run(ctx):
    """Pass arbitrary arguments through to CocosCreator."""
    result = run_creator(ctx.args, ctx.obj.get("creator_path"))
    emit(result, ctx.obj["json"])
