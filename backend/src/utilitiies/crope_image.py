from PIL import Image

def crop_image(file_path: str, output_size=(500, 500)) -> str:
    """Crop the image to a square and resize it."""
    with Image.open(file_path) as img:
        # Get dimensions and crop to square
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = (width + min_dim) // 2
        bottom = (height + min_dim) // 2

        # Resize the cropped image
        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize(output_size)
        img_resized.save(file_path)  # Overwrite the existing file

    return file_path