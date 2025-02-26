#!/usr/bin/env python3
"""
ASCII Art Generator
A tool to convert images to ASCII art with support for animation and edge detection.
"""

import argparse
import os
import sys
import time
import numpy as np
from PIL import Image
from skimage import feature


def resize_image(image, new_width=100):
    """Resize the image while maintaining aspect ratio."""
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  # Adjust for character height/width ratio
    return image.resize((new_width, new_height))


def convert_to_grayscale(image):
    """Convert image to grayscale."""
    return image.convert("L")


def detect_edges(image, sigma=1.0, low_threshold=0.1, high_threshold=0.2):
    """Detect edges in the image using Canny edge detection."""
    # Convert PIL image to numpy array
    img_array = np.array(image)
    
    # Apply Canny edge detection
    edges = feature.canny(
        img_array,
        sigma=sigma,
        low_threshold=low_threshold,
        high_threshold=high_threshold
    )
    
    return edges


def determine_edge_direction(edges, x, y):
    """Determine the direction of an edge at a specific point."""
    # Check if the point is actually an edge
    if not edges[y, x]:
        return None
    
    height, width = edges.shape
    
    # Check surrounding pixels to determine edge direction
    # We'll check in 8 directions (N, NE, E, SE, S, SW, W, NW)
    directions = []
    
    # North
    if y > 0 and edges[y-1, x]:
        directions.append("N")
    # Northeast
    if y > 0 and x < width-1 and edges[y-1, x+1]:
        directions.append("NE")
    # East
    if x < width-1 and edges[y, x+1]:
        directions.append("E")
    # Southeast
    if y < height-1 and x < width-1 and edges[y+1, x+1]:
        directions.append("SE")
    # South
    if y < height-1 and edges[y+1, x]:
        directions.append("S")
    # Southwest
    if y < height-1 and x > 0 and edges[y+1, x-1]:
        directions.append("SW")
    # West
    if x > 0 and edges[y, x]:
        directions.append("W")
    # Northwest
    if y > 0 and x > 0 and edges[y-1, x-1]:
        directions.append("NW")
    
    # Determine primary direction
    if "N" in directions and "S" in directions:
        return "|"  # Vertical line
    elif "E" in directions and "W" in directions:
        return "-"  # Horizontal line
    elif ("NE" in directions and "SW" in directions) or ("NW" in directions and "SE" in directions):
        if "NE" in directions or "SW" in directions:
            return "/"  # Diagonal (/)
        else:
            return "\\"  # Diagonal (\)
    elif "N" in directions or "S" in directions:
        return "|"  # Vertical line
    elif "E" in directions or "W" in directions:
        return "-"  # Horizontal line
    elif "NE" in directions or "SW" in directions:
        return "/"  # Diagonal (/)
    elif "NW" in directions or "SE" in directions:
        return "\\"  # Diagonal (\)
    else:
        return "+"  # Intersection or isolated point
    

def pixels_to_ascii(image, edges=None, ascii_chars=None, edge_chars="|/-\\+_"):
    """Convert pixels to ASCII characters based on intensity and edges."""
    width, height = image.size
    pixels = list(image.getdata())
    ascii_str = ""
    
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            pixel = pixels[idx]
            
            # Check if this pixel is an edge and should use a line character
            if edges is not None and y < edges.shape[0] and x < edges.shape[1] and edges[y, x]:
                # Determine which edge character to use based on direction
                edge_char = determine_edge_direction(edges, x, y)
                if edge_char:
                    ascii_str += edge_char
                    continue
            
            # If not an edge or no direction determined, use regular intensity mapping
            char_index = min(int(pixel * len(ascii_chars) / 256), len(ascii_chars) - 1)
            ascii_str += ascii_chars[char_index]
            
    return ascii_str


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def image_to_ascii(image_path, width=100, ascii_chars=None, output_file=None, animate=False, delay=0.1, edge_detection=False):
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
                
                # Detect edges if requested
                edges = None
                if edge_detection:
                    edges = detect_edges(frame_copy)
                
                # Convert to ASCII
                ascii_str = pixels_to_ascii(frame_copy, edges, ascii_chars)
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
    
    # Detect edges if requested
    edges = None
    if edge_detection:
        edges = detect_edges(image)
    
    # Convert to ASCII
    ascii_str = pixels_to_ascii(image, edges, ascii_chars)
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
    parser.add_argument("-e", "--edges", action="store_true", help="Enable edge detection with line characters")
    
    args = parser.parse_args()
    
    # Process character set
    chars = args.chars
    if args.reverse:
        chars = chars[::-1]
    
    # Convert image to ASCII
    ascii_art = image_to_ascii(
        args.image, args.width, chars, args.output, 
        args.animate, args.delay, args.edges
    )
    
    # Print to console if no output file specified and not animated
    if not args.output and ascii_art and not args.animate:
        print(ascii_art)


if __name__ == "__main__":
    main()
