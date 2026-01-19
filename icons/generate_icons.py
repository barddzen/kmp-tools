#!/usr/bin/env python3
"""
Main icon automation script
Generates iOS and Android icons from a single source image
"""

import sys
import logging
from pathlib import Path
from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

from ios_generator import iOSIconGenerator
from android_generator import AndroidIconGenerator


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
    logger.info("KMP ICON GENERATOR")
    logger.info("=" * 50)

    # Validate project structure
    project_path = Path(project_root)
    if not project_path.exists():
        logger.error(f"Project not found: {project_root}")
        sys.exit(1)

    ios_path = project_path / "iosApp"
    android_path = project_path / "composeApp"

    if not ios_path.exists() and not android_path.exists():
        logger.error("Not a KMP project (no iosApp or composeApp folder)")
        sys.exit(1)

    # Validate source image
    if not Path(source_path).exists():
        logger.error(f"Source image not found: {source_path}")
        sys.exit(1)

    source_img = validate_source_image(source_path)
    if source_img is None:
        sys.exit(1)

    total_files = 0

    # Generate iOS icons
    if ios_path.exists():
        try:
            ios_gen = iOSIconGenerator(project_root)
            total_files += ios_gen.generate(source_img)
        except Exception as e:
            logger.error(f"iOS generation failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        logger.info("Skipping iOS (no iosApp folder)")

    # Generate Android icons
    if android_path.exists():
        try:
            android_gen = AndroidIconGenerator(project_root)
            total_files += android_gen.generate(source_img)
        except Exception as e:
            logger.error(f"Android generation failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        logger.info("Skipping Android (no composeApp folder)")

    logger.info("")
    logger.info("=" * 50)
    logger.info(f"COMPLETE: {total_files} files generated")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()
