#!/usr/bin/env python3
"""
Claude Vision API integration for screenshot analysis
"""

import base64
import json
import logging
from pathlib import Path
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class VisionAnalyzer:
    """Analyzes screenshots using Claude Vision API"""
    
    def __init__(self, api_key=None):
        """
        Initialize the vision analyzer
        
        Args:
            api_key: Anthropic API key (if None, uses ANTHROPIC_API_KEY env var)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_and_rank_screenshots(self, image_paths, platform, device_type):
        """
        Analyze multiple screenshots and rank them for optimal App Store ordering
        
        Args:
            image_paths: List of Path objects to screenshot files
            platform: 'android', 'ios_iphone', or 'ios_ipad'
            device_type: 'phone', 'iphone', or 'ipad'
        
        Returns:
            List of dictionaries sorted by rank, each containing:
            {
                'original_name': str,
                'rank': int,
                'rank_reason': str,
                'hero_shot': bool,
                'title': str,
                'subtitle': str,
                'detected_content': list,
                'confidence': float
            }
        """
        logger.info(f"Analyzing and ranking {len(image_paths)} screenshots...")
        
        # Get platform context
        platform_context = self._get_platform_context(platform, device_type)
        
        # Prepare all images
        images_data = []
        for idx, img_path in enumerate(image_paths):
            with open(img_path, 'rb') as f:
                image_data = base64.standard_b64encode(f.read()).decode('utf-8')
            
            ext = img_path.suffix.lower()
            media_type_map = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
            }
            media_type = media_type_map.get(ext, 'image/png')
            
            images_data.append({
                'name': img_path.name,
                'data': image_data,
                'media_type': media_type
            })
        
        # Create ranking prompt
        prompt = f"""You are an App Store optimization expert analyzing screenshots for a fishing app.

Platform: {platform_context['name']}
Theme: {platform_context['theme']}
Context: This is Get Hooked, a fishing intelligence app with features like heat maps, fishing forecasts, angler DNA profiles, weather overlays, and satellite imagery.

I'm providing you with {len(images_data)} screenshots. Your task:

1. **RANK them in optimal order** for App Store display (1 = hero shot, shown first)
2. **Generate compelling titles + subtitles** for each (following character limits)
3. **Explain your ranking** - why this order tells the best story

Ranking Criteria:
- Screenshot #1 (HERO): Most eye-catching, shows unique value, hooks users immediately
- Screenshot #2-3 (VALUE): Demonstrate core functionality and benefits
- Screenshot #4+ (PROOF): Additional features, credibility, depth

App Store Psychology:
- Users often only view first 2-3 screenshots
- First screenshot should show what makes this app DIFFERENT
- Order should tell a story: Hook → Value → Proof
- Visual impact matters - colorful, data-rich screenshots work better early

Title Requirements:
- TITLE: Max 30 chars, benefit-focused, punchy
- SUBTITLE: Max 50 chars, adds context/detail

Return ONLY a JSON array sorted by rank (1, 2, 3...):
[
  {{
    "original_name": "filename.png",
    "rank": 1,
    "rank_reason": "Why this screenshot is the hero shot",
    "hero_shot": true,
    "title": "Your Title Here",
    "subtitle": "Your subtitle here",
    "detected_content": ["feature1", "feature2"],
    "confidence": 0.95
  }},
  ...
]"""

        # Build message content with all images
        message_content = []
        for img_data in images_data:
            message_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img_data['media_type'],
                    "data": img_data['data'],
                }
            })
            # Add caption for reference
            message_content.append({
                "type": "text",
                "text": f"Screenshot filename: {img_data['name']}"
            })
        
        # Add the ranking prompt at the end
        message_content.append({
            "type": "text",
            "text": prompt
        })
        
        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            )
            
            # Parse response
            response_text = response.content[0].text
            
            # Clean up response (remove markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            results = json.loads(response_text)
            
            # Log the ranking
            logger.info("\n📊 RANKING RESULTS:")
            for result in results:
                hero_badge = " 🏆 HERO" if result.get('hero_shot') else ""
                logger.info(f"  #{result['rank']}{hero_badge}: {result['original_name']}")
                logger.info(f"    Reason: {result['rank_reason']}")
                logger.info(f"    Title: \"{result['title']}\"")
                logger.info(f"    Subtitle: \"{result['subtitle']}\"")
            
            return results
            
        except Exception as e:
            logger.error(f"Error ranking screenshots: {e}")
            # Return fallback - alphabetical order with generic content
            fallback = []
            for idx, img_path in enumerate(sorted(image_paths), 1):
                fallback.append({
                    'original_name': img_path.name,
                    'rank': idx,
                    'rank_reason': 'Fallback alphabetical ordering (API error)',
                    'hero_shot': (idx == 1),
                    'title': 'Get Hooked!',
                    'subtitle': 'Your intelligent fishing companion',
                    'detected_content': ['unknown'],
                    'confidence': 0.0
                })
            return fallback
    
    def analyze_screenshot(self, image_path, platform, device_type):
        """
        Analyze a single screenshot and generate title/subtitle
        (Legacy method - now prefer analyze_and_rank_screenshots for better results)
        
        Args:
            image_path: Path to screenshot file
            platform: 'android', 'ios_iphone', or 'ios_ipad'
            device_type: 'phone', 'iphone', or 'ipad'
        
        Returns:
            Dictionary with analysis results:
            {
                'title': str,
                'subtitle': str,
                'detected_content': list,
                'confidence': float
            }
        """
        logger.info(f"Analyzing: {image_path.name}")
        
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')
        
        # Determine media type
        ext = image_path.suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
        }
        media_type = media_type_map.get(ext, 'image/png')
        
        # Build platform context
        platform_context = self._get_platform_context(platform, device_type)
        
        # Create prompt
        prompt = f"""Analyze this fishing app screenshot and generate compelling App Store marketing copy.

Platform: {platform_context['name']}
Theme: {platform_context['theme']}
Messaging style: {platform_context['style']}

Your task:
1. Identify what feature/screen is shown (map, forecast, profile, layers, etc.)
2. Generate TWO text elements:
   - TITLE: Punchy, benefit-focused headline (max 30 chars)
   - SUBTITLE: Supporting detail that adds context (max 50 chars)

Both should be centered and work together to sell the feature.

Rules:
- Focus on USER BENEFITS, not feature names
- Use active, energetic language
- Make it feel exclusive/intelligent
- TITLE should make them want to know more
- SUBTITLE should deliver the "how" or "what"
- Keep it short and impactful

Example pairs:
- TITLE: "Find Fish in Real-Time"
  SUBTITLE: "Heat maps reveal hotspots instantly"
  
- TITLE: "Your Personal Fishing Coach"
  SUBTITLE: "AI learns your patterns and preferences"
  
- TITLE: "Never Miss Perfect Conditions"
  SUBTITLE: "Weather overlays show rain, wind, pressure"

Return ONLY a JSON object:
{{
  "title": "Your Title Here",
  "subtitle": "Your subtitle here",
  "detected_content": ["feature1", "feature2"],
  "confidence": 0.95
}}"""
        
        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            # Parse response
            response_text = response.content[0].text
            
            # Clean up response (remove markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            logger.info(f"  Title: \"{result['title']}\"")
            logger.info(f"  Subtitle: \"{result['subtitle']}\"")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {image_path.name}: {e}")
            # Return fallback
            return {
                'title': 'Get Hooked!',
                'subtitle': 'Your intelligent fishing companion',
                'detected_content': ['unknown'],
                'confidence': 0.0
            }
    
    def _get_platform_context(self, platform, device_type):
        """Get platform-specific context for analysis"""
        contexts = {
            'android': {
                'name': 'Android (Google Play)',
                'theme': 'Gradient green - emphasizes precision, data, analytics',
                'style': 'Technical, data-driven, powerful'
            },
            'ios_iphone': {
                'name': 'iOS iPhone (App Store)',
                'theme': 'Gradient blue - emphasizes simplicity, intelligence',
                'style': 'Clean, smart, intuitive, on-the-go'
            },
            'ios_ipad': {
                'name': 'iOS iPad (App Store)',
                'theme': 'Gradient blue - emphasizes workspace, productivity',
                'style': 'Professional, comprehensive, detailed analysis'
            }
        }
        return contexts.get(platform, contexts['android'])
