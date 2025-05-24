import os
import magic
from PIL import Image
import io

# Fetch allowed types from environment variable or use defaults
allowed_types_env = os.getenv("ALLOWED_FILE_TYPES", "image/jpeg,image/png,image/gif")
allowed_types = allowed_types_env.split(",")

# Fetch max file size from environment variable or default to 5MB
max_size = int(os.getenv("MAX_FILE_SIZE", 5 * 1024 * 1024))  # Default: 5 MB

def check_file_type(upload_stream):
    """
    Validate the file type using the magic library's MIME type detection.
    """
    position = upload_stream.tell()  # Save current stream position
    file_type = magic.from_buffer(upload_stream.read(1024), mime=True)  # Detect MIME type
    upload_stream.seek(position)  # Reset stream position
    
    if file_type not in allowed_types:
        raise ValueError(f"Invalid file type detected: {file_type}. Allowed types: {', '.join(allowed_types)}")


def check_magic_number(upload_stream):
    """
    Validate the file's magic number (file header) using the magic library.
    """
    position = upload_stream.tell()  # Save current stream position
    file_type = magic.from_buffer(upload_stream.read(1024), mime=True)  # Read magic number
    upload_stream.seek(position)  # Reset stream position

    if file_type not in allowed_types:
        raise ValueError(f"Invalid magic number: {file_type}. Allowed types: {', '.join(allowed_types)}")

def verify_image(upload_stream):
    """
    Verify the integrity of the image using Pillow.
    """
    try:
        image = Image.open(upload_stream)
        image.verify()  # Check if the image is valid
    except (IOError, SyntaxError):
        raise ValueError("Invalid image: The image is corrupted or not a valid format.")

def check_file_size(file_data, max_size=max_size):
    """
    Validate that the file size does not exceed the maximum limit.
    """
    file_size = len(file_data)
    if file_size > max_size:
        raise ValueError(f"File size exceeds the maximum limit of {max_size / (1024 * 1024):.2f} MB.")
    return file_size
