#!/usr/bin/env python3
"""
Configuration for icon automation
Edit this file to change what platforms/sizes are generated
"""

# Icon padding (as percentage of final size)
IOS_PADDING_PERCENT = 15
ANDROID_PADDING_PERCENT = 15

# iOS icon sizes (pt_size, scale, idiom, platform)
IOS_ICON_DEFINITIONS = [
    # iOS Icon (1024pt only)
    {"pt_size": 1024, "scale": 1, "idiom": "universal", "platform": "ios"},

    # macOS Icons
    {"pt_size": 16, "scale": 1, "idiom": "mac", "platform": None},
    {"pt_size": 16, "scale": 2, "idiom": "mac", "platform": None},
    {"pt_size": 32, "scale": 1, "idiom": "mac", "platform": None},
    {"pt_size": 32, "scale": 2, "idiom": "mac", "platform": None},
    {"pt_size": 128, "scale": 1, "idiom": "mac", "platform": None},
    {"pt_size": 128, "scale": 2, "idiom": "mac", "platform": None},
    {"pt_size": 256, "scale": 1, "idiom": "mac", "platform": None},
    {"pt_size": 256, "scale": 2, "idiom": "mac", "platform": None},
    {"pt_size": 512, "scale": 1, "idiom": "mac", "platform": None},
    {"pt_size": 512, "scale": 2, "idiom": "mac", "platform": None},
]

# iOS appearance variants
IOS_APPEARANCES = [
    {"mode": "", "suffix": "", "json_value": None},
    {"mode": "dark", "suffix": "_dark", "json_value": "dark"},
    {"mode": "tinted", "suffix": "_tinted", "json_value": "tinted"}
]

# Android icon sizes (density, size_px)
ANDROID_ICON_SIZES = [
    {"density": "mdpi", "size": 48},
    {"density": "hdpi", "size": 72},
    {"density": "xhdpi", "size": 96},
    {"density": "xxhdpi", "size": 144},
    {"density": "xxxhdpi", "size": 192},
]

# Android adaptive icon size
ANDROID_ADAPTIVE_SIZE = 108  # Adaptive icons are 108x108dp
ANDROID_SAFE_ZONE = 66       # Only center 66dp guaranteed visible
