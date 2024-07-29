import os
import logging
import io
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError, ImageEnhance
import pyheif
import colorlog
import concurrent.futures

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

file_handler = logging.FileHandler('image_processing.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

SUPPORTED_IMAGE_TYPES = ['.heic', '.jpg', '.jpeg', '.tiff']
FONT_PATH = '/home/robertmcasper/Repos/ebay-listing-app/fonts/GreatVibes-Regular.ttf'
DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
THUMBNAIL_SIZE = (300, 300)
MAX_THREADS = 2  # Limit the number of threads

def enhance_image(image):
    enhancer = ImageEnhance.Sharpness(image)
    enhanced_image = enhancer.enhance(1.1)  # Slight enhancement
    logger.debug("Image enhanced slightly.")
    return enhanced_image

def rotate_image(image):
    try:
        image = image.transpose(Image.ROTATE_270)
        logger.debug("Image rotated successfully.")
    except Exception as e:
        logger.error(f"Failed to rotate image: {e}")
    return image

def crop_image_to_content(image):
    gray = np.array(image.convert("L"))
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    x, y, w, h = cv2.boundingRect(thresh)
    logger.debug("Image cropped to content.")
    return image.crop((x, y, x+w, y+h))

def align_and_crop_image(image):
    image = crop_image_to_content(image)
    return image

def add_watermark(image, text="Eternal Elegance Emporium", font_path=FONT_PATH):
    try:
        font = ImageFont.truetype(font_path, 224)
        logger.info(f"Using font from {font_path}")
    except IOError:
        logger.error("Font file not found or cannot be opened. Using default font.")
        try:
            font = ImageFont.truetype(DEFAULT_FONT_PATH, 224)
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
    x, y = (width - text_width) // 2, height - text_height - 10
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))
    logger.debug("Watermark added to image.")
    return Image.alpha_composite(image.convert('RGBA'), watermark).convert('RGB')

def generate_thumbnail(image):
    thumbnail = image.copy()
    thumbnail.thumbnail(THUMBNAIL_SIZE)
    logger.debug("Thumbnail generated.")
    return thumbnail

def save_thumbnail(thumbnail, thumbnail_path):
    thumbnail.save(thumbnail_path, format='JPEG', quality=95, optimize=True)
    logger.info(f"Saved thumbnail {thumbnail_path}")

def compress_image(image, file_path):
    try:
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=100, optimize=True)
        buffer.seek(0)
        compressed_image = Image.open(buffer)
        compressed_image.save(file_path, format='JPEG', quality=100, optimize=True)
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
            logger.debug(f"Processed HEIC file: {file_path}")
        else:
            image = Image.open(file_path)
            logger.debug(f"Opened image file: {file_path}")

        image = rotate_image(image)
        image = align_and_crop_image(image)
        image = enhance_image(image)
        image = add_watermark(image, font_path=font_path)

        compress_image(image, file_path)

        thumbnail = generate_thumbnail(image)
        subfolder = os.path.dirname(file_path)
        thumbnail_dir = os.path.join(subfolder, "thumbnails")
        os.makedirs(thumbnail_dir, exist_ok=True)
        thumbnail_filename = os.path.splitext(os.path.basename(file_path))[0] + "_thumbnail.jpg"
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
        save_thumbnail(thumbnail, thumbnail_path)

        return True
    except (UnidentifiedImageError, OSError) as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return False

def process_subfolders(output_dir):
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.lower().endswith(tuple(SUPPORTED_IMAGE_TYPES)):
                    file_path = os.path.join(root, file)
                    futures.append(executor.submit(process_image, file_path, FONT_PATH))
        
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                logger.info("Image processed successfully.")
            else:
                logger.error("Failed to process image.")

if __name__ == "__main__":
    output_dir = '/home/robertmcasper/Repos/ebay-listing-app/output/processed/images'

    if not os.path.exists(output_dir):
        logger.error(f"Output directory does not exist: {output_dir}")
        exit(1)

    process_subfolders(output_dir)
    logger.info("Processing complete.")
