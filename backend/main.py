"""
main.py
────────
CLI entry point for the Autoposter.

Usage examples:
  python main.py post --image photo.jpg --description "Sunset at the beach"
  python main.py post -i photo.jpg -d "My amazing post"
  python main.py check-config
"""

import sys
from pathlib import Path

# Reconfigure stdout and stderr to UTF-8 to prevent UnicodeEncodeError on Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box

from config import AppConfig
from platforms import PostPayload, FacebookPlatform, InstagramPlatform, LinkedInPlatform
from utils import validate_image, prepare_image, image_info, ImageValidationError

console = Console()

ALL_PLATFORMS = ["facebook", "instagram", "linkedin"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_platform_adapters(cfg: AppConfig, platforms: list[str]) -> dict:
    """Instantiate only the adapters for selected platforms."""
    adapters = {}
    for name in platforms:
        raw_cfg = getattr(cfg, name, None)
        if isinstance(raw_cfg, EnvironmentError):
            console.print(f"  [yellow]⚠[/] {name.capitalize()}: {raw_cfg}")
            continue
        if raw_cfg is None:
            continue
        if name == "facebook":
            adapters[name] = FacebookPlatform(raw_cfg)
        elif name == "instagram":
            adapters[name] = InstagramPlatform(raw_cfg)
        elif name == "linkedin":
            adapters[name] = LinkedInPlatform(raw_cfg)
    return adapters


def _print_results(results: list) -> None:
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
    table.add_column("Platform", style="bold", width=12)
    table.add_column("Status", width=8)
    table.add_column("Details")

    for r in results:
        status = "[green]✓ OK[/]" if r.success else "[red]✗ Fail[/]"
        detail = r.url or r.error or f"ID: {r.post_id}"
        table.add_row(r.platform, status, detail)

    console.print(table)


# ── Commands ──────────────────────────────────────────────────────────────────

@click.group()
def cli():
    """🤖 Autoposter — One-click social media posting."""


@cli.command()
@click.option("--image", "-i", required=True, type=click.Path(exists=True), help="Path to image file")
@click.option("--description", "-d", required=True, help="Post caption (used as-is for all platforms)")
@click.option("--image-url", "-u", default=None, help="Public URL of image (required for Instagram)")
def post(image, description, image_url):
    """Post your image and description to Facebook, Instagram, and LinkedIn."""
    image_path = Path(image)
    platforms = ALL_PLATFORMS

    console.print(Panel(
        f"[bold]Autoposter[/]\n"
        f"Image: [cyan]{image_path.name}[/]  |  Platforms: [cyan]{', '.join(platforms)}[/]",
        border_style="dim"
    ))

    # ── Image info ────────────────────────────────────────────────────────────
    info = image_info(image_path)
    console.print(f"  [dim]Image:[/] {info['size']}  {info['file_size']}  {info['format']}")

    # ── Validate image per platform ───────────────────────────────────────────
    console.print("\n[bold]Validating image...[/]")
    for p in platforms:
        try:
            validate_image(image_path, p)
            console.print(f"  [green]✓[/] {p.capitalize()}")
        except ImageValidationError as e:
            console.print(f"  [yellow]⚠[/] {p.capitalize()}: {e}")

    # ── Load config ───────────────────────────────────────────────────────────
    try:
        cfg = AppConfig.from_env(platforms)
    except EnvironmentError as e:
        console.print(f"\n[red]Config error:[/] {e}")
        raise SystemExit(1)

    # ── Prepare image (convert if needed) ────────────────────────────────────
    console.print("\n[bold]Preparing image...[/]")
    prepared_path = prepare_image(image_path)
    if prepared_path != image_path:
        console.print(f"  [dim]Converted image to JPEG: {prepared_path.name}[/]")

    payload_base = {"image_path": prepared_path, "image_url": image_url, "caption": description}

    # ── Build adapters and post ───────────────────────────────────────────────
    adapters = _build_platform_adapters(cfg, platforms)
    results = []

    console.print("\n[bold]Posting to all platforms...[/]")
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as progress:
        for platform, adapter in adapters.items():
            task = progress.add_task(f"  Posting to {platform}...", total=None)
            payload = PostPayload(**payload_base)
            result = adapter._safe_publish(payload)
            results.append(result)
            progress.remove_task(task)

    # ── Results ───────────────────────────────────────────────────────────────
    console.print()
    _print_results(results)


@cli.command("check-config")
def check_config():
    """Verify that all .env credentials are present."""
    console.print(Panel("[bold]Config Check[/]", border_style="dim"))

    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column("Key", style="dim", width=30)
    table.add_column("Status")

    import os
    from dotenv import load_dotenv
    load_dotenv()

    keys = [
        "FACEBOOK_PAGE_ID", "FACEBOOK_ACCESS_TOKEN",
        "INSTAGRAM_ACCOUNT_ID", "INSTAGRAM_ACCESS_TOKEN",
        "LINKEDIN_ACCESS_TOKEN", "LINKEDIN_AUTHOR_URN",
    ]

    for key in keys:
        val = os.getenv(key, "").strip()
        if val:
            masked = val[:6] + "..." + val[-4:] if len(val) > 12 else "****"
            table.add_row(key, f"[green]✓[/]  {masked}")
        else:
            table.add_row(key, "[red]✗  Missing[/]")

    console.print(table)


@cli.command("serve")
@click.option("--port", default=None, help="Port to run the API server on")
@click.option("--host", default="0.0.0.0", help="Host to run the API server on")
def serve(port, host):
    """Start the FastAPI backend server."""
    import uvicorn
    import os
    
    if port is None:
        port = int(os.environ.get("PORT", 8000))
    else:
        port = int(port)

    console.print(Panel(f"[bold green]Starting FastAPI backend server on http://{host}:{port}...[/]", border_style="dim"))
    
    # We run uvicorn programmatically. We specify app.py location
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Disable hot-reload in production environments like Render
    use_reload = not bool(os.environ.get("RENDER"))
    
    uvicorn.run("app:app", host=host, port=port, reload=use_reload)


if __name__ == "__main__":
    cli()

