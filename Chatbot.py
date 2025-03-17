# main file to be run by streamlit.
# Set up and run this Streamlit App
#__import__('pysqlite3')
import sys
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from streamlit import session_state as ss
from modules.nav import MenuButtons
from pages.account import get_roles
from helper_functions.utility import text_import, email_msg_import, check_password
from logics.email_query_handler import full_workflow
import io
import email


# If the user reloads or refreshes the page while still logged in,
# go to the account page to restore the login status. Note reloading
# the page changes the session id and previous state values are lost.
# What we are doing is only to relogin the user.
if 'authentication_status' not in ss:
    st.switch_page('./pages/account.py')

MenuButtons(get_roles())
st.header('Home page')

# Protected content in home page.
if ss.authentication_status:
    st.write('This content is only accessible for logged in users.')
else:
    st.write('Please log in on login page.')
    
# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="My Streamlit App"
)
# endregion <--------- Streamlit App Configuration --------->

# Do not continue if check_password is not True.  
if not check_password():  
    st.stop()

## WHAT IS SHOWN ON THE APP STARTS FROM HERE!!!!

# Initialize the session state for page navigation and inputs
if 'page' not in st.session_state:
    st.session_state.page = 'input'

if 'response' not in st.session_state:
    st.session_state.response = None

if 'name_input' not in st.session_state:
    st.session_state.name_input = '[Officer Name]'

if 'designation_input' not in st.session_state:
    st.session_state.designation_input = '[Designation]'

if st.session_state.page == 'input':
    # st.image("data/Information_page/PUB_logo.png")
    # st.logo("data/Information_page/PUB_logo.png")
    st.title("Ask Your Question Here!")
    st.sidebar.title("Welcome to Water Quality Chatbot!")
    with st.expander('Click to see disclaimer'):
        st.write('''
        IMPORTANT NOTICE: This web application is developed as a proof-of-concept prototype. The information provided here is NOT intended for actual usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.
        
        Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.
        
        Always consult with qualified professionals for accurate and personalized advice.
        ''')

    name_input = st.text_input("Please enter name for email sign-off")
    designation_input = st.text_input("Please enter designation for email sign-off")

    if name_input:
        st.session_state.name_input = name_input

    if designation_input:
        st.session_state.designation_input = designation_input

    input_method = st.radio("Choose input method: ", ("Text Input", "Email Upload (.msg file):"))

    # Define a function to handle generating response on button click or file upload
    def generate_response(content): 
        # function is only triggered when the submit button or the email file is uploaded. 
        public_query, email_elements = content
        st.session_state.public_query = public_query
        st.session_state.email_elements = email_elements
        with st.spinner("Generating response..."):
            st.session_state.response = full_workflow(st.session_state.public_query,st.session_state.email_elements)
        st.session_state.page = 'output'
        st.rerun()

    # Text Input Method
    if input_method == "Text Input":
        text_input = st.text_area("Paste the content of the email below.", height=300)
        
        # Only trigger full_workflow if the Submit button is clicked and input is provided
        if st.button('Submit', type="primary"):
            if text_input:
                generate_response(text_import(text_input))
            else:
                st.warning("Please provide an input before submitting")

    # Email Upload Method
    else:
        email_input = st.file_uploader('Please upload an email message to submit')
        
        # Trigger full_workflow as soon as an email is uploaded
        if email_input is not None:
            generate_response(email_msg_import(email_input))


elif st.session_state.page == 'output':
    st.title("Email Content and Response")
    
    st.subheader("Generated Response:")
    st.write('To: ',st.session_state.email_elements.get('From'))
    st.write('CC: ',st.session_state.email_elements.get('CC'))
    st.write(st.session_state.response)
    st.write(st.session_state.name_input)
    st.write(st.session_state.designation_input)
    
    st.subheader("Original Email Content:")
    st.write(st.session_state.public_query)
  
    if st.button('Back to Input'):
        st.session_state.name_input = '[Officer Name]'
        st.session_state.designation_input = '[Designation]'
        st.session_state.page = 'input'
        st.session_state.response = None  # Clear the response
        st.rerun()
