from typing import Literal, Optional, Tuple 
import logging 
import base64
from io import BytesIO
import os
from PIL import Image

import replicate
from pydantic import HttpUrl
import requests


os.environ['REPLICATE_API_TOKEN'] = 'YOUR_API_TOKEN'
logging.basicConfig(level=logging.INFO)


class ImageGenerater: 
    def __init__(self, asset_suggestions: dict) -> None:
        self.asset_suggestions = asset_suggestions
    
    def generate_images(self, store_location: str ='./images') -> dict:
        generated_images = {}
        for frame, elements in self.asset_suggestions.items():
            if frame.startswith('frame'):
                generated_images[frame] = []
                for type, description in elements.items():
                    downloaded_image = ImageGenerater.download_image(ImageGenerater.generate_images(prompt=description)[0],store_location)
                    generated_images[frame].append((type, *downloaded_image))
        
        return generated_images
    
    @staticmethod
    def generate_images(prompt: str):
        
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
        image_data = base64.b64decode(base64_data)
        image_stream = BytesIO(image_data)
        return Image.open(image_stream)
    
    @staticmethod
    def download_image(url: HttpUrl, save_path: str) -> Tuple[str, str]:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image.save(save_path)
                logging.info(f'Image downloaded successfully at {save_path}')
                return (url, save_path)
            
        except Exception as e:
            raise RuntimeError(f'Error downloading image: {e}')
        
    
    