from docx import Document

# Load template document
template = Document("LESSON_PLAN_TEMPLATE.docx")

def get_all_data_from_file():
    return Document("LESSON_TEMPLATE.docx")

def get_table_id_of_days(lesson_plan_days):
    """ This function get list  which contain days names
    and return dictionary that contain name of day as a key and table id as a value.
    return:
        dictionary that contain name of day as a key and table id as a value.
        Error_error -  if there is any problem
    """
    # TODO: Need to update doc string
    try:
        list_of_days_table_id = []
        for lesson_plan_day in lesson_plan_days:
            for i in range(0, len(template.tables)):
                if  template.tables[i].rows[0].cells[0].text == lesson_plan_day:
                    list_of_days_table_id.append(template.tables[i])
                    break
        return list_of_days_table_id
    except Exception as e:
        return f"Error_{e}"

def get_table_id_from_template_contain_days():
    """ This function give table_objects of those tables which contain days names
    return:
        list of those table_objects which contain days names
        Error_error -  if there is any problem to get table id from template contain days
    """
    try:
        days_names = ["MONDAY", "TUESDAY", "WEDNESDAY", 
                      "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        tables_id_of_tables_contain_days_name = []
        for i in range(0, len(template.tables)):
            for day in days_names:
                if  str.lower(template.tables[i].rows[0].cells[0].text) == str.lower(day):
                    tables_id_of_tables_contain_days_name.append(template.tables[i])
                    break
        return tables_id_of_tables_contain_days_name
    except Exception as e:
        return f"Error_{e}"

def get_available_days_name():
    """ This function get days name which are available in provided template
    return:
        list of days available in template
        Error_error -  if there is any problem to get names of days from template
    """
    try:
        days_available_in_template = []
        for table_id in get_table_id_from_template_contain_days():
            days_available_in_template.append(table_id.rows[0].cells[0].text)
        return days_available_in_template
    except Exception as e:
        return f"Error_{e}"

def update_intro_table(teacher_name, course, unit_title, week):
    """This function will update template of first table which is introduction table
    parameters (required):
        - teacher_name, course, unit and title, week
    return:
        True - if table updated successfully
        Error_error -  if table is not updated for any reason
    """
    try:
        # First table about Introduction
        intro_table = template.tables[0]
        intro_table.rows[0].cells[1].text = teacher_name
        intro_table.rows[0].cells[3].text = course
        intro_table.rows[1].cells[1].text = unit_title
        intro_table.rows[1].cells[3].text = week
        save_document()
        return True
    except Exception as e:
        return f"Error_{e}"

def update_table_for_lesson_plan(list_of_table_id, list_of_gpt_response):
    """
    parameters: 
        table_id (required): object id of table in which user want to update
        data (required): data should be in json format
    """
    # TODO: need to update doc string
    try:
        # Table of key concept and update it's value
        terminology = ""
        for index_number, table_id in enumerate(list_of_table_id):
            # list_of_gpt_response is a list of dictionaries
            # Check if index_number is within the range of list_of_gpt_response
            if index_number < len(list_of_gpt_response):
                terminology += list_of_gpt_response[index_number]["terminology"]+"\n"

                # table_id has rows and cells structure
                table_id.rows[1].cells[1].text = list_of_gpt_response[index_number]["aims_and_objective"]
                table_id.rows[2].cells[1].text = list_of_gpt_response[index_number]["introduction"]
                table_id.rows[3].cells[1].text = list_of_gpt_response[index_number]["lesson_body"]
                table_id.rows[4].cells[1].text = list_of_gpt_response[index_number]["conclusion"]

        # Update key concept and terminology table
        template.tables[1].rows[1].cells[0].text = terminology

        # Save the document
        return save_document()
    except Exception as e:
        return f"Error_{e}"

def save_document(name_of_document="LESSON_TEMPLATE"):
    """This function will save document
    parameters (optional):
        - name_of_document (default name of saved document is LESSON_PLAN_TEMPLATE)
    return:
        True - if document saved successfully
        Error_error -  if table is not updated for any reason
    """
    try:
        template.save(f"{name_of_document}.docx")
        return True
    except Exception as e:
        return f"Error_{e}"
