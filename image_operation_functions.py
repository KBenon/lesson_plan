# Import modules
import base64
from PIL import Image
import io

def encode_image(image):
    """
    Encodes an image into a base64 string.

    Parameters:
    image : Union[str, Image.Image]
        The image to be encoded. Can be a file path or a PIL Image object.

    Returns:
        The base64 encoded image.
    """
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

def resize_image(image, max_width=768, max_height=1024):
    """ 
    This function get image and resize it to 768x1024(default)
    
    Parameters:
        image (required): The image to be resized. Can be a file path or a PIL Image object.
        max_width (optional): The maximum width of the resized image. Defaults to 768.
        max_height (optional): The maximum height of the resized image. Defaults to 1024.
    
    Return:
        resized image: The resized image.
        Error_error -  if there is any problem in resizing
    """
    try:
        pil_image = Image.open(image)
        # Get size of orignal image
        image_width, image_height = pil_image.size
        
        # Check and limit size of image
        if image_width > max_width:
            image_width = max_width
        if image_height > max_height:
            image_height = max_height

        pil_image_resized = pil_image.resize((image_width, image_height))
        print(pil_image_resized.size)
        return pil_image_resized
    except Exception as e:
        return f"Error_{e}"