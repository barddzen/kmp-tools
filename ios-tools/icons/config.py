#!/usr/bin/env python3
"""
Configuration for iOS-only icon automation
"""

# iOS icon sizes (pt_size, scale, idiom, platform)
IOS_ICON_DEFINITIONS = [
    # iOS Icon (1024pt only - universal)
    {"pt_size": 1024, "scale": 1, "idiom": "universal", "platform": "ios"},

    # macOS Icons (for Mac Catalyst / macOS target)
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

# iOS appearance variants (light, dark, tinted)
IOS_APPEARANCES = [
    {"mode": "", "suffix": "", "json_value": None},
    {"mode": "dark", "suffix": "_dark", "json_value": "dark"},
    {"mode": "tinted", "suffix": "_tinted", "json_value": "tinted"}
]
