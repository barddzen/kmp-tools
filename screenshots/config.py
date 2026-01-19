#!/usr/bin/env python3
"""
Configuration and constants for screenshot automation
Edit this file to change screen sizes, gradients, etc.
"""

# Screenshot dimensions for each platform and device
SIZES = {
    'android': {
        'phone': [
            (1080, 1920),  # Standard phone
            (1440, 2560),  # High-res phone
        ],
    },
    'ios_iphone': {
        'iphone': [
            (1320, 2868),  # 6.9" iPhone (REQUIRED)
            (1290, 2796),  # 6.7" iPhone
            (1284, 2778),  # 6.5" iPhone
            (1242, 2208),  # 5.5" iPhone
        ],
    },
    'ios_ipad': {
        'ipad': [
            (2064, 2752),  # 13" iPad (REQUIRED)
            (1668, 2388),  # 11" iPad
        ],
    },
}

# Size labels for folder organization
SIZE_LABELS = {
    (1080, 1920): 'phone_1080x1920',
    (1440, 2560): 'phone_1440x2560',
    (1320, 2868): '6.9_inch',
    (1290, 2796): '6.7_inch',
    (1284, 2778): '6.5_inch',
    (1242, 2208): '5.5_inch',
    (2064, 2752): '13_inch',
    (1668, 2388): '11_inch',
}

# Gradient colors
GRADIENTS = {
    'gradient_green': {
        'top': (0, 128, 64),     # Fishing green
        'bottom': (0, 64, 32),   # Dark green
    },
    'gradient_blue': {
        'top': (30, 144, 255),   # Dodger blue
        'bottom': (0, 71, 171),  # Dark blue
    },
}

# Font paths (in order of preference)
FONT_PATHS = [
    '/System/Library/Fonts/SFNSDisplay-Bold.otf',  # macOS San Francisco Bold
    '/System/Library/Fonts/Helvetica.ttc',  # macOS Helvetica
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
    '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf',  # Android/Linux Roboto
    'Arial Bold',
    'Helvetica Bold',
]

# Title generation settings
TITLE_MAX_LENGTH = 30
SUBTITLE_MAX_LENGTH = 50

# Screenshot scale (how much of canvas the screenshot takes)
DEFAULT_SCREENSHOT_SCALE = 0.95

# Image file extensions
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
