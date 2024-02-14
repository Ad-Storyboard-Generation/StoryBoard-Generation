from typing import Literal, Optional, Tuple 
import logging 
import base64
from io import BytesIO
import os
from PIL import Image

import replicate
from pydantic import HttpUrl
import requests


# Set Replicate API token in the environment variable
os.environ['REPLICATE_API_TOKEN'] = 'YOUR_API_TOKEN'
logging.basicConfig(level=logging.INFO)


class ImageGenerator:
    """
    A class for generating and working with images using the Replicate API.

    Attributes:
        asset_suggestions (dict): A dictionary containing frame and elements for image generation.
    """
    def __init__(self, asset_suggestions: dict) -> None:
        """
        Initialize the ImageGenerator object with asset suggestions.

        Args:
            asset_suggestions (dict): A dictionary containing frame and elements for image generation.
        """
        self.asset_suggestions = asset_suggestions
    
    def generate_images(self, store_location: str ='./images') -> dict:
        """
        Generate images based on the provided asset suggestions.

        Args:
            store_location (str, optional): The directory path to store the generated images. Defaults to './images'.

        Returns:
            dict: A dictionary containing generated images with frame and element details.
        """
        generated_images = {}
        for frame, elements in self.asset_suggestions.items():
            if frame.startswith('frame'):
                generated_images[frame] = []
                for type, description in elements.items():
                    downloaded_image = ImageGenerator.download_image(
                        ImageGenerator.generate_images(prompt=description)[0], store_location)
                    generated_images[frame].append((type, *downloaded_image))
        
        return generated_images
    
    @staticmethod
    def generate_images(prompt: str) -> Optional[list]:
        """
        Generate images using the Replicate API based on the provided prompt.

        Args:
            prompt (str): The prompt for image generation.

        Returns:
            list: A list containing image details, or None if an error occurs.
        """
        focus_api = os.environ.get('FOCUS_API')
        
        try:
            output = replicate.run(
                    'konieshadow/fooocus-api:{focus_api}',
                    input={
                        'prompt': prompt,
                        'num_images': 1
                    }
                )
            logging.info('Image generated successfully')
            return output
        except Exception as e:
            logging.error(f'Error generating image: {e}')
            return None
        
    @staticmethod
    def decode_image(base64_data: str) -> Optional[Image.Image]:
        """
        Decode base64-encoded image data and return the PIL Image object.

        Args:
            base64_data (str): Base64-encoded image data.

        Returns:
            Optional[Image.Image]: The PIL Image object, or None if decoding fails.
        """
        image_data = base64.b64decode(base64_data)
        image_stream = BytesIO(image_data)
        return Image.open(image_stream)
    
    @staticmethod
    def download_image(url: HttpUrl, save_path: str) -> Tuple[str, str]:
        """
        Download an image from the given URL and save it to the specified path.

        Args:
            url (HttpUrl): The URL of the image to be downloaded.
            save_path (str): The local path where the image should be saved.

        Returns:
            Tuple[str, str]: A tuple containing the original URL and the local path where the image is saved.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image.save(save_path)
                logging.info(f'Image downloaded successfully at {save_path}')
                return (url, save_path)
            
        except Exception as e:
            raise RuntimeError(f'Error downloading image: {e}')
