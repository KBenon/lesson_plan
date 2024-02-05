# Import modules
import streamlit as st
from image_operation_functions import resize_image, encode_image
from openai_functions import chat_complition_images
from document_functions import update_intro_table, \
    get_available_days_name, get_table_id_of_a_day, \
        update_table_for_lesson_plan, get_all_data_from_file
import os
import glob
import io
import json

# =============== Page setup
st.header("Automated Lesson Plan App📄")
st.subheader("Image Uploader section")

# =============== Functions
def show_uploaded_img_in_sidebar(uploaded_images):
    """This function will take uploaded images and display on the sidebar 
    """
    st.sidebar.write("Uploaded Images: ")
    for image in uploaded_images:
        st.sidebar.image(image)

def handle_images_and_prompts(user_uploaded_images):
    prompt = """I need lesson plan according to provided images. 
    Identify the following items from all provided images: 
    - KEY  CONCEPTS & TERMINOLOGY 
    - Aims and Objectives
    - Introduction (Opening routines, warmer, topic lead-in etc.)
    - Lesson Body (Stages, activities, focus etc.)
    - Conclusion (Closing routines & wrap up, e.g. homework setting, review, summary etc.)

    Your response should start with json object.
    I will use json.loads() to load your response in json. Give your response properly so that json.loads() don't create any issue.
    Do not include any explanations, only provide a  RFC8259 compliant JSON response following this format without deviation.
    {"terminology": "key concepts and terminology seperated by new line",
    "aims_and_objective": "Aims and objectives seperated by new line",
    "introduction": "opening routines, warmer, topic lead-in etc seperated by new line",
    "lesson_body": "stages, activities, focus etc seperated by new line",
    "conclusion": "closing routines & wrap up, e.g. homework setting, review, summary etc seperated by new line"}

    Make sure that values must be in string.
    Don't use collections in values. 
    Don't change any key.
    """
    content = [{"type": "text", "text": prompt}]

    for image in user_uploaded_images:
        resized_image = resize_image(image)
        
        # Convert RGBA image to RGB
        if resized_image.mode == 'RGBA':
            resized_image = resized_image.convert('RGB')
        base64_image = encode_image(resized_image)
        content.append({"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"})

    return chat_complition_images(content)

def get_current_path_of_file(file_name):
    """ This function will find the file from current working directory. 
    parameters:
        file_name (required) - the file you want to search from current working directory
    return:
        file path - if file found
        False - if file is not in the directory
    """
    try:
        current_directory = os.getcwd()
        file_path = glob.glob(f"{current_directory}\{file_name}")
        if file_path:
            return file_path
        else:
            return False
    except Exception as e:
        st.error(e)
        st.stop()

def save_content_in_file(text, file_extension=".docx"):
    """ This function will save content into  file and provide path of the  file
    parameters:
        text (required) - the content that you want to save in file
        file_extension (optional) - give the extension of file that you want to save the file. 
                                                bydefault, it is .docx
    """
    # Check if file_extension contain . before if not available the add . in the start of file extension
    if not file_extension.startswith("."):
        file_extension = f".{file_extension}"
    # Intialize file and save content into it
    with open(f"chatgpt_response{file_extension}", "w") as f:
        f.write(text)
    # Get complete file path
    file_path = get_current_path_of_file(f"chatgpt_response{file_extension}")
    return file_path

def show_download_button(text, file_extension=".docx"):
    """ This function will save content into  file and enable download button on web app 
            from where user can download file.
    parameters:
        text (required) - the content that you want to save in file
        file_extension (optional) - give the extension of file that you want to save the file. 
                                                bydefault, it is .docx
    """
    # Check if file_extension contain . before
    if not file_extension.startswith("."):
        file_extension = f".{file_extension}"

    doc_download = get_all_data_from_file()
    bio = io.BytesIO()
    doc_download.save(bio)
    st.download_button(f"Download your {file_extension} file", 
                       data=bio.getvalue(), 
                       file_name=f"lesson_plan{file_extension}", 
                       mime="docx",
                       type="primary")
    
def main():
    file_ready = False
    # =============== User interaction section
    # ---------- Get information to update intro table
    col1, col2 = st.columns(2)
    with col1:
        teacher_name = st.text_input("Teacher: ", value="BEN")
        unit_title = st.text_input("Unit and Title: ", value="ONE DIMENSIONAL ARRAYS")
    with col2:
        course_name = st.text_input("Course: ", value="AP COMPUTER SCIENCE")
        week = st.text_input("Week: ", value="15")
    day_for_lesson_plan = st.selectbox("Select a day for lesson planning", get_available_days_name())

    # ---------- Get images from user for lesson planning
    st.info("Upload image and then press Process button", icon="ℹ")
    # Take images from user
    user_uploaded_images = st.file_uploader("Upload your image", type=['png', 'jpg'], accept_multiple_files=True)
    # User prompt - optional
    # user_prompt = st.text_input(label="", placeholder="Your specified prompt (What ChatGPT do with your images) (optional)", label_visibility="collapsed")
    #  Process button
    process_button = st.button("Process")

    # =============== Checks section
    # Display uploaded images in sidebar if any
    if user_uploaded_images is not None:
        show_uploaded_img_in_sidebar(user_uploaded_images)

    # if user press process button then check for uploaded images
    if process_button:
        if teacher_name and unit_title and course_name and week:
            updated_intro_table = update_intro_table(teacher_name, course_name, unit_title, week)
            table_id_for_lesson_plan = get_table_id_of_a_day(day_for_lesson_plan)

            if updated_intro_table == True:
                st.success("Introduction Updated Successfully")
            else:
                st.error(updated_intro_table)

            if user_uploaded_images:
                with st.spinner('Creating your document...'):
                    gpt_response = handle_images_and_prompts(user_uploaded_images)
                    print(gpt_response)
                    print("--->", type(gpt_response))

                    gpt_response = gpt_response.replace("`", "").replace("json", "")
                    print(gpt_response)
                    print("--->", type(gpt_response))

                    gpt_response_dict = json.loads(gpt_response)
                    print(gpt_response_dict)
                    print("--->", type(gpt_response_dict))

                    # TODO: Replace "data" with gpt response
                    file_ready = update_table_for_lesson_plan(table_id_for_lesson_plan, gpt_response_dict)
                    
                    # Download button
                    if file_ready == True:
                        with st.spinner('Creating your document...'):
                            show_download_button("LESSON_TEMPLATE.docx")
                    else:
                        st.error(file_ready)
            else:
                st.error("Please upload images first then press button", icon="🚨")
        else:
                st.error("All fields are required", icon="🚨")

if __name__ == '__main__':
    main()