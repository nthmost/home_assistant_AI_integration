"""
Natural language interface for label printing using Claude API
"""
import logging
from anthropic import Anthropic
import json
import re
from . import config

logger = logging.getLogger(__name__)


class LabelCommandParser:
    """Parse natural language commands for label printing"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        
        self.client = Anthropic(api_key=self.api_key)
        
    def parse_command(self, command):
        """
        Parse a natural language command into label parameters
        
        Args:
            command: Natural language string like "print a label that says JUNTAWA"
            
        Returns:
            dict with keys: text, font_size (optional), border (bool)
        """
        logger.info(f"💬 Parsing command: '{command}'")
        
        system_prompt = """You are a label printer command parser. 
Extract the text to print on the label and any formatting options from natural language commands.

Return ONLY a JSON object (no markdown, no code blocks) with these fields:
- text: The text to print (required)
- font_size: Optional font size in points (omit for auto)
- border: true/false for border (default false)

Examples:
"print a label that says JUNTAWA" -> {"text": "JUNTAWA"}
"make a label for Tea - Jasmine Green" -> {"text": "Tea - Jasmine Green"}
"print OFFICE with a border" -> {"text": "OFFICE", "border": true}
"print Kitchen in small font" -> {"text": "Kitchen", "font_size": 24}

Return ONLY the JSON object, no other text."""

        try:
            message = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=200,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": command}
                ]
            )
            
            response_text = message.content[0].text.strip()
            logger.debug(f"📝 Claude response: {response_text}")
            
            # Strip markdown code blocks if present
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON response
            params = json.loads(response_text)
            
            # Validate required fields
            if "text" not in params:
                raise ValueError("No text found in command")
            
            logger.info(f"✅ Parsed: text='{params['text']}', font_size={params.get('font_size', 'auto')}, border={params.get('border', False)}")
            
            return params
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Claude response as JSON: {e}")
            logger.error(f"   Response was: {response_text}")
            raise
        except Exception as e:
            logger.error(f"❌ Error calling Claude API: {e}")
            raise
