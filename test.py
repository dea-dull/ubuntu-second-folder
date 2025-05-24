import io
import os
from image_validator_test import check_file_type, check_magic_number, verify_image, check_file_size

# Sample test data (replace with actual file paths or streams)
valid_image_path = "/home/ubuntu/Images/imageTest1.jpg"
invalid_image_path = "/home/ubuntu/Images/notea.yaml"
large_image_path = "/home/ubuntu/Images/images.jpeg"

# Read the file data
def read_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

# Testing the validation functions
def test_file_validation():
    # Test with valid file (JPEG)
    try:
        file_data = read_file(valid_image_path)
        file_stream = io.BytesIO(file_data)
        
        # Check file type
        check_file_type(file_stream)
        
        # Check magic number (MIME type)
        check_magic_number(file_stream)
        
        # Verify image integrity
        verify_image(file_stream)
        
        # Check file size
        check_file_size(file_data)  # Uses the default max_size (5 MB)
        
        print(f"'{valid_image_path}' passed all checks!")
    
    except ValueError as e:
        print(f"Validation failed for '{valid_image_path}': {e}")
    
    # Test with invalid file (text file)
    try:
        file_data = read_file(invalid_image_path)
        file_stream = io.BytesIO(file_data)
        
        check_file_type(file_stream)
        check_magic_number(file_stream)
        verify_image(file_stream)
        check_file_size(file_data)
        
        print(f"'{invalid_image_path}' passed all checks!")
    
    except ValueError as e:
        print(f"Validation failed for '{invalid_image_path}': {e}")
    
    # Test with large file
    try:
        file_data = read_file(large_image_path)
        file_stream = io.BytesIO(file_data)
        
        check_file_size(file_data)  # This check will fail if file is too large
        
        print(f"'{large_image_path}' passed all checks!")
    
    except ValueError as e:
        print(f"Validation failed for '{large_image_path}': {e}")

if __name__ == "__main__":
    test_file_validation()
