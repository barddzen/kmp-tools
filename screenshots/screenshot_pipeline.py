#!/usr/bin/env python3
"""
Automated Screenshot Pipeline for App Store Submissions

Analyzes screenshots using Claude Vision API, ranks them strategically,
and generates professional store screenshots with titles, subtitles, and
gradient backgrounds.

Usage:
    # Analyze screenshots and generate config (auto-orders by default)
    python screenshot_pipeline.py --analyze
    
    # Analyze without auto-ordering (preserve filenames)
    python screenshot_pipeline.py --analyze --preserve-names
    
    # Generate screenshots from config
    python screenshot_pipeline.py --generate
    
    # Full auto (analyze + generate in one shot)
    python screenshot_pipeline.py --auto
    
    # Regenerate specific screenshots
    python screenshot_pipeline.py --regenerate android/01_map.png ios_iphone/02_forecast.png
"""

import os
import sys
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
import argparse

from vision_analyzer import VisionAnalyzer
from image_processor import ImageProcessor
from config import SIZES, SIZE_LABELS, IMAGE_EXTENSIONS, GRADIENTS, DEFAULT_SCREENSHOT_SCALE

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class ScreenshotPipeline:
    """Main screenshot automation pipeline"""
    
    def __init__(self, base_dir='ScreenShots'):
        """
        Initialize the pipeline
        
        Args:
            base_dir: Base directory containing Input/ and Output/ folders
        """
        self.base_dir = Path(base_dir)
        self.input_dir = self.base_dir / 'Input'
        self.output_dir = self.base_dir / 'Output'
        self.config_file = self.base_dir / 'screenshot_config.json'
        
        self.analyzer = None  # Lazy load when needed
        self.processor = ImageProcessor()
    
    def analyze(self, preserve_names=False, force_files=None):
        """
        Analyze screenshots and generate configuration file
        
        Args:
            preserve_names: If True, don't auto-order/rename files
            force_files: List of specific files to re-analyze (None = all files)
        """
        logger.info("=" * 70)
        logger.info("SCREENSHOT ANALYZER - Powered by Claude Vision")
        logger.info("=" * 70)
        
        if preserve_names:
            logger.info("Mode: PRESERVE NAMES (no auto-ordering)")
        else:
            logger.info("Mode: AUTO-ORDER (Claude ranks screenshots strategically)")
        
        logger.info("")
        
        # Check if API key is set
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            logger.error("Error: ANTHROPIC_API_KEY environment variable not set")
            logger.error("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
            sys.exit(1)
        
        # Initialize analyzer
        self.analyzer = VisionAnalyzer(api_key=api_key)
        
        # Check input directories
        if not self.input_dir.exists():
            logger.error(f"Error: Input directory not found: {self.input_dir}")
            logger.error("Create the directory structure:")
            logger.error(f"  {self.input_dir}/android/")
            logger.error(f"  {self.input_dir}/ios_iphone/")
            logger.error(f"  {self.input_dir}/ios_ipad/")
            sys.exit(1)
        
        # Scan for screenshots
        platforms = {
            'android': ('android', 'phone'),
            'ios_iphone': ('ios_iphone', 'iphone'),
            'ios_ipad': ('ios_ipad', 'ipad'),
        }
        
        config = {
            'version': '1.0.0',
            'generated': datetime.now().isoformat(),
            'auto_ordered': not preserve_names,
            'platforms': {}
        }
        
        total_analyzed = 0
        
        for platform_dir, (platform, device_type) in platforms.items():
            platform_path = self.input_dir / platform_dir
            
            if not platform_path.exists():
                logger.warning(f"⚠️  Skipping {platform_dir} - directory not found")
                continue
            
            # Find all images
            image_files = sorted([
                f for f in platform_path.iterdir()
                if f.is_file() and f.suffix in IMAGE_EXTENSIONS
            ])
            
            if not image_files:
                logger.warning(f"⚠️  No images found in {platform_path}")
                continue
            
            # Determine theme
            theme = 'gradient_green' if platform == 'android' else 'gradient_blue'
            
            logger.info(f"\n{platform_dir.upper()}:")
            logger.info(f"  Found {len(image_files)} screenshots")
            logger.info(f"  Theme: {theme}")
            logger.info("")
            
            if preserve_names:
                # Use existing order, analyze individually
                screenshots = []
                for img_file in image_files:
                    if force_files and img_file.name not in force_files:
                        continue
                    
                    analysis = self.analyzer.analyze_screenshot(img_file, platform, device_type)
                    
                    screenshot_config = {
                        'file': img_file.name,
                        'original_name': img_file.name,
                        'title': analysis['title'],
                        'subtitle': analysis['subtitle'],
                        'detected_content': analysis['detected_content'],
                        'confidence': analysis['confidence']
                    }
                    
                    screenshots.append(screenshot_config)
                    total_analyzed += 1
            else:
                # Use smart ranking
                ranked_results = self.analyzer.analyze_and_rank_screenshots(
                    image_files, platform, device_type
                )
                
                screenshots = []
                
                # Build a mapping from filename to actual path for fuzzy matching
                file_map = {f.name: f for f in image_files}
                
                # First pass: move all files to temp names to avoid conflicts
                temp_mappings = []
                for result in ranked_results:
                    original_name = result['original_name']
                    
                    # Normalize unicode whitespace for comparison
                    # macOS uses \u202f (narrow no-break space) in screenshot names
                    def normalize_whitespace(s):
                        import unicodedata
                        # Replace all unicode whitespace with regular space
                        return ''.join(' ' if unicodedata.category(c) in ('Zs', 'Zl', 'Zp') else c for c in s)
                    
                    normalized_name = normalize_whitespace(original_name)
                    
                    # Try to find matching file
                    matched = None
                    for fname, fpath in file_map.items():
                        if normalize_whitespace(fname) == normalized_name:
                            matched = fpath
                            break
                    
                    if matched:
                        original_path = matched
                    else:
                        logger.warning(f"  ⚠️ File not found: {original_name}")
                        logger.warning(f"     Available files: {list(file_map.keys())}")
                        continue
                    
                    temp_name = f"_temp_{result['rank']:02d}_{original_path.stem}.png"
                    temp_path = platform_path / temp_name
                    
                    shutil.move(str(original_path), str(temp_path))
                    temp_mappings.append((result, temp_path, original_path.name))
                    
                    # Remove from file_map so we don't match it again
                    if original_path.name in file_map:
                        del file_map[original_path.name]
                
                # Second pass: move from temp to final names
                for result, temp_path, actual_name in temp_mappings:
                    # Create filename from title (sanitized)
                    title_slug = result['title'].replace(' ', '_').replace('"', '').replace("'", '')
                    title_slug = ''.join(c for c in title_slug if c.isalnum() or c == '_')
                    new_name = f"{result['rank']:02d}_{title_slug}.png"
                    new_path = platform_path / new_name
                    
                    logger.info(f"  📝 Renaming: {actual_name} → {new_name}")
                    shutil.move(str(temp_path), str(new_path))
                    
                # Build config from mappings
                for result, _, actual_name in temp_mappings:
                    # Create filename from title (sanitized) - same logic as above
                    title_slug = result['title'].replace(' ', '_').replace('"', '').replace("'", '')
                    title_slug = ''.join(c for c in title_slug if c.isalnum() or c == '_')
                    new_name = f"{result['rank']:02d}_{title_slug}.png"
                    screenshot_config = {
                        'file': new_name,
                        'original_name': result['original_name'],
                        'rank': result['rank'],
                        'rank_reason': result['rank_reason'],
                        'hero_shot': result['hero_shot'],
                        'title': result['title'],
                        'subtitle': result['subtitle'],
                        'detected_content': result['detected_content'],
                        'confidence': result['confidence']
                    }
                    
                    screenshots.append(screenshot_config)
                    total_analyzed += 1
            
            config['platforms'][platform] = {
                'theme': theme,
                'device_type': device_type,
                'screenshots': screenshots
            }
        
        # Save config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"✅ Analysis complete! Analyzed {total_analyzed} screenshots")
        logger.info(f"Configuration saved to: {self.config_file}")
        
        if not preserve_names:
            logger.info("")
            logger.info("📊 Files have been auto-ordered based on Claude's strategic ranking")
            logger.info("   Review screenshot_config.json to see ranking reasons")
        
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Review screenshot_config.json")
        logger.info("  2. Edit titles/subtitles if needed")
        logger.info("  3. Run: python screenshot_pipeline.py --generate")
        
        if not preserve_names:
            logger.info("")
            logger.info("💡 To preserve original filenames next time:")
            logger.info("   python screenshot_pipeline.py --analyze --preserve-names")
        
        logger.info("=" * 70)
    
    def generate(self, regenerate_files=None):
        """
        Generate all screenshot sizes from configuration
        
        Args:
            regenerate_files: List of specific files to regenerate (None = all)
        """
        logger.info("=" * 70)
        logger.info("SCREENSHOT GENERATOR")
        logger.info("=" * 70)
        logger.info("")
        
        # Load config
        if not self.config_file.exists():
            logger.error(f"Error: Config file not found: {self.config_file}")
            logger.error("Run analysis first: python screenshot_pipeline.py --analyze")
            sys.exit(1)
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        logger.info(f"Loaded config: {config.get('version', 'unknown')}")
        logger.info(f"Generated: {config.get('generated', 'unknown')}")
        
        if config.get('auto_ordered'):
            logger.info("Auto-ordered: Yes (screenshots ranked by Claude)")
        else:
            logger.info("Auto-ordered: No (preserved original order)")
        
        logger.info("")
        
        # Clean output directories for a fresh run (unless regenerating specific files)
        if not regenerate_files:
            platforms_to_clean = []
            for platform in config['platforms'].keys():
                if platform == 'android':
                    clean_path = self.output_dir / 'android'
                elif platform == 'ios_iphone':
                    clean_path = self.output_dir / 'ios' / 'iphone'
                elif platform == 'ios_ipad':
                    clean_path = self.output_dir / 'ios' / 'ipad'
                else:
                    continue
                platforms_to_clean.append(clean_path)
            
            for clean_path in platforms_to_clean:
                if clean_path.exists():
                    logger.info(f"🧹 Cleaning: {clean_path}")
                    shutil.rmtree(clean_path)
            
            if platforms_to_clean:
                logger.info("")
        
        total_generated = 0
        
        for platform, platform_config in config['platforms'].items():
            theme = platform_config['theme']
            device_type = platform_config['device_type']
            screenshots = platform_config['screenshots']
            
            logger.info(f"\n{platform.upper()}:")
            logger.info(f"  Theme: {theme}")
            logger.info(f"  Screenshots: {len(screenshots)}")
            logger.info("")
            
            for screenshot in screenshots:
                filename = screenshot['file']
                
                # Check if we should skip this file
                if regenerate_files:
                    match = f"{platform}/{filename}"
                    if match not in regenerate_files:
                        continue
                
                title = screenshot['title']
                subtitle = screenshot['subtitle']
                
                # Show ranking info if available
                if 'rank' in screenshot:
                    hero_badge = " 🏆" if screenshot.get('hero_shot') else ""
                    logger.info(f"Processing #{screenshot['rank']}{hero_badge}: {filename}")
                else:
                    logger.info(f"Processing: {filename}")
                
                logger.info(f"  Title: \"{title}\"")
                logger.info(f"  Subtitle: \"{subtitle}\"")
                
                if 'rank_reason' in screenshot:
                    logger.info(f"  Why: {screenshot['rank_reason']}")
                
                # Get source image path
                source_path = self.input_dir / platform / filename
                
                if not source_path.exists():
                    logger.error(f"  ❌ Source file not found: {source_path}")
                    continue
                
                # Generate all required sizes
                sizes = SIZES.get(platform, {})
                
                for device_category, size_list in sizes.items():
                    for size in size_list:
                        try:
                            # Create output directory
                            size_label = SIZE_LABELS[size]
                            
                            if platform == 'android':
                                output_path = self.output_dir / platform / 'phone' / size_label
                            elif platform == 'ios_iphone':
                                output_path = self.output_dir / 'ios' / 'iphone' / size_label
                            else:  # ios_ipad
                                output_path = self.output_dir / 'ios' / 'ipad' / size_label
                            
                            output_path.mkdir(parents=True, exist_ok=True)
                            
                            # Generate safe filename
                            base_name = Path(filename).stem
                            output_file = output_path / f"{base_name}.png"
                            
                            # Create screenshot
                            img = self.processor.create_screenshot_with_text(
                                source_path, title, subtitle, size, theme, DEFAULT_SCREENSHOT_SCALE
                            )
                            
                            # Save
                            img.save(output_file, 'PNG', quality=95, optimize=True)
                            
                            logger.info(f"    ✅ {size[0]}x{size[1]}: {output_file}")
                            total_generated += 1
                            
                        except Exception as e:
                            logger.error(f"    ❌ Failed {size[0]}x{size[1]}: {e}")
                
                logger.info("")
        
        logger.info("=" * 70)
        logger.info(f"✅ Generation complete! Created {total_generated} screenshots")
        logger.info(f"Output directory: {self.output_dir}")
        
        # Generate results.md for each platform
        self._generate_results_markdown(config)
        
        logger.info("=" * 70)
    
    def _generate_results_markdown(self, config):
        """
        Generate results.md files with analysis details for each platform
        """
        for platform, platform_config in config['platforms'].items():
            # Determine output path
            if platform == 'android':
                md_path = self.output_dir / 'android' / 'RESULTS.md'
            elif platform == 'ios_iphone':
                md_path = self.output_dir / 'ios' / 'iphone' / 'RESULTS.md'
            elif platform == 'ios_ipad':
                md_path = self.output_dir / 'ios' / 'ipad' / 'RESULTS.md'
            else:
                continue
            
            # Ensure directory exists
            md_path.parent.mkdir(parents=True, exist_ok=True)
            
            screenshots = platform_config['screenshots']
            
            lines = [
                f"# Screenshot Analysis - {platform.upper()}",
                "",
                f"Generated: {config.get('generated', 'unknown')}",
                f"Auto-ordered: {'Yes' if config.get('auto_ordered') else 'No'}",
                "",
                "## Screenshots",
                "",
                "| # | Filename | Title | Subtitle | Ranking Reason |",
                "|---|----------|-------|----------|----------------|",
            ]
            
            for ss in screenshots:
                rank = ss.get('rank', '-')
                filename = ss.get('file', 'unknown')
                title = ss.get('title', '').replace('|', '\\|')
                subtitle = ss.get('subtitle', '').replace('|', '\\|')
                reason = ss.get('rank_reason', '-').replace('|', '\\|')
                
                # Truncate reason for table readability
                if len(reason) > 80:
                    reason = reason[:77] + '...'
                
                lines.append(f"| {rank} | {filename} | {title} | {subtitle} | {reason} |")
            
            # Add detailed section with full reasoning
            lines.extend([
                "",
                "## Detailed Analysis",
                "",
            ])
            
            for ss in screenshots:
                rank = ss.get('rank', '-')
                hero = " 🏆 HERO" if ss.get('hero_shot') else ""
                filename = ss.get('file', 'unknown')
                title = ss.get('title', '')
                subtitle = ss.get('subtitle', '')
                reason = ss.get('rank_reason', '-')
                detected = ss.get('detected_content', [])
                
                lines.extend([
                    f"### #{rank}{hero}: {title}",
                    "",
                    f"**File:** `{filename}`",
                    "",
                    f"**Subtitle:** {subtitle}",
                    "",
                    f"**Why this ranking:** {reason}",
                    "",
                    f"**Detected content:** {', '.join(detected) if detected else 'N/A'}",
                    "",
                ])
            
            # Write file
            with open(md_path, 'w') as f:
                f.write('\n'.join(lines))
            
            logger.info(f"📄 Generated: {md_path}")
    
    def auto(self, preserve_names=False):
        """
        Run full pipeline: analyze + generate
        
        Args:
            preserve_names: If True, don't auto-order files
        """
        self.analyze(preserve_names=preserve_names)
        logger.info("\n")
        self.generate()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Automated Screenshot Pipeline for App Stores',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze screenshots and generate config (AUTO-ORDER by default)
  python screenshot_pipeline.py --analyze
  
  # Analyze without auto-ordering (preserve filenames)
  python screenshot_pipeline.py --analyze --preserve-names
  
  # Generate screenshots from config
  python screenshot_pipeline.py --generate
  
  # Full auto (analyze + generate with auto-ordering)
  python screenshot_pipeline.py --auto
  
  # Full auto without reordering files
  python screenshot_pipeline.py --auto --preserve-names
  
  # Regenerate specific screenshots
  python screenshot_pipeline.py --regenerate android/01_map.png ios_iphone/02_forecast.png
  
  # Use custom base directory
  python screenshot_pipeline.py --auto --base-dir /path/to/screenshots

Directory Structure:
  ScreenShots/
  ├── Input/
  │   ├── android/          # Android screenshots
  │   ├── ios_iphone/       # iPhone screenshots
  │   └── ios_ipad/         # iPad screenshots
  ├── Output/               # Generated screenshots
  └── screenshot_config.json

Auto-Ordering:
  By default, Claude Vision ranks screenshots for optimal App Store impact:
  - #1 (Hero): Most eye-catching, shows unique value
  - #2-3 (Value): Core functionality and benefits
  - #4+ (Proof): Additional features and credibility
  
  Files are renamed to 01_, 02_, 03_ based on strategic ranking.
  Use --preserve-names to skip auto-ordering.
        """
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze screenshots and generate config file'
    )
    
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate screenshots from existing config'
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Run full pipeline (analyze + generate)'
    )
    
    parser.add_argument(
        '--regenerate',
        nargs='+',
        metavar='FILE',
        help='Regenerate specific screenshots (e.g., android/01_map.png)'
    )
    
    parser.add_argument(
        '--preserve-names',
        action='store_true',
        help='Preserve original filenames (skip auto-ordering)'
    )
    
    parser.add_argument(
        '--base-dir',
        default='ScreenShots',
        help='Base directory for screenshots (default: ScreenShots)'
    )
    
    args = parser.parse_args()
    
    # Check if any action was specified
    if not (args.analyze or args.generate or args.auto or args.regenerate):
        parser.print_help()
        sys.exit(1)
    
    # Create pipeline
    pipeline = ScreenshotPipeline(base_dir=args.base_dir)
    
    # Execute requested action
    try:
        if args.auto:
            pipeline.auto(preserve_names=args.preserve_names)
        elif args.regenerate:
            pipeline.generate(regenerate_files=args.regenerate)
        elif args.analyze:
            pipeline.analyze(preserve_names=args.preserve_names)
        elif args.generate:
            pipeline.generate()
    
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
