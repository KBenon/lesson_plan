from docx import Document

# Load template document
template = Document("LESSON_PLAN_TEMPLATE.docx")

def get_table_id_from_template_contain_days():
    """ This function get table_objects of those tables which contain days names
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


print(get_available_days_name())