#!/usr/bin/env python3
"""
Android icon generation
Creates mipmap folders with all required Android icon sizes
"""

import logging
from pathlib import Path
from PIL import Image

from config import ANDROID_ICON_SIZES

logger = logging.getLogger(__name__)


class AndroidIconGenerator:
    """Generates Android icon assets"""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.output_path = self.project_root / "composeApp" / "src" / "androidMain" / "res"

    def resize_and_save(self, img, size, output_path):
        """Resize and save image"""
        try:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
        except AttributeError:
            resized = img.resize((size, size), Image.LANCZOS)

        # Ensure RGB mode for compatibility
        if resized.mode == 'RGBA':
            background = Image.new('RGB', resized.size, (255, 255, 255))
            background.paste(resized, mask=resized.split()[3])
            resized = background
        elif resized.mode != 'RGB':
            resized = resized.convert('RGB')

        resized.save(output_path, format="PNG")

    def generate(self, source_img):
        """
        Generate complete Android icon set

        Args:
            source_img: PIL Image

        Returns:
            Number of files generated
        """
        logger.info("")
        logger.info("Android Icons")
        logger.info("-" * 40)

        base_img = source_img.convert('RGBA')

        files_created = 0

        for size_def in ANDROID_ICON_SIZES:
            density = size_def["density"]
            size = size_def["size"]

            # Create mipmap directory
            mipmap_dir = self.output_path / f"mipmap-{density}"
            mipmap_dir.mkdir(parents=True, exist_ok=True)

            # Generate ic_launcher.png
            output_path = mipmap_dir / "ic_launcher.png"
            self.resize_and_save(base_img, size, output_path)
            files_created += 1

            # Generate ic_launcher_round.png (same image, Android handles rounding)
            round_path = mipmap_dir / "ic_launcher_round.png"
            self.resize_and_save(base_img, size, round_path)
            files_created += 1

        logger.info(f"  Generated {files_created} icon files")
        logger.info(f"  Output: {self.output_path}")

        return files_created
