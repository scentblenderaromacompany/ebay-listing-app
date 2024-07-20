import os
import logging
import base64
import colorlog
from PIL import Image, UnidentifiedImageError
import io
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

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png']
MAX_THREADS = 2

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

def process_images_in_subdir(subdir_path):
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

def process_subfolders(output_dir):
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for root, dirs, _ in os.walk(output_dir):
            for subdir in dirs:
                subdir_path = os.path.join(root, subdir)
                futures.append(executor.submit(process_images_in_subdir, subdir_path))
        
        for future in concurrent.futures.as_completed(futures):
            if future.result() is None:
                logger.info("Subdirectory processed successfully.")
            else:
                logger.error("Failed to process subdirectory.")

if __name__ == "__main__":
    output_dir = '/home/robertmcasper/ebay-listing-app/output/processed/images'

    if not os.path.exists(output_dir):
        logger.error(f"Output directory does not exist: {output_dir}")
        exit(1)

    process_subfolders(output_dir)
    logger.info("Processing complete.")
