# ASCII Art Generator

A Python tool to convert images to ASCII art with support for animation and edge detection.

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
- `-e, --edges`: Enable edge detection with line characters (|, -, \, /, +, _)

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

Enable edge detection for better outlines:
```bash
python ascii_art.py image.jpg -e
```

Combine multiple options:
```bash
python ascii_art.py image.jpg -w 120 -e -a
```

## How It Works

1. The image is resized while maintaining the aspect ratio
2. The image is converted to grayscale
3. If edge detection is enabled, Canny edge detection is applied to identify edges
4. Edges are represented with appropriate line characters (|, -, \, /, +, _) based on their direction
5. Non-edge pixels are mapped to ASCII characters based on their intensity
6. The resulting ASCII characters are arranged to form the final ASCII art

## License

This project is open source and available under the MIT License.
