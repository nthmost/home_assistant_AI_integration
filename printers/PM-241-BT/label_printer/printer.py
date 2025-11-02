"""
Print driver wrapper for Phomemo PM-241-BT via CUPS
"""
import logging
import subprocess
from pathlib import Path
from . import config

logger = logging.getLogger(__name__)


class PhomemoPrinter:
    """Interface to Phomemo PM-241-BT thermal label printer"""
    
    def __init__(self, printer_name=config.PRINTER_NAME):
        self.printer_name = printer_name
        
    def check_printer_status(self):
        """Check if printer is available and ready"""
        try:
            result = subprocess.run(
                ["lpstat", "-p", self.printer_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                status = result.stdout.strip()
                if "idle" in status.lower():
                    logger.info(f"🖨️  Printer {self.printer_name} is ready")
                    return True
                else:
                    logger.warning(f"⚠️  Printer status: {status}")
                    return False
            else:
                logger.error(f"❌ Printer {self.printer_name} not found")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout checking printer status")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking printer: {e}")
            return False
    
    def print_image(self, image_path, options=None):
        """
        Print an image file to the Phomemo printer
        
        Args:
            image_path: Path to image file (PNG)
            options: Dict of additional print options
            
        Returns:
            True if successful, False otherwise
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            logger.error(f"❌ Image file not found: {image_path}")
            return False
        
        logger.info(f"🖨️  Printing {image_path} to {self.printer_name}")
        
        # Command matching the working script exactly
        cmd = [
            "lp",
            "-d", self.printer_name,
            "-o", "media=Custom.2x2in",  # Critical! This makes it work
            str(image_path)
        ]
        
        logger.debug(f"Print command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Print job submitted successfully")
                if result.stdout:
                    logger.debug(f"   {result.stdout.strip()}")
                return True
            else:
                logger.error(f"❌ Print failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Print command timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error printing: {e}")
            return False
