import os
import logging
import io
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import pyheif
from datetime import datetime
import colorlog

# Configure logging
log_colors_config = {
    'DEBUG': 'bold_blue',
    'INFO': 'bold_green',
    'WARNING': 'bold_yellow',
    'ERROR': 'bold_red',
    'CRITICAL': 'bold_red,bg_white',
}

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors=log_colors_config
))

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

SUPPORTED_IMAGE_TYPES = ['.heic', '.jpg', '.jpeg', '.png', '.tiff']
FONT_PATH = '/home/robertmcasper/ebay-listing-app/fonts/GreatVibes-Regular.ttf'
DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
THUMBNAIL_SIZE = (300, 300)

def enhance_image(image):
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    enhanced_image = cv2.filter2D(image, -1, sharpen_kernel)
    return enhanced_image

def rotate_image(image):
    try:
        image = image.transpose(Image.ROTATE_270)  # Rotate as needed
    except Exception as e:
        logger.error(f"Failed to rotate image: {e}")
    return image

def crop_image_to_content(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    x, y, w, h = cv2.boundingRect(thresh)
    return image.crop((x, y, x+w, y+h))

def align_and_crop_image(image):
    image = crop_image_to_content(image)
    return image

def add_watermark(image, text="Eternal Elegance Emporium", font_path=FONT_PATH):
    try:
        font = ImageFont.truetype(font_path, 48)  # Increased font size by 50% from 32 to 48
        logger.info(f"Using font from {font_path}")
    except IOError:
        logger.error("Font file not found or cannot be opened. Using default font.")
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, 48)  # Increased font size by 50% from 32 to 48
            logger.info("Using default font.")
        except IOError:
            logger.error("Default font file not found. Using default PIL font.")
            font = ImageFont.load_default()

    watermark = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark, 'RGBA')
    width, height = image.size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x, y = (width - text_width) // 2, height - text_height - 10  # Bottom middle with 10 pixels margin from bottom
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))  # Adjusted transparency to 200
    return Image.alpha_composite(image.convert('RGBA'), watermark)

def generate_thumbnail(image):
    thumbnail = image.copy()
    thumbnail.thumbnail(THUMBNAIL_SIZE)
    return thumbnail

def save_thumbnail(thumbnail, thumbnail_path):
    thumbnail.save(thumbnail_path, quality=95, optimize=True)
    logger.info(f"Saved thumbnail {thumbnail_path}")

def convert_to_supported_format(file_path):
    try:
        image = Image.open(file_path)
        new_file_path = os.path.splitext(file_path)[0] + ".png"
        image.save(new_file_path)
        os.remove(file_path)  # Remove the old image
        return new_file_path
    except (UnidentifiedImageError, OSError) as e:
        logger.error(f"Failed to convert {file_path}: {e}")
        return None

def compress_image(image, file_path):
    try:
        buffer = io.BytesIO()
        image.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        compressed_image = Image.open(buffer)
        compressed_image.save(file_path, format='PNG', optimize=True)
        logger.info(f"Compressed and saved {file_path}")
    except Exception as e:
        logger.error(f"Failed to compress image {file_path}: {e}")

def process_image(file_path, font_path):
    try:
        if file_path.lower().endswith('.heic'):
            heif_file = pyheif.read(file_path)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
        else:
            image = Image.open(file_path)

        image = rotate_image(image)
        image = align_and_crop_image(image)
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        enhanced_image = enhance_image(image_cv)

        resized_image_rgb = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB)
        resized_image_pil = Image.fromarray(resized_image_rgb)
        resized_image_pil = add_watermark(resized_image_pil, font_path=font_path)

        # Save the enhanced image, replacing the original
        compress_image(resized_image_pil, file_path)

        # Generate and save thumbnail
        thumbnail = generate_thumbnail(resized_image_pil)
        thumbnail_dir = os.path.join(os.path.dirname(file_path), "thumbnails")
        os.makedirs(thumbnail_dir, exist_ok=True)
        thumbnail_filename = os.path.splitext(os.path.basename(file_path))[0] + "_thumbnail.png"
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
        save_thumbnail(thumbnail, thumbnail_path)

        return True
    except (UnidentifiedImageError, OSError) as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return False

def process_subfolders(output_dir):
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.lower().endswith(tuple(SUPPORTED_IMAGE_TYPES)):
                file_path = os.path.join(root, file)
                new_file_path = convert_to_supported_format(file_path)
                if new_file_path:
                    process_image(new_file_path, FONT_PATH)

if __name__ == "__main__":
    output_dir = '/home/robertmcasper/ebay-listing-app/output/processed/images'

    if not os.path.exists(output_dir):
        logger.error(f"Output directory does not exist: {output_dir}")
        exit(1)

    process_subfolders(output_dir)
    logger.info("Processing complete.")
