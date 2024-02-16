from PIL import Image
import os


def get_image_size(image_path: str) -> tuple:
    """
    Get the width and height of an image.

    :param image_path: Path to the image file.
    :return: A tuple containing the width and height of the image.
    """
    with Image.open(image_path) as img:
        width, height = img.size

    return width, height


def resize_image(image_path: str, new_width: int, new_height: int, output_dir: str = './images/resized_images') -> None:
    """
    Resize an image to a specific width and height and save it to a different location.

    :param image_path: Path to the image file.
    :param new_width: The new width for the image.
    :param new_height: The new height for the image.
    :param output_dir: The directory to save the resized image.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_dir, filename)

    with Image.open(image_path) as img:
        resized_img = img.resize((new_width, new_height))
        resized_img.save(output_path)

    print(f"Resized image saved to {output_path}")