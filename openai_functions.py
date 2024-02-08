# Import modules
import streamlit as st
from openai import OpenAI
from image_operation_functions import encode_image, resize_image

# Define api keys
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def chat_complition_images(content, total_plans):
    """
    This function uses the OpenAI API to generate text based on the input text.

    Parameters:
        content: The input text and images.
        total_plans (int): The number of plans to generate.

    Returns:
        str: The generated text.
    """
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        max_tokens=600*total_plans
    )
    return response.choices[0].message.content


