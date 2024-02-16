from typing import Literal, Optional, Tuple
import logging
import base64
from io import BytesIO
from dotenv import load_dotenv
import os

import replicate
from PIL import Image
import requests
from pydantic import HttpUrl

# Configurations
load_dotenv()

REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')

logging.basicConfig(level=logging.INFO)

class ImageGenerater:
    def __init__(self, asset_suggestions: dict) -> None:
        self.asset_suggestions = asset_suggestions

    def generate_images(self, store_location: str ='../images') -> dict:

        os.makedirs(store_location, exist_ok=True)

        generated_images = {}
        for frame, elements in self.asset_suggestions.items():
            if frame.startswith('frame'):
                generated_images[frame] = []
                for type, description in elements.items():
                    downloaded_image = ImageGenerater.download_image(ImageGenerater.generate_image(prompt=description)[0], store_location)
                    generated_images[frame].append((type, *downloaded_image))

        return generated_images


    @staticmethod
    def generate_image(prompt: str, performance_selection: Literal['Speed', 'Quality', 'Extreme Speed'] = "Speed", 
                       aspect_ratios_selection: str = "1024*1024", image_seed: int = 1234, sharpness: int = 2) -> Optional[dict]:
        """
        Generates an image based on the given prompt and settings.
        "Background": "In the center of a vibrant scene, a high-resolution 3D Coca-Cola bottle surrounded by effervescent bubbles captures the viewer's attention. As the bubbles rise, the bottle seamlessly transforms into a sleek DJ turntable, complete with illuminated controls and a spinning vinyl record bearing the Coke Studio logo. This imagery symbolizes a fusion of refreshing beverage and rhythmic beats. Directly below this dynamic transformation, the call-to-action 'Mix Your Beat' shines in a bold, dynamic font with a playful energy. The text, surrounded by a subtle glow, invites interaction, set against a backdrop designed to evoke creativity and musical exploration.
        :param prompt: Textual description of the image to generate.
        :param performance_selection: Choice of performance level affecting generation speed and quality.
        :param aspect_ratio: The desired aspect ratio of the generated image.
        :param image_seed: Seed for the image generation process for reproducibility.
        :param sharpness: The sharpness level of the generated image.
        :return: The generated image or None if an error occurred.
        """
        try:
            output = replicate.run(
                "konieshadow/fooocus-api-realistic:612fd74b69e6c030e88f6548848593a1aaabe16a09cb79e6d714718c15f37f47",
                input={
                    "prompt": prompt,
                    "performance_selection": performance_selection,
                    "aspect_ratios_selection": aspect_ratios_selection,
                    "image_seed": image_seed,
                    "sharpness": sharpness
                }
            )
            logging.info("Image generated successfully.")
            return output
        except Exception as e:
            logging.error(f"Failed to generate image: {e}")
            return None
        
    @staticmethod
    def decode_image(base64_data: str) -> Optional[Image.Image]:
        """
        Converts a base64 image into pillow iamge object.

        :param base64_data: Textual base64 image data.
        :return: Converted pillow image.
        """
        image_data = base64.b64decode(base64_data)
        image_stream = BytesIO(image_data)
        return (Image.open(image_stream))
    
    @staticmethod
    def download_image(url: HttpUrl, save_path: str) -> Tuple[str, str]:
        """
        Downloads provided url data to given location.

        :param url: HTTP Url of the file.
        :param save_path: Folder location to save the data.
        :return: Tuple of the url and save location.
        """

        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                save_path = os.path.join(save_path, os.path.basename(url))
                image = Image.open(BytesIO(response.content))
                image.save(save_path)
                logging.info(f"Image saved to {save_path}")
                return (url, save_path)
            else:
                raise RuntimeError(f"Failed to download image. Status code: {response.status_code}") from None
        except Exception as e:
            raise RuntimeError(f"An error occurred: {e}") from e
        
        
if __name__ == "__main__":
    # output = ImageGenerater.generate_image("a big star being born")
    # print(output)
    # image = ImageGenerater.download_image('https://replicate.delivery/pbxt/a4uwoBueQhS5cCdF6VeUJfpvuslvXQBA9NRQcE3dFRR6D5skA/d7c83396-f43f-4d61-bdf4-76db405bf2ef.png', './images')
    # image.show()
    a = {
    "frame_1": {
        "Animated Element": "A high-resolution 3D Coca-Cola bottle center-screen, bubbles rising to the top, transitioning into a sleek DJ turntable with a vinyl record that has the Coke Studio logo.",
    },
    "frame_2": {
        "CTA Text": "'Mix Your Beat' in bold, playful font pulsating to the rhythm of a subtle background beat, positioned at the bottom of the screen."
    },
    "explanation": "This variation emphasizes the joy and interactivity of music mixing, with each frame building on the last to create a crescendo of engagement. The 3D bottle-to-turntable animation captures attention, the interactive beat mixer sustains engagement, and the vibrant animations encourage sharing, aligning with the campaign's objectives of engagement and message recall."
    }
    test = ImageGenerater(a)

    test.generate_images()