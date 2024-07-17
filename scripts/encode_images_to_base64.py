import os
import logging
import base64
import colorlog
from PIL import Image, UnidentifiedImageError
import io

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

SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png']

def encode_image_to_base64(file_path):
    try:
        with Image.open(file_path) as img:
            rgb_image = img.convert('RGB')
            buffered = io.BytesIO()
            rgb_image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except (FileNotFoundError, UnidentifiedImageError) as e:
        logger.error(f"Failed to encode {file_path}: {e}")
        return None

def process_subfolders(output_dir):
    for root, dirs, files in os.walk(output_dir):
        for subdir in dirs:
            subdir_path = os.path.join(root, subdir)
            base64_dir = os.path.join(subdir_path, "base64")

            if not os.path.exists(base64_dir):
                os.makedirs(base64_dir, exist_ok=True)

            for file in os.listdir(subdir_path):
                file_path = os.path.join(subdir_path, file)
                if file.lower().endswith(tuple(SUPPORTED_IMAGE_TYPES)) and "thumbnail" not in file.lower():
                    base64_string = encode_image_to_base64(file_path)
                    if base64_string:
                        base64_filename = os.path.splitext(file)[0] + ".txt"
                        base64_file_path = os.path.join(base64_dir, base64_filename)
                        with open(base64_file_path, 'w') as txt_file:
                            txt_file.write(base64_string)
                        logger.info(f"Saved base64 for {file} to {base64_file_path}")

            # Check if the base64 directory is empty after processing
            if os.path.exists(base64_dir) and not os.listdir(base64_dir):
                os.rmdir(base64_dir)

if __name__ == "__main__":
    output_dir = '/home/robertmcasper/ebay-listing-app/output/processed/images'

    if not os.path.exists(output_dir):
        logger.error(f"Output directory does not exist: {output_dir}")
        exit(1)

    process_subfolders(output_dir)
    logger.info("Processing complete.")
