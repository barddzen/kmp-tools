#!/usr/bin/env python3
"""
iOS icon generation
Creates Assets.xcassets folder with all required iOS/macOS icon sizes
"""

import json
import logging
from pathlib import Path
from PIL import Image, ImageEnhance

from config import IOS_ICON_DEFINITIONS, IOS_APPEARANCES

logger = logging.getLogger(__name__)


class iOSIconGenerator:
    """Generates iOS icon assets"""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.output_path = self.project_root / "iosApp" / "iosApp" / "Assets.xcassets"

    def resize_and_save_no_alpha(self, img, size, output_path):
        """
        Resize and save image WITHOUT alpha channel (Apple requirement)
        """
        try:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
        except AttributeError:
            resized = img.resize((size, size), Image.LANCZOS)

        # Remove alpha channel if present
        if resized.mode == 'RGBA':
            background = Image.new('RGB', resized.size, (255, 255, 255))
            background.paste(resized, mask=resized.split()[3])
            resized = background
        elif resized.mode != 'RGB':
            resized = resized.convert('RGB')

        resized.save(output_path, format="PNG")

    def apply_appearance_variant(self, img, mode):
        """
        Apply iOS appearance variants (dark/tinted)
        """
        variant_img = img.copy()

        if variant_img.mode != 'RGBA':
            variant_img = variant_img.convert('RGBA')

        if mode == "dark":
            variant_img = ImageEnhance.Brightness(variant_img).enhance(1.2)
            variant_img = ImageEnhance.Color(variant_img).enhance(1.3)
            variant_img = ImageEnhance.Contrast(variant_img).enhance(1.15)
        elif mode == "tinted":
            variant_img = ImageEnhance.Color(variant_img).enhance(0.2)
            variant_img = ImageEnhance.Brightness(variant_img).enhance(1.15)

        return variant_img

    def create_root_json_files(self, assets_dir):
        """Generate root Contents.json and AccentColor.colorset"""

        # Assets.xcassets/Contents.json
        root_json_path = assets_dir / "Contents.json"
        root_json_data = {"info": {"version": 1, "author": "xcode"}}
        with open(root_json_path, 'w') as f:
            json.dump(root_json_data, f, indent=4)

        logger.info("  Generated Assets.xcassets/Contents.json")

        # AccentColor.colorset/Contents.json
        colorset_dir = assets_dir / "AccentColor.colorset"
        colorset_dir.mkdir(exist_ok=True)
        colorset_json_path = colorset_dir / "Contents.json"
        colorset_json_data = {
            "colors": [{"idiom": "universal"}],
            "info": {"version": 1, "author": "xcode"}
        }
        with open(colorset_json_path, 'w') as f:
            json.dump(colorset_json_data, f, indent=4)

        logger.info("  Generated AccentColor.colorset/Contents.json")

    def generate(self, source_img):
        """
        Generate complete iOS icon set

        Args:
            source_img: PIL Image

        Returns:
            Number of files generated
        """
        logger.info("")
        logger.info("iOS Icons")
        logger.info("-" * 40)

        base_img = source_img.convert('RGBA')

        # Create output directory
        assets_dir = self.output_path
        assets_dir.mkdir(parents=True, exist_ok=True)

        self.create_root_json_files(assets_dir)

        # Generate AppIcon.appiconset
        appiconset_dir = assets_dir / "AppIcon.appiconset"
        appiconset_dir.mkdir(exist_ok=True)

        # Prepare Contents.json structure
        contents_data = {
            "images": [],
            "info": {
                "version": 1,
                "author": "xcode",
                "properties": {
                    "provides-app-icon-for-dark-appearance": True,
                    "provides-app-icon-for-tinted-tertiary-appearance": True
                }
            }
        }

        files_created = 0

        for definition in IOS_ICON_DEFINITIONS:
            pt_size = definition["pt_size"]
            scale = definition["scale"]
            idiom = definition["idiom"]
            platform = definition["platform"]

            pixel_size = int(round(pt_size * scale))
            pt_size_str = f"{pt_size}x{pt_size}"

            # Only 1024pt iOS icon gets appearance variants
            is_ios_marketing = (idiom == "universal" and platform == "ios")
            appearances = IOS_APPEARANCES if is_ios_marketing else [IOS_APPEARANCES[0]]

            for app_info in appearances:
                app_mode = app_info["mode"]
                app_suffix = app_info["suffix"]
                json_value = app_info["json_value"]

                # Filename logic
                if scale == 1 and not app_mode:
                    filename = f"{pt_size_str}{app_suffix}.png"
                else:
                    filename = f"{pt_size_str}@{scale}x{app_suffix}.png"

                variant_img = self.apply_appearance_variant(base_img, app_mode)

                output_path = appiconset_dir / filename
                self.resize_and_save_no_alpha(variant_img, pixel_size, output_path)

                files_created += 1

                # Add to Contents.json
                image_info = {
                    "idiom": idiom,
                    "size": pt_size_str,
                    "filename": filename
                }

                if idiom == "mac":
                    image_info["scale"] = f"{scale}x"

                if platform:
                    image_info["platform"] = platform

                if json_value:
                    image_info["appearances"] = [
                        {
                            "appearance": "luminosity",
                            "value": json_value
                        }
                    ]

                contents_data["images"].append(image_info)

        # Write Contents.json
        json_path = appiconset_dir / "Contents.json"
        with open(json_path, 'w') as f:
            json.dump(contents_data, f, indent=4)

        logger.info(f"  Generated {files_created} icon files")
        logger.info(f"  Output: {assets_dir}")

        return files_created
