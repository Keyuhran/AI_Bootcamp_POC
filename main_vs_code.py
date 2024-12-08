from helper_functions.utility import text_import_vs
from logics.email_query_handler import full_workflow

# enter prompt into the space below.
input_prompt = """
Please provide the safe guideline limit for fluoride in drinking water
"""

llm_input = text_import_vs(input_prompt)  # use the text_import_vs, text_import has streamlit elements in it.
public_query, email_elements = llm_input # tuple unpacking for output of text_import_vs
response = full_workflow(public_query, email_elements)
print(response)