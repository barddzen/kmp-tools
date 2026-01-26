#!/usr/bin/env python3
"""
iOS-only icon automation script
Generates iOS icons from a single source image for Xcode projects
"""

import sys
import logging
from pathlib import Path
from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

from ios_generator import iOSIconGenerator


def find_assets_xcassets(project_root):
    """
    Find Assets.xcassets in an iOS-only Xcode project.

    iOS-only projects typically have structure:
    - ProjectName/Assets.xcassets (most common)
    - ProjectName/ProjectName/Assets.xcassets (alternative)

    Unlike KMP projects which use:
    - iosApp/iosApp/Assets.xcassets
    """
    project_path = Path(project_root)
    project_name = project_path.name

    # Search patterns for iOS-only projects (in order of preference)
    search_patterns = [
        # Direct child: ProjectName/Assets.xcassets
        project_path / project_name / "Assets.xcassets",
        # Any Assets.xcassets in immediate subdirectory
        *list(project_path.glob("*/Assets.xcassets")),
        # Deeper nested (less common)
        *list(project_path.glob("*/*/Assets.xcassets")),
    ]

    # Also check for .xcodeproj to confirm it's an Xcode project
    xcodeproj = list(project_path.glob("*.xcodeproj"))

    for pattern in search_patterns:
        if isinstance(pattern, Path) and pattern.exists():
            return pattern

    # If no existing Assets.xcassets found, determine where to create one
    # Look for the main source folder (same name as project, or contains Swift files)
    for subdir in project_path.iterdir():
        if subdir.is_dir() and subdir.name == project_name:
            return subdir / "Assets.xcassets"
        if subdir.is_dir() and list(subdir.glob("*.swift")):
            return subdir / "Assets.xcassets"

    return None


def validate_source_image(image_path):
    """Validate source image meets requirements"""
    try:
        img = Image.open(image_path)
    except Exception as e:
        logger.error(f"Failed to open image: {e}")
        return None

    width, height = img.size

    logger.info(f"Source: {image_path}")
    logger.info(f"Size: {width}x{height}px, Mode: {img.mode}")

    if width < 1024 or height < 1024:
        logger.error(f"Image too small: {width}x{height}px (minimum 1024x1024)")
        return None

    if width != height:
        logger.warning(f"Image not square, cropping to center...")
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))
        logger.info(f"Cropped to: {img.size[0]}x{img.size[1]}px")

    return img


def main():
    if len(sys.argv) != 3:
        logger.error("Usage: python3 generate_icons.py <project_root> <source_image>")
        sys.exit(1)

    project_root = sys.argv[1]
    source_path = sys.argv[2]

    logger.info("")
    logger.info("=" * 50)
    logger.info("iOS ICON GENERATOR")
    logger.info("=" * 50)

    # Validate project exists
    project_path = Path(project_root)
    if not project_path.exists():
        logger.error(f"Project not found: {project_root}")
        sys.exit(1)

    # Find Assets.xcassets location
    assets_path = find_assets_xcassets(project_root)

    if assets_path is None:
        logger.error("Could not determine Assets.xcassets location")
        logger.error("Make sure you're in an Xcode project directory")
        sys.exit(1)

    logger.info(f"Assets path: {assets_path}")

    # Check for .xcodeproj to confirm it's an Xcode project
    xcodeproj = list(project_path.glob("*.xcodeproj"))
    if not xcodeproj:
        logger.warning("No .xcodeproj found - is this an Xcode project?")

    # Validate source image
    if not Path(source_path).exists():
        logger.error(f"Source image not found: {source_path}")
        sys.exit(1)

    source_img = validate_source_image(source_path)
    if source_img is None:
        sys.exit(1)

    # Generate iOS icons
    try:
        ios_gen = iOSIconGenerator(assets_path)
        total_files = ios_gen.generate(source_img)
    except Exception as e:
        logger.error(f"iOS generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    logger.info("")
    logger.info("=" * 50)
    logger.info(f"COMPLETE: {total_files} files generated")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()
