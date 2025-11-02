"""
Label formatter - no font increase, just auto-size
"""
import logging
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from . import config

logger = logging.getLogger(__name__)


class LabelFormatter:
    """Generate properly sized label images for Phomemo printer"""
    
    def __init__(self):
        self.margin = config.DEFAULT_MARGINS_PIXELS
        
    def _find_font_size(self, draw, text, max_width, max_height, start_size=60):
        """Binary search to find the largest font size that fits"""
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        min_size = 8
        max_size = start_size
        best_font = None
        
        while min_size <= max_size:
            font_size = (min_size + max_size) // 2
            try:
                font = ImageFont.truetype(font_path, font_size)
            except OSError:
                font = ImageFont.load_default()
                return font
                
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if text_width <= max_width and text_height <= max_height:
                best_font = font
                min_size = font_size + 1
            else:
                max_size = font_size - 1
                
        if best_font is None:
            best_font = ImageFont.load_default()
            
        return best_font
    
    def create_label(self, text, font_size=None, border=False, size=None):
        """Create a label image"""
        logger.info(f"🏷️  Creating label for: '{text}'")
        
        if size is None:
            size = (config.LABEL_WIDTH_PIXELS, config.LABEL_HEIGHT_PIXELS)
        
        # Create RGB image
        img = Image.new('RGB', size, 'white')
        draw = ImageDraw.Draw(img)
        
        side_margin = self.margin
        available_width = size[0] - (2 * side_margin)
        available_height = size[1] - (2 * side_margin)
        
        logger.info(f"📐 Label size: {size[0]}x{size[1]}px")
        
        # Find best font size that fits (no increase)
        if font_size:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except OSError:
                font = ImageFont.load_default()
        else:
            font = self._find_font_size(draw, text, available_width, available_height)
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        logger.info(f"✅ Text size: {text_width}x{text_height}px")
        
        # Draw border if requested
        if border:
            draw.rectangle([side_margin, self.margin, 
                          size[0] - side_margin - 1, size[1] - self.margin - 1], 
                          outline='black', width=1)
        
        # Center horizontally, position at y=70
        text_x = side_margin + (available_width - text_width) // 2
        text_y = 70
        
        logger.info(f"📍 Text position: ({text_x}, {text_y})")
        
        # Draw text
        draw.text((text_x, text_y), text, fill='black', font=font)
        
        logger.info(f"✨ Label created: {size[0]}x{size[1]}px")
        return img
    
    def save_label(self, img, filename=None):
        """Save label image to file"""
        if filename is None:
            filename = config.TEMP_IMAGE_DIR / "label.png"
        else:
            filename = Path(filename)
        
        img.save(filename, format='PNG')
        logger.info(f"💾 Saved label to: {filename}")
        return filename
