#!/usr/bin/env python3
"""
ASCII Art Generator
A tool to convert images to ASCII art with support for dithering and animation.
"""

import argparse
import os
import sys
import time
import numpy as np
from PIL import Image


def resize_image(image, new_width=100):
    """Resize the image while maintaining aspect ratio."""
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  # Adjust for character height/width ratio
    return image.resize((new_width, new_height))


def convert_to_grayscale(image):
    """Convert image to grayscale."""
    return image.convert("L")


def apply_dithering(image, method='floyd-steinberg'):
    """Apply dithering to the grayscale image."""
    # Convert PIL Image to numpy array for easier manipulation
    img_array = np.array(image, dtype=np.float64)
    height, width = img_array.shape
    
    if method == 'none':
        # No dithering, just return the original image
        return image
    
    elif method == 'ordered':
        # 4x4 Bayer matrix for ordered dithering
        bayer_matrix = np.array([
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]) / 16.0 * 255
        
        for y in range(height):
            for x in range(width):
                # Add the dither pattern value
                threshold = bayer_matrix[y % 4, x % 4]
                img_array[y, x] = img_array[y, x] + threshold - 128
                # Clamp values
                img_array[y, x] = max(0, min(255, img_array[y, x]))
    
    elif method == 'floyd-steinberg':
        # Floyd-Steinberg dithering
        for y in range(height):
            for x in range(width):
                old_pixel = img_array[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                img_array[y, x] = new_pixel
                
                error = old_pixel - new_pixel
                
                # Distribute error to neighboring pixels
                if x + 1 < width:
                    img_array[y, x + 1] += error * 7 / 16
                if y + 1 < height:
                    if x - 1 >= 0:
                        img_array[y + 1, x - 1] += error * 3 / 16
                    img_array[y + 1, x] += error * 5 / 16
                    if x + 1 < width:
                        img_array[y + 1, x + 1] += error * 1 / 16
    
    elif method == 'atkinson':
        # Atkinson dithering
        for y in range(height):
            for x in range(width):
                old_pixel = img_array[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                img_array[y, x] = new_pixel
                
                error = (old_pixel - new_pixel) / 8  # Distribute 1/8 of the error to each of 6 neighboring pixels
                
                # Distribute error to neighboring pixels
                if x + 1 < width:
                    img_array[y, x + 1] += error
                if x + 2 < width:
                    img_array[y, x + 2] += error
                if y + 1 < height:
                    if x - 1 >= 0:
                        img_array[y + 1, x - 1] += error
                    img_array[y + 1, x] += error
                    if x + 1 < width:
                        img_array[y + 1, x + 1] += error
                if y + 2 < height:
                    img_array[y + 2, x] += error
    
    # Create a new PIL Image from the dithered array
    return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))


def pixels_to_ascii(image, ascii_chars):
    """Convert pixels to ASCII characters based on intensity."""
    pixels = list(image.getdata())
    ascii_str = ""
    for pixel in pixels:
        # Map pixel intensity to ASCII character
        char_index = min(int(pixel * len(ascii_chars) / 256), len(ascii_chars) - 1)
        ascii_str += ascii_chars[char_index]
    return ascii_str


def pixels_to_ascii_pattern(image, ascii_chars):
    """Convert pixels to ASCII characters based on local patterns."""
    width, height = image.size
    img_array = np.array(image)
    ascii_str = ""
    
    # Process 2x2 blocks of pixels to determine appropriate character
    for y in range(0, height, 2):
        for x in range(0, width, 2):
            # Extract 2x2 block (or smaller if at the edge)
            block_height = min(2, height - y)
            block_width = min(2, width - x)
            block = img_array[y:y+block_height, x:x+block_width]
            
            # Calculate average brightness
            avg_brightness = np.mean(block)
            
            # Map to character based on average brightness
            char_index = min(int(avg_brightness * len(ascii_chars) / 256), len(ascii_chars) - 1)
            ascii_str += ascii_chars[char_index]
        
        # Add a newline after each row of blocks
        ascii_str += "\n"
    
    return ascii_str


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def image_to_ascii(image_path, width=100, ascii_chars=None, output_file=None, animate=False, delay=0.1, dither='none', pattern_mode=False):
    """Convert an image to ASCII art."""
    if ascii_chars is None:
        # From dark to light - a carefully selected set with good contrast
        ascii_chars = " .:-=+*#%@"  # Reversed order (light to dark)
    
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return None
    
    # Check if the image is animated
    is_animated = hasattr(image, "is_animated") and image.is_animated
    
    if is_animated and animate:
        # Process animated GIF
        frames = []
        try:
            frame_count = getattr(image, "n_frames", 1)
            for frame_idx in range(frame_count):
                image.seek(frame_idx)
                frame_copy = image.copy()
                frame_copy = resize_image(frame_copy, width)
                frame_copy = convert_to_grayscale(frame_copy)
                
                # Apply dithering if requested
                if dither != 'none':
                    frame_copy = apply_dithering(frame_copy, dither)
                
                # Convert to ASCII
                if pattern_mode:
                    ascii_str_with_breaks = pixels_to_ascii_pattern(frame_copy, ascii_chars)
                else:
                    ascii_str = pixels_to_ascii(frame_copy, ascii_chars)
                    img_width = frame_copy.width
                    ascii_str_with_breaks = "\n".join(
                        ascii_str[i:i+img_width] for i in range(0, len(ascii_str), img_width)
                    )
                
                frames.append(ascii_str_with_breaks)
            
            # Display animation
            try:
                while True:  # Loop forever until Ctrl+C
                    for frame in frames:
                        clear_screen()
                        print(frame)
                        time.sleep(delay)
            except KeyboardInterrupt:
                print("\nAnimation stopped.")
            return None
        except Exception as e:
            print(f"Error processing animated GIF: {e}")
            # Fall back to processing as a static image
    
    # Process the image as a static image
    image = resize_image(image, width)
    image = convert_to_grayscale(image)
    
    # Apply dithering if requested
    if dither != 'none':
        image = apply_dithering(image, dither)
    
    # Convert to ASCII
    if pattern_mode:
        ascii_str_with_breaks = pixels_to_ascii_pattern(image, ascii_chars)
    else:
        ascii_str = pixels_to_ascii(image, ascii_chars)
        img_width = image.width
        ascii_str_with_breaks = "\n".join(
            ascii_str[i:i+img_width] for i in range(0, len(ascii_str), img_width)
        )
    
    # Output
    if output_file:
        try:
            with open(output_file, "w") as f:
                f.write(ascii_str_with_breaks)
            print(f"ASCII art saved to {output_file}")
        except Exception as e:
            print(f"Error saving to file: {e}")
    
    return ascii_str_with_breaks


def main():
    parser = argparse.ArgumentParser(description="Convert images to ASCII art.")
    parser.add_argument("image", help="Path to the image file")
    parser.add_argument("-w", "--width", type=int, default=100, help="Width of the ASCII art (default: 100)")
    parser.add_argument("-c", "--chars", default=" .:-=+*#%@", help="ASCII characters to use (from light to dark)")
    parser.add_argument("-o", "--output", help="Output file (if not specified, prints to console)")
    parser.add_argument("-r", "--reverse", action="store_true", help="Reverse the ASCII character set (dark to light)")
    parser.add_argument("-a", "--animate", action="store_true", help="Animate GIFs (if the input is an animated GIF)")
    parser.add_argument("-d", "--delay", type=float, default=0.1, help="Delay between frames for animation (default: 0.1 seconds)")
    parser.add_argument("--dither", choices=["none", "ordered", "floyd-steinberg", "atkinson"], default="none",
                        help="Dithering method to use (default: none)")
    parser.add_argument("-p", "--pattern", action="store_true", help="Use pattern-based character selection")
    
    args = parser.parse_args()
    
    # Process character set
    chars = args.chars
    if args.reverse:
        chars = chars[::-1]
    
    # Convert image to ASCII
    ascii_art = image_to_ascii(
        args.image, args.width, chars, args.output, 
        args.animate, args.delay, args.dither, args.pattern
    )
    
    # Print to console if no output file specified and not animated
    if not args.output and ascii_art and not args.animate:
        print(ascii_art)


if __name__ == "__main__":
    main()
