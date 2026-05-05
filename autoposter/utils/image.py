"""
utils/image.py
───────────────
Image validation and resizing helpers.
Ensures images meet platform constraints before uploading.
"""

from pathlib import Path
from PIL import Image

# Platform constraints
CONSTRAINTS = {
    "facebook":  {"max_size_mb": 10, "min_w": 400,  "min_h": 400,  "formats": ["JPEG", "PNG", "GIF", "WEBP"]},
    "instagram": {"max_size_mb": 8,  "min_w": 320,  "min_h": 320,  "formats": ["JPEG", "PNG"]},
    "linkedin":  {"max_size_mb": 5,  "min_w": 552,  "min_h": 276,  "formats": ["JPEG", "PNG", "GIF"]},
}


class ImageValidationError(ValueError):
    pass


def validate_image(path: Path, platform: str) -> None:
    """
    Raises ImageValidationError if the image doesn't meet platform constraints.
    """
    if not path.exists():
        raise ImageValidationError(f"Image not found: {path}")

    constraints = CONSTRAINTS.get(platform, {})

    # File size check
    size_mb = path.stat().st_size / (1024 * 1024)
    max_mb = constraints.get("max_size_mb", 10)
    if size_mb > max_mb:
        raise ImageValidationError(
            f"Image too large for {platform}: {size_mb:.1f}MB (max {max_mb}MB)"
        )

    with Image.open(path) as img:
        fmt = img.format
        w, h = img.size

        # Format check
        allowed = constraints.get("formats", [])
        if allowed and fmt not in allowed:
            raise ImageValidationError(
                f"{platform} does not support {fmt}. Allowed: {', '.join(allowed)}"
            )

        # Dimension check
        min_w = constraints.get("min_w", 0)
        min_h = constraints.get("min_h", 0)
        if w < min_w or h < min_h:
            raise ImageValidationError(
                f"Image too small for {platform}: {w}×{h}px (min {min_w}×{min_h}px)"
            )


def prepare_image(path: Path, output_dir: Path | None = None) -> Path:
    """
    Converts non-JPEG images to JPEG and strips EXIF data.
    Returns the (possibly new) path to use for uploading.
    """
    with Image.open(path) as img:
        if img.format == "JPEG":
            return path  # Already fine

        out_dir = output_dir or path.parent
        out_path = out_dir / (path.stem + "_converted.jpg")

        # Convert to RGB (handles RGBA PNG etc.)
        rgb = img.convert("RGB")
        rgb.save(out_path, "JPEG", quality=92, optimize=True)
        return out_path


def image_info(path: Path) -> dict:
    """Return a summary dict of image metadata."""
    with Image.open(path) as img:
        return {
            "path": str(path),
            "format": img.format,
            "size": f"{img.width}×{img.height}px",
            "file_size": f"{path.stat().st_size / 1024:.0f} KB",
            "mode": img.mode,
        }
