import argparse
from PIL import Image

# A string of characters ordered from darkest to lightest.
# This character set will be used to represent the brightness of each pixel.
ASCII_CHARS = " .,;:-_+*#%&@$"

def resize_image(image, new_width=100):
    """
    Resizes an image while maintaining the aspect ratio.
    """
    width, height = image.size
    ratio = height / width
    # The 0.5 factor corrects for the difference in character aspect ratio (characters are taller than they are wide).
    new_height = int(new_width * ratio * 0.5)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def map_pixels_to_color_ascii(image, chars=ASCII_CHARS):
    """
    Takes an image and maps each pixel's color and brightness to a
    colored ASCII character using ANSI escape codes.
    """
    pixels = list(image.getdata())
    ascii_art_str = ""
    step_size = 256 / len(chars)
    
    # Get the width of the resized image
    width, _ = image.size
    
    # Iterate through the pixels with a counter
    for i, (r, g, b) in enumerate(pixels):
        # Calculate a simple brightness value for character selection.
        brightness = (r + g + b) // 3
        
        # Map the brightness to an index in the character set.
        index = int(brightness / step_size)
        
        # ANSI escape code for a true color (24-bit) foreground.
        # Format is \033[38;2;R;G;Bm
        ansi_color_code = f"\033[38;2;{r};{g};{b}m"
        
        # The character representing the brightness.
        ascii_char = chars[index]
        
        # The ANSI escape code to reset color to default.
        ansi_reset_code = "\033[0m"
        
        ascii_art_str += f"{ansi_color_code}{ascii_char}{ansi_reset_code}"
        
        # Add a newline at the end of each row
        if (i + 1) % width == 0:
            ascii_art_str += "\n"
            
    return ascii_art_str

def main():
    """
    Main function to parse arguments and run the ASCII conversion.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Convert an image to color ASCII art.')
    parser.add_argument('input_image', type=str, help='Path to the input image file.')
    parser.add_argument('-o', '--output_file', type=str, help='Optional path to save the output text file with ANSI codes.')
    parser.add_argument('-w', '--width', type=int, default=100, help='Optional output width of the ASCII art (default: 100).')

    args = parser.parse_args()

    try:
        # Open the image file
        image = Image.open(args.input_image).convert("RGB")

        # Resize the image while maintaining aspect ratio
        resized_image = resize_image(image, args.width)

        # Convert the image pixels to a string of colored ASCII characters
        ascii_art = map_pixels_to_color_ascii(resized_image)

        # Print the ASCII art to the console
        print(ascii_art)

        # Save the output to a file if an output path was provided
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(ascii_art)
            print(f"Color ASCII art successfully saved to {args.output_file}")

    except FileNotFoundError:
        print(f"Error: The file at '{args.input_image}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()

# uv run ascii_converter.py car.jpg
