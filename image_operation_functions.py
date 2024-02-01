import base64
from PIL import Image
import io

# def encode_image(image_path):
#   with open(image_path, "rb") as image_file:
#     return base64.b64encode(image_file.read()).decode('utf-8')

def encode_image(image):
    if isinstance(image, str):  # If image is a file path
        with open(image, "rb") as image_file:
            image_data = image_file.read()
    elif isinstance(image, Image.Image):  # If image is a PIL Image object
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_data = image_bytes.getvalue()
    else:
        raise ValueError("Unsupported image type")

    base64_image = base64.b64encode(image_data).decode('utf-8')
    return base64_image

def resize_image(image, width=768, height=1024):
    """ This function get image and resize it to 500x500(default)
    parameters:
        - image (required)
        - width (optional)
        - height (optional)
    return:
        resized image
        Error_error -  if there is any problem in resizing
    """
    try:
        pil_image = Image.open(image)
        
        original_image_width, original_image_height = pil_image.size
        print(original_image_width, original_image_height)
        
        # TODO: conditions to resize image to 1000px

        pil_image_resized = pil_image.resize((width, height))
        print(pil_image_resized.size)
        return pil_image_resized
    except Exception as e:
        return f"Error_{e}"