# Phomemo PM-241-BT Label Printer Setup

## Device Information
- **Model**: Phomemo PM-241-BT
- **Connection**: Bluetooth/USB
- **Resolution**: 203 DPI (native)
- **CUPS Printer Name**: PM-241-BT

## Label Specifications
### Rectangular Labels (Current Working Setup)
- **Physical Size**: Approximately 1.5" wide × 2" tall
- **Label Type**: Pre-cut labels with gaps
- **Printable Area**: ~350px wide × 380px tall at 300 DPI

## Working Parameters (Rectangular Labels)

### Image Dimensions
```python
LABEL_WIDTH_PIXELS = 350   # Width at 300 DPI
LABEL_HEIGHT_PIXELS = 380  # Height at 300 DPI
DPI = 300
DEFAULT_MARGINS_PIXELS = 10
```

### Positioning
- **Text Y Position**: 70 pixels from top (keeps text visible, avoids bottom clipping)
- **Margins**: 10 pixels on sides
- **Text Alignment**: Horizontally centered, fixed vertical position

### Print Command
```bash
lp -d PM-241-BT -o media=Custom.2x2in <image_file>
```

### Image Format
- **Color Mode**: RGB (NOT 1-bit/monochrome - causes blank labels!)
- **Background**: White
- **Text Color**: Black
- **Font**: DejaVuSans-Bold (system font)

## Key Learnings

### What Works
✅ RGB color mode for images  
✅ 300 DPI images  
✅ Fixed text position (y=70) instead of centering  
✅ Media option: `Custom.2x2in`  
✅ Portrait orientation (taller than wide)  
✅ Canvas: 350×380 pixels  

### What Doesn't Work
❌ 1-bit (monochrome) images → blank labels  
❌ Centering text vertically → text gets cut off at bottom  
❌ Square 600x600 images → text positioned wrong  
❌ Native 203 DPI dimensions → printer crops incorrectly  
❌ Images without media size specified → unpredictable results  
❌ Canvas smaller than text → clipping on sides  

## Installation

### Prerequisites
```bash
python3 -m venv label_venv
source label_venv/bin/activate
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

## Usage

### Basic Command
```bash
./print_label "print a label that says JUNTAWA"
```

### With Options
```bash
./print_label "print a label for Kitchen"
./print_label "print OFFICE" --no-print  # Generate only, don't print
./print_label "test" --debug  # Enable debug logging
```

## Natural Language Support
The system uses Claude API to parse natural language commands:
- "print a label that says X"
- "make a label for X"  
- "print X with a border"

## File Structure
```
PM-241-BT/
├── label_printer/          # Main module
│   ├── __init__.py
│   ├── config.py          # Printer specs & settings
│   ├── formatter.py       # Image generation (y=70 positioning)
│   ├── printer.py         # CUPS interface
│   └── nl_interface.py    # Claude API parser
├── print_label            # CLI tool
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Blank Labels
- Check image is RGB mode, not 1-bit
- Verify text is being drawn (check logs with --debug)
- Ensure media option is set correctly

### Text Cut Off
- **Bottom**: Text positioned too low (should be at y=70)
- **Sides**: Canvas too narrow (increase LABEL_WIDTH_PIXELS)
- **Top**: Text positioned too high (increase y position)

### Printer Not Found
```bash
lpstat -p PM-241-BT  # Check printer status
lpstat -p -d          # List all printers
```

## Development History
- Started with 600×600 square images → text cut off
- Tried 288×432 (native 203 DPI) → wrong scaling
- Tried 300×400 → text cut off at bottom
- Tried 280×380 → text clipped on sides  
- **Final: 350×380 with y=70** → Working!

## Next Steps
- Fine-tune horizontal centering
- Test with different label shapes (square, larger rectangles)
- Add QR code support
- Implement voice input (Phase 2)

## Last Updated
October 28, 2025 - Initial checkpoint with rectangular label support
