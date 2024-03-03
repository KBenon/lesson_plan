# Import modules
import streamlit as st
import streamlit_ext as ste
import glob
import json
import os
import io
from image_operation_functions import resize_image, encode_image
from openai_functions import chat_complition_images
from document_functions import update_intro_table, \
    get_available_days_name, get_table_id_of_days, \
        update_table_for_lesson_plan, get_all_data_from_file, \
            document_templates, document_templates_names_for_saving, \
                update_assessment_and_marking_guide

# =============== Page setup
st.header("Automated Lesson Plan App📄")
# st.subheader("Image Uploader section")

# =============== Functions
def show_uploaded_img_in_sidebar(uploaded_images):
    """
    Display uploaded images in the sidebar.

    Parameters:
        uploaded_images (List[Image.Image]): A list of images uploaded by the user.
    """
    st.sidebar.info("Upload image and then press Process button", icon="ℹ")
    st.sidebar.write("Uploaded Images: ")
    for image in uploaded_images:
        st.sidebar.image(image)

def handle_images_and_prompts(user_uploaded_images, days_selected_by_user, no_of_questions_for_assessment, dict_of_duration_and_activity):
    """
    Prompts the ChatGPT model to generate a lesson plan based on the provided images.

    Parameters:
        user_uploaded_images (List[Image.Image]): A list of images uploaded by the user.
        no_of_days (int): The number of days for which the lesson plan is required.
        no_of_questions_for_assessment (int): The number of questions for each day of the assessment.
        dict_of_duration_and_activity(dict): 
    Returns:
        str: A JSON string containing the lesson plan for each day.
    """
    # Prompt to get desired response from chatGPT
    no_of_days = len(days_selected_by_user)
    
    # Extract durations
    durations = [day["Duration"] for day in dict_of_duration_and_activity.values()]
    durations = ", ".join(str(duration)+" minutes" for duration in durations[:-1]) + " and " + str(durations[-1]) + " minutes"

    prompt = f"""I need {f"{no_of_days} lesson plans" if no_of_days>1 else f"{no_of_days} lesson plan"} according to provided images using Bloom's Taxonomy.
    Design lesson plans for {durations} respectively.
    Duration must be same as provided, adjust lesson plan according to time duration.
    
    Identify the following items from all provided images:
    - KEY CONCEPTS & TERMINOLOGY
    - Aims and Objectives
    - Introduction (Opening routines, warmer, topic lead-in etc.)
    - Lesson Body (Stages, activities, focus etc.)
    - Duration
    - Conclusion (Closing routines & wrap up, e.g. homework setting, review, summary etc.)
    - Assessment ({no_of_questions_for_assessment} questions for students for assessment from the topic)
    - Exact answers of assessment questions

    Your response should start with JSON object.
    I will use `json.loads()` to load your response in JSON. Give your response properly so that `json.loads()` don't create any issue.
    Do not include any explanations, only provide {no_of_days} RFC8259 compliant JSON response following this format without deviation.
    [{{"terminology": "key concepts and terminology separated by new line",
    "aims_and_objective": "Aims and objectives separated by new line. Each line should start with SWBAT",
    "introduction": "opening routines, warmer, topic lead-in etc separated by new line",
    "lesson_body": "stages, activities, focus etc and should be a bit long e.g 4 to 5 lines",
    "Duration": "lecture duration in minutes",
    "conclusion": "closing routines & wrap up, e.g. homework setting, review, summary etc separated by new line",
    "assessment": "{no_of_questions_for_assessment} questions for students for assessment from the topic separated by new line",
    "answers": "Exact answers of assessment questions separated by new line"}}]

    Make sure that values must be in string.
    Don't repeat terminologies for each day.
    Don't change any key.
    Don't forget to use Bloom's Taxonomy while creating lesson plans.
    Don't forget any instruction mentioned above.
    """
    # Don't use collections in values. 

    content = [{"type": "text", "text": prompt}]

    for image in user_uploaded_images:
        resized_image = resize_image(image)
        
        # Convert RGBA image to RGB
        if resized_image.mode == 'RGBA':
            resized_image = resized_image.convert('RGB')
        base64_image = encode_image(resized_image)
        content.append({"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"})
    # print(content)
    # print(prompt)
    return chat_complition_images(content, no_of_days)

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

def show_download_button(file_name_containing_data, file_extension=".docx"):
    """ 
    This function will save content into  file and enable download button on web app 
     from where user can download file.
    
    Parameters:
        text (required): the content that you want to save in file
        file_extension (optional): give the extension of file that you want to save the file. 
                                                bydefault, it is .docx
    """
    # Check if file_extension contain . before
    if not file_extension.startswith("."):
        file_extension = f".{file_extension}"

    doc_download = get_all_data_from_file(file_name_containing_data)
    bio = io.BytesIO()
    doc_download.save(bio)
    # use ste extension of streamlit for the reload problem while press download button
    # while click on download button page reload and other download buttons disappear because app rerun.
    # using ste prevent application from rerun.
    ste.download_button(f"Download your {file_name_containing_data}{file_extension} file", 
                       data=bio.getvalue(), 
                       file_name=f"{file_name_containing_data}{file_extension}", 
                       mime="docx")
    
def main():
    """
    Main function of the app.
    """
    file_ready = assessment_ready = marking_guide_ready = False
    # =============== User interaction section
    # ---------- Get information to update intro table
    col1, col2 = st.columns(2)
    # Define a column layout with two columns.
    with col1:
        teacher_name = st.text_input("Teacher: ", value="BEN")
        unit_title = st.text_input("Unit and Title: ", value="ONE DIMENSIONAL ARRAYS")
    with col2:
        course_name = st.text_input("Course: ", value="AP COMPUTER SCIENCE")
        week = st.text_input("Week: ", value="19")
    
    user_selected_days = st.multiselect("Select days for lesson planning", get_available_days_name())
    
    # Define a column layout with two columns.
    col3, col4 = st.columns(2)
   
    duration_activity = {}
    for day in user_selected_days:
        with col3:
            duration = st.number_input(f"Select duration for {day}", 
                                    min_value=10, value="min", key=f"duration_{day}")
        with col4:
            activity = st.text_area(f"Enter Activity for {day}", key=f"activity_{day}")
        duration_activity[day] = {"Duration": duration, "Activity": activity}
    # st.write(duration_activity)
    
    number_of_questions_for_assessment = st.number_input("Select number of questions of each day for assessment", 
                                                         min_value=1, max_value=10, value="min")
    
    # ---------- Get images from user for lesson planning
    # st.info("Upload image and then press Process button", icon="ℹ")
    # Take images from user
    user_uploaded_images = st.file_uploader("Upload your image", type=['png', 'jpg'], accept_multiple_files=True)
    #  Process button
    process_button = st.button("Process")

    # =============== Checks section
    # Display uploaded images in sidebar if any
    if user_uploaded_images is not None:
        # Display uploaded images in the sidebar.
        show_uploaded_img_in_sidebar(user_uploaded_images)

    # if user press process button then check for uploaded images
    if process_button:
        # Check if all the required fields are present.
        if teacher_name and unit_title and course_name and week and \
            user_selected_days and number_of_questions_for_assessment and \
                duration_activity:

            updated_intro_table, selected_doc_template = update_intro_table(teacher_name, course_name, unit_title, week)
            # list of table_id_of_lesson_plan_days
            table_id_for_lesson_plan = get_table_id_of_days(user_selected_days, selected_doc_template)

            if updated_intro_table == True:
                st.success("Introduction Updated Successfully")
            else:
                st.error(updated_intro_table)

            if user_uploaded_images:
                with st.spinner('Creating your document...'):
                    gpt_response = handle_images_and_prompts(user_uploaded_images, user_selected_days, 
                                                             number_of_questions_for_assessment, duration_activity)
                    # for debugging - view responses in terminal
                    print(f"{'-'*20}GPT Response Original{'-'*20}\n", type(gpt_response))
                    print(gpt_response)

                    gpt_response = gpt_response.replace("`", "").replace("json", "")

                    # for debugging - view responses in terminal
                    # print(f"{'-'*20}GPT Response Setted{'-'*20}\n", type(gpt_response))
                    # print(gpt_response)
                    
                    # for a_lesson_plan in gpt_response
                    gpt_response_list = json.loads(gpt_response)

                    # for debugging - view responses in terminal
                    # print(f"{'-'*20}GPT Response Finalized{'-'*20}\n", type(gpt_response_list))
                    # print(gpt_response_list)

                with st.spinner('Creating Lesson Plans...'):
                    activities = [day["Activity"] for day in duration_activity.values()]
                    file_ready = update_table_for_lesson_plan(table_id_for_lesson_plan, gpt_response_list, activities)
                with st.spinner('Creating Assessments...'):
                    assessment_ready = update_assessment_and_marking_guide(document_templates()[1], 
                                                                                        gpt_response_list, "assessment")
                with st.spinner('Creating Marking Guides...'):
                    marking_guide_ready = update_assessment_and_marking_guide(document_templates()[2],
                                                                                            gpt_response_list, "answers")
                # Download buttons
                if file_ready == assessment_ready == marking_guide_ready == True:
                    show_download_button(document_templates_names_for_saving[0])
                    show_download_button(document_templates_names_for_saving[1])
                    show_download_button(document_templates_names_for_saving[2])

                else:
                    if file_ready != True:
                        st.error(file_ready)
                    if assessment_ready != True:
                        st.error(assessment_ready)
                    if marking_guide_ready != True:
                        st.error(marking_guide_ready)
            else:
                st.error("Please upload images first then press button", icon="🚨")
        else:
                st.error("All fields are required", icon="🚨")

if __name__ == '__main__':
    main()