#!/usr/bin/env python3
"""
Image processing for iOS screenshot generation
"""

import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from config import GRADIENTS, FONT_PATHS

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles image manipulation for iOS screenshots"""

    def __init__(self):
        """Initialize the image processor"""
        self.font_cache = {}

    def create_gradient_background(self, size, gradient_name):
        """
        Create a vertical gradient background

        Args:
            size: Tuple of (width, height)
            gradient_name: 'gradient_blue' (iOS uses blue theme)

        Returns:
            PIL Image with gradient
        """
        colors = GRADIENTS[gradient_name]
        color1 = colors['top']
        color2 = colors['bottom']

        base = Image.new('RGB', size, color1)
        mask = Image.new('L', size)
        mask_data = []

        for y in range(size[1]):
            # Linear gradient from top to bottom
            alpha = int(255 * (y / size[1]))
            mask_data.extend([alpha] * size[0])

        mask.putdata(mask_data)

        # Create gradient by compositing two colors with mask
        bottom = Image.new('RGB', size, color2)
        base.paste(bottom, (0, 0), mask)

        return base

    def get_font(self, size):
        """
        Get the best available bold font

        Args:
            size: Font size in points

        Returns:
            PIL ImageFont
        """
        # Check cache
        if size in self.font_cache:
            return self.font_cache[size]

        # Try to find a good bold font
        for font_path in FONT_PATHS:
            try:
                font = ImageFont.truetype(font_path, size)
                self.font_cache[size] = font
                return font
            except (OSError, IOError):
                continue

        # Fallback to default font
        logger.warning("Using default font - install SF Pro Display or Roboto Bold for best results")
        font = ImageFont.load_default()
        self.font_cache[size] = font
        return font

    def wrap_text(self, text, font, max_width, draw):
        """
        Wrap text to fit within max_width

        Args:
            text: Text to wrap
            font: PIL Font to use
            max_width: Maximum width in pixels
            draw: ImageDraw object for measuring

        Returns:
            List of text lines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def calculate_optimal_font_size(self, title, subtitle, target_size):
        """
        Calculate optimal font sizes for title and subtitle

        Args:
            title: Title text
            subtitle: Subtitle text
            target_size: Tuple of (width, height) for canvas

        Returns:
            Tuple of (title_font_size, subtitle_font_size, total_height)
        """
        canvas_width, canvas_height = target_size
        max_text_width = int(canvas_width * 0.90)

        # Start with reasonable sizes
        title_size = int(canvas_height * 0.05)  # Title at 5% of height
        subtitle_size = int(canvas_height * 0.03)  # Subtitle at 3% of height

        min_title_size = int(canvas_height * 0.025)
        min_subtitle_size = int(canvas_height * 0.02)

        # Create temporary image for measuring
        temp_img = Image.new('RGB', (100, 100))
        temp_draw = ImageDraw.Draw(temp_img)

        # Adjust title size to fit in one line
        while title_size > min_title_size:
            font = self.get_font(title_size)
            bbox = temp_draw.textbbox((0, 0), title, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_text_width:
                break
            title_size -= 2

        # Adjust subtitle size to fit in one line
        while subtitle_size > min_subtitle_size:
            font = self.get_font(subtitle_size)
            bbox = temp_draw.textbbox((0, 0), subtitle, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_text_width:
                break
            subtitle_size -= 2

        # Calculate total height needed
        title_font = self.get_font(title_size)
        subtitle_font = self.get_font(subtitle_size)

        title_bbox = temp_draw.textbbox((0, 0), title, font=title_font)
        subtitle_bbox = temp_draw.textbbox((0, 0), subtitle, font=subtitle_font)

        title_height = title_bbox[3] - title_bbox[1]
        subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]

        # Add spacing between lines (20% of title height)
        line_spacing = int(title_height * 0.3)

        total_height = title_height + line_spacing + subtitle_height

        return title_size, subtitle_size, total_height

    def create_screenshot_with_text(self, source_image_path, title, subtitle,
                                   target_size, gradient_name, screenshot_scale=0.95):
        """
        Create a professional screenshot with title, subtitle, and gradient background

        Args:
            source_image_path: Path to source screenshot
            title: Title text
            subtitle: Subtitle text
            target_size: Tuple of (width, height) for final image
            gradient_name: 'gradient_blue' (iOS theme)
            screenshot_scale: How much of canvas the screenshot takes (0.0-1.0)

        Returns:
            PIL Image
        """
        canvas_width, canvas_height = target_size

        # Create gradient background
        canvas = self.create_gradient_background(target_size, gradient_name)

        # Calculate optimal font sizes
        title_font_size, subtitle_font_size, text_total_height = \
            self.calculate_optimal_font_size(title, subtitle, target_size)

        title_font = self.get_font(title_font_size)
        subtitle_font = self.get_font(subtitle_font_size)

        # Calculate text area with padding
        text_area_height = text_total_height + int(canvas_height * 0.04)

        # Load and resize screenshot
        screenshot = Image.open(source_image_path)

        # Calculate available space for screenshot
        available_height = int((canvas_height - text_area_height) * screenshot_scale)
        available_width = int(canvas_width * screenshot_scale)

        # Resize screenshot maintaining aspect ratio
        screenshot_ratio = screenshot.width / screenshot.height
        target_ratio = available_width / available_height

        if screenshot_ratio > target_ratio:
            # Screenshot is wider - fit to width
            new_width = available_width
            new_height = int(new_width / screenshot_ratio)
        else:
            # Screenshot is taller - fit to height
            new_height = available_height
            new_width = int(new_height * screenshot_ratio)

        screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Position screenshot centered, below text
        screenshot_x = (canvas_width - new_width) // 2
        screenshot_y = text_area_height + ((canvas_height - text_area_height - new_height) // 2)

        # Paste screenshot onto canvas
        canvas.paste(screenshot, (screenshot_x, screenshot_y))

        # Draw text
        draw = ImageDraw.Draw(canvas)

        # Calculate text positions (centered)
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)

        title_width = title_bbox[2] - title_bbox[0]
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]

        title_x = (canvas_width - title_width) // 2
        subtitle_x = (canvas_width - subtitle_width) // 2

        # Position text at top with padding
        top_padding = int(canvas_height * 0.02)
        title_y = top_padding

        title_height = title_bbox[3] - title_bbox[1]
        line_spacing = int(title_height * 0.3)
        subtitle_y = title_y + title_height + line_spacing

        # Draw text with slight shadow for better readability
        shadow_offset = max(2, int(canvas_height * 0.001))

        # Title shadow
        draw.text((title_x + shadow_offset, title_y + shadow_offset),
                 title, font=title_font, fill=(0, 0, 0, 128))
        # Title
        draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255, 255))

        # Subtitle shadow
        draw.text((subtitle_x + shadow_offset, subtitle_y + shadow_offset),
                 subtitle, font=subtitle_font, fill=(0, 0, 0, 128))
        # Subtitle
        draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(255, 255, 255, 200))

        return canvas
