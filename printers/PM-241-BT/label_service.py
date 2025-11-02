#!/usr/bin/env python3
"""
Label Printer Service API
FastAPI daemon for remote label printing with configurable sizes
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add label_printer to path
sys.path.insert(0, str(Path(__file__).parent))

from label_printer.formatter import LabelFormatter
from label_printer.printer import PhomemoPrinter
import label_printer.config as config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Phomemo Label Printer Service",
    description="REST API for printing labels on Phomemo PM-241-BT",
    version="1.0.0"
)


# Pydantic models
class LabelSize(BaseModel):
    """Label dimensions in millimeters"""
    width_mm: float = Field(..., gt=0, description="Label width in millimeters")
    height_mm: float = Field(..., gt=0, description="Label height in millimeters")


class PrintOptions(BaseModel):
    """Optional print parameters"""
    border: bool = Field(False, description="Draw border around label")
    font_size: Optional[int] = Field(None, description="Font size in points (auto if not specified)")
    dpi: int = Field(300, description="Image DPI (dots per inch)")


class PrintRequest(BaseModel):
    """Request to print a label"""
    text: str = Field(..., min_length=1, max_length=100, description="Text to print on label")
    label_size: LabelSize = Field(..., description="Label dimensions")
    options: PrintOptions = Field(default_factory=PrintOptions, description="Print options")


class PrintResponse(BaseModel):
    """Response from print request"""
    success: bool
    message: str
    job_id: Optional[str] = None
    image_path: Optional[str] = None


class CapabilitiesResponse(BaseModel):
    """Printer capabilities"""
    printer_name: str
    available: bool
    supported_dpi: list[int]
    default_label_sizes: dict[str, LabelSize]
    max_label_size_mm: LabelSize
    min_label_size_mm: LabelSize


def mm_to_pixels(mm: float, dpi: int) -> int:
    """Convert millimeters to pixels at given DPI"""
    inches = mm / 25.4
    return int(inches * dpi)


def pixels_to_mm(pixels: int, dpi: int) -> float:
    """Convert pixels to millimeters at given DPI"""
    inches = pixels / dpi
    return inches * 25.4


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "label-printer-service"
    }


@app.get("/api/v1/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities():
    """Get printer capabilities and supported label sizes"""
    printer = PhomemoPrinter()
    is_available = printer.check_printer_status()

    # Calculate current default size in mm
    default_width_mm = pixels_to_mm(config.LABEL_WIDTH_PIXELS, config.DPI)
    default_height_mm = pixels_to_mm(config.LABEL_HEIGHT_PIXELS, config.DPI)

    return CapabilitiesResponse(
        printer_name=config.PRINTER_NAME,
        available=is_available,
        supported_dpi=[203, 300],
        default_label_sizes={
            "rectangular": LabelSize(
                width_mm=round(default_width_mm, 1),
                height_mm=round(default_height_mm, 1)
            ),
            "square_small": LabelSize(width_mm=50, height_mm=50),
            "square_large": LabelSize(width_mm=60, height_mm=60),
        },
        max_label_size_mm=LabelSize(width_mm=100, height_mm=150),
        min_label_size_mm=LabelSize(width_mm=20, height_mm=20)
    )


@app.post("/api/v1/print", response_model=PrintResponse)
async def print_label(request: PrintRequest):
    """Print a label with specified text and dimensions"""
    logger.info(f"🎯 Print request: '{request.text}' @ {request.label_size.width_mm}x{request.label_size.height_mm}mm")

    try:
        # Check printer status
        printer = PhomemoPrinter()
        if not printer.check_printer_status():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Printer {config.PRINTER_NAME} is not available"
            )

        # Convert mm to pixels
        width_px = mm_to_pixels(request.label_size.width_mm, request.options.dpi)
        height_px = mm_to_pixels(request.label_size.height_mm, request.options.dpi)

        logger.info(f"📐 Label size: {width_px}x{height_px}px @ {request.options.dpi} DPI")

        # Create label image
        formatter = LabelFormatter()
        img = formatter.create_label(
            text=request.text,
            font_size=request.options.font_size,
            border=request.options.border,
            size=(width_px, height_px)
        )

        # Save to temp file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"label_{timestamp}.png"
        image_path = config.TEMP_IMAGE_DIR / filename
        formatter.save_label(img, image_path)

        # Print
        success = printer.print_image(image_path)

        if success:
            logger.info(f"✅ Label printed successfully: {filename}")
            return PrintResponse(
                success=True,
                message="Label printed successfully",
                job_id=timestamp,
                image_path=str(image_path)
            )
        else:
            logger.error(f"❌ Print failed for: {filename}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Print job failed"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing print request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


def main():
    """Run the service"""
    import argparse

    parser = argparse.ArgumentParser(description="Label Printer Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    logger.info(f"🚀 Starting Label Printer Service on {args.host}:{args.port}")
    logger.info(f"📍 Printer: {config.PRINTER_NAME}")

    uvicorn.run(
        "label_service:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=config.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
