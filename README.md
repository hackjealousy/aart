# ASCII Art Generator

A Python tool to convert images to ASCII art with support for animation and dithering.

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:

```bash
python ascii_art.py path/to/image.jpg
```

### Options

- `-w, --width`: Set the width of the ASCII art (default: 100)
- `-c, --chars`: Specify the ASCII characters to use (from light to dark, default: " .:-=+*#%@")
- `-o, --output`: Save the ASCII art to a file instead of printing to console
- `-r, --reverse`: Reverse the ASCII character set (dark to light)
- `-a, --animate`: Animate GIFs (if the input is an animated GIF)
- `-d, --delay`: Set the delay between frames for animation (default: 0.1 seconds)
- `--dither`: Choose a dithering method: "none", "ordered", "floyd-steinberg", or "atkinson" (default: "none")
- `-p, --pattern`: Use pattern-based character selection for improved detail

### Examples

Convert an image with default settings:
```bash
python ascii_art.py image.jpg
```

Convert an image with custom width:
```bash
python ascii_art.py image.jpg -w 150
```

Convert an image with custom character set:
```bash
python ascii_art.py image.jpg -c "#@%*+=-:. "
```

Save the output to a file:
```bash
python ascii_art.py image.jpg -o output.txt
```

Reverse the character set (dark to light):
```bash
python ascii_art.py image.jpg -r
```

Animate a GIF:
```bash
python ascii_art.py animation.gif -a
```

Apply Floyd-Steinberg dithering:
```bash
python ascii_art.py image.jpg --dither floyd-steinberg
```

Use pattern-based character selection:
```bash
python ascii_art.py image.jpg -p
```

Combine multiple options:
```bash
python ascii_art.py image.jpg -w 120 --dither atkinson -p
```

## Dithering Methods

- **None**: No dithering applied
- **Ordered**: Uses a Bayer matrix for ordered dithering, creating a regular pattern
- **Floyd-Steinberg**: Error diffusion dithering that distributes quantization error to neighboring pixels
- **Atkinson**: Similar to Floyd-Steinberg but distributes less error, creating cleaner results with less noise

## How It Works

1. The image is resized while maintaining the aspect ratio
2. The image is converted to grayscale
3. Optional dithering is applied to improve visual quality
4. Each pixel's intensity is mapped to an ASCII character
5. The resulting ASCII characters are arranged to form the final ASCII art

## License

This project is open source and available under the MIT License.
