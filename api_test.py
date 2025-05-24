import io
from image_validator_test import check_file_type, check_magic_number, verify_image, check_file_size
from PIL import Image

 
# Generate a valid JPEG image
def create_valid_jpeg():
    jpeg_image = Image.new("RGB", (10, 10), "blue")  # 10x10 blue image
    jpeg_buffer = io.BytesIO()
    jpeg_image.save(jpeg_buffer, format="JPEG")
    return jpeg_buffer.getvalue()

# Generate a valid PNG image
def create_valid_png():
    png_image = Image.new("RGB", (10, 10), "green")  # 10x10 green image
    png_buffer = io.BytesIO()
    png_image.save(png_buffer, format="PNG")
    return png_buffer.getvalue()


# Generate a large JPEG image
def create_large_jpeg(width=5000, height=5000, color="red"):
    """
    Creates a large JPEG image with the specified dimensions and color.
    :param width: Width of the image
    :param height: Height of the image
    :param color: Background color of the image
    :return: Byte data of the large JPEG image
    """
    large_image = Image.new("RGB", (width, height), color)  # Create a large image
    large_buffer = io.BytesIO()
    large_image.save(large_buffer, format="JPEG")  # Save as JPEG
    return large_buffer.getvalue()

# Replace your test data
large_image_data = create_large_jpeg()  # Default size is 5000x5000 pixels

print(f"Large JPEG Test Data Size: {len(large_image_data)} bytes")

# Replace your test data
valid_jpeg_data = create_valid_jpeg()
valid_png_data = create_valid_png()

print(f"JPEG Test Data Size: {len(valid_jpeg_data)} bytes")
print(f"PNG Test Data Size: {len(valid_png_data)} bytes")



invalid_txt_data = b'Hello, this is a plain text file.'


def test_file_from_stream(file_data, max_size):
    file_stream = io.BytesIO(file_data)
    try:
        check_file_type(file_stream)
        print("File type is valid.")
    except ValueError as e:
        print(f"File type validation failed: {e}")
    file_stream.seek(0)
    try:
        check_magic_number(file_stream)
        print("Magic number is valid.")
    except ValueError as e:
        print(f"Magic number validation failed: {e}")
    file_stream.seek(0)
    try:
        verify_image(file_stream)
        print("Image is valid.")
    except ValueError as e:
        print(f"Image verification failed: {e}")
    try:
        check_file_size(file_data, max_size)
        print("File size is valid.")
    except ValueError as e:
        print(f"File size validation failed: {e}")

def simulate_file_upload_tests():
    max_size = 5 * 1024 * 1024
    print("Testing valid JPEG image:")
    test_file_from_stream(valid_jpeg_data, max_size)
    print("\nTesting valid PNG image:")
    test_file_from_stream(valid_png_data, max_size)
    print("\nTesting invalid text file:")
    test_file_from_stream(invalid_txt_data, max_size)
    print("\nTesting large image (over 5 MB):")
    test_file_from_stream(large_image_data, max_size)

if __name__ == "__main__":
    simulate_file_upload_tests()
