import qrcode
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import urllib.parse
from bs4 import BeautifulSoup
import numpy as np
import re

def validate_url(url):
    """Validate URL format"""
    url_pattern = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}'  # domain
        r'(:\d+)?'  # optional port
        r'(/[-a-zA-Z0-9%_.~#]*)*'  # path
        r'(\?[;&a-zA-Z0-9%_.~+=-]*)?'  # query string
        r'(#[-a-zA-Z0-9_]*)?$'  # fragment
    )
    return bool(url_pattern.match(url))

def create_rainbow_gradient(width, height):
    """Create a rainbow gradient image"""
    rainbow_img = Image.new("RGB", (width, height))
    pixels = rainbow_img.load()
    # Defines rainbow colors
    rainbow_colors = [
        (255, 0, 0),    # Red
        (255, 165, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 128, 0),    # Green
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211)   # Violet
    ]
    
    # Calculates horizontal gradient
    for x in range(width):
        segment = len(rainbow_colors) - 1
        segment_width = width / segment
        idx = int(x / segment_width)
        next_idx = min(idx + 1, segment - 1)
        t = (x % segment_width) / segment_width
        r = int(rainbow_colors[idx][0] * (1 - t) + rainbow_colors[next_idx][0] * t)
        g = int(rainbow_colors[idx][1] * (1 - t) + rainbow_colors[next_idx][1] * t)
        b = int(rainbow_colors[idx][2] * (1 - t) + rainbow_colors[next_idx][2] * t)
        for y in range(height):
            pixels[x, y] = (r, g, b)
    return rainbow_img.convert("RGBA")

def create_circular_mask(size):
    """Create a circular mask for the logo"""
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    return mask

def create_rainbow_qr_code(data, output_path, logo_url=None):
    """Create a rainbow QR code with optional logo"""
    if not validate_url(data):
        raise ValueError("Invalid URL format")

    # Creates QR code instance with high error correction
    qr = qrcode.QRCode(
        version=None,  # Auto-determine version based on data
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )

    # Adds data to the QR code
    qr.add_data(data)
    qr.make(fit=True)

    # Creates QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_width, qr_height = qr_img.size

    # Creates a rainbow gradient image
    rainbow_img = create_rainbow_gradient(qr_width, qr_height)
    qr_array = np.array(qr_img)
    mask = (qr_array[:, :, 0] == 0)
    rainbow_array = np.array(rainbow_img)
    final_qr = Image.new("RGBA", (qr_width, qr_height), (0, 0, 0, 255))  # Black background
    final_qr_array = np.array(final_qr)
    final_qr_array[mask] = rainbow_array[mask]
    final_qr = Image.fromarray(final_qr_array)

    # Add logo if provided
    if logo_url:
        if not validate_url(logo_url):
            raise ValueError("Invalid logo URL format")
            
        try:
            logo_size = qr_width // 6  # Slightly smaller logo size
            response = requests.get(logo_url, timeout=5)
            response.raise_for_status()
            
            try:
                logo = Image.open(BytesIO(response.content)).convert("RGBA")
            except Image.UnidentifiedImageError:
                raise ValueError("Logo URL does not point to a recognized image format.")
            except Exception as img_error:
                raise ValueError(f"Error decoding image from URL: {str(img_error)}")
                
            # Resize logo with padding
            padding = int(logo_size * 0.1)  # 10% padding
            logo = logo.resize((logo_size - padding * 2, logo_size - padding * 2), Image.LANCZOS)
            
            # Create a new image with padding
            padded_logo = Image.new("RGBA", (logo_size, logo_size), (255, 255, 255, 0))
            padded_logo.paste(logo, (padding, padding), logo)
            
            # Calculate position to center the logo
            logo_position = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            
            # Create a temporary image for the logo area
            temp_qr = final_qr.copy()
            
            # Create a mask from the logo's alpha channel
            logo_mask = padded_logo.split()[3]
            
            # Create a black background for the logo area
            black_patch = Image.new("RGBA", (logo_size, logo_size), (0, 0, 0, 255))
            
            # Apply the logo mask to create a black background that follows the logo's shape
            black_patch.putalpha(logo_mask)
            
            # Paste the black background
            temp_qr.paste(black_patch, logo_position, black_patch)
            final_qr = temp_qr
            
            # Paste the logo on top
            final_qr.paste(padded_logo, logo_position, padded_logo)
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch logo: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing logo: {str(e)}")

    # Save the final QR code
    try:
        final_qr.save(output_path, "PNG", quality=95)
        return output_path
    except Exception as e:
        raise ValueError(f"Failed to save QR code: {str(e)}")

def main():
    # Data to encode in the QR code
    data = "https://example.com"  # Replace with your desired URL
    output_path = "qr_code_output.png"  # Default output path
    
    try:
        create_rainbow_qr_code(data, output_path)
        print(f"QR code saved as {output_path}")
    except Exception as e:
        print(f"Error creating QR code: {e}")

if __name__ == "__main__":
    main()