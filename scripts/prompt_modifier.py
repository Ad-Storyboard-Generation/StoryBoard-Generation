import os
from dotenv import load_dotenv
from openai import OpenAI


def generate_prompt(input_dict):
    """
    This function generates a more detailed description for each key-value pair in the input dictionary using the OpenAI model.
    The model takes each description and generates a new, more detailed description based on it.
    The descriptions are stored in a dictionary with keys like "frame_1", "frame_2", etc., and values that are dictionaries with the original key and the new description.

    Parameters:
    input_dict (dict): A dictionary containing key-value pairs where the key is a string and the value is a description to be expanded.

    Returns:
    dict: A dictionary with keys like "frame_1", "frame_2", etc., and values that are dictionaries with the original key and the new description.
    """
    load_dotenv()

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    prompts = {}
    frame_counter = 1
    for key, value in input_dict.items():
        prompt = f"Given the following description, generate a more detailed description:\n{key}: {value}\n"

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Your task is to generate a more detailed description based on the given description."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        new_description = chat_completion.choices[0].message.content.strip()
        if key == "CTA Button":
            key = "Call to Action"
            new_description = new_description.replace("CTA", "Call to Action")

        frame_key = f"frame_{frame_counter}"
        prompts[frame_key] = {key: new_description}
        frame_counter += 1

    return prompts


frame_1 = {
    "Background": "In the center of a vibrant scene, a high-resolution 3D Coca-Cola bottle surrounded by effervescent bubbles captures the viewer's attention. As the bubbles rise, the bottle seamlessly transforms into a sleek DJ turntable, complete with illuminated controls and a spinning vinyl record bearing the Coke Studio logo. This imagery symbolizes a fusion of refreshing beverage and rhythmic beats. Directly below this dynamic transformation, the call-to-action 'Mix Your Beat' shines in a bold, dynamic font with a playful energy. The text, surrounded by a subtle glow, invites interaction, set against a backdrop designed to evoke creativity and musical exploration.",
    "CTA Button": "'Mix Your Beat' displayed in a bold, dynamic font on a contrasting background. The font style is playful and energetic, designed to evoke a sense of creativity and engagement. The text is surrounded by a subtle glow, suggesting interactivity and inviting the viewer to start their musical adventure."
}

new_prompts = generate_prompt(frame_1)

print("======================================================")
print(new_prompts)