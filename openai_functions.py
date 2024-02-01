# Import modules
import streamlit as st
import openai
from openai import OpenAI
from image_operation_functions import encode_image, resize_image

# Define api keys
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()

# =============== User prompt
def user_prompt(placeholder):
    user_prompt = st.text_input(label="", placeholder=placeholder, label_visibility="collapsed")
    if user_prompt:
        return user_prompt
    
def chat_complition_images(content):
    """This function will extract information from images and respond to your prompt
    """
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        max_tokens=500
    )
    return response.choices[0].message.content


