import streamlit as st  
import hmac  
import extract_msg
import email
import io
import hashlib
import aiofiles.os


# """  
# This file contains the common components used in the Streamlit App.  
# This includes the sidebar, the title, the footer, and the password check.  
# """  

def check_password():  
    """Returns `True` if the user had the correct password."""  
    def password_entered():  
        """Checks whether a password entered by the user is correct."""  
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):  
            st.session_state["password_correct"] = True  
            del st.session_state["password"]  # Don't store the password.  
        else:  
            st.session_state["password_correct"] = False  
    # Return True if the passward is validated.  
    if st.session_state.get("password_correct", False):  
        return True  
    # Show input for password.  
    st.text_input(  
        "Password", type="password", on_change=password_entered, key="password"  
    )  
    if "password_correct" in st.session_state:  
        st.error("😕 Password incorrect")  
    return False

def print_header_if_exists(msg, header):
    if header in msg:
        st.write(f'{header}: {msg[header]}')

def text_import(text_input):
    input_msg = email.message_from_string(text_input)

    email_elements = {
        'Subject': input_msg.get('Subject', 'N/A'),
        'From': input_msg.get('From', 'N/A'),
        'To': input_msg.get('To', 'N/A'),
        'CC': input_msg.get('CC', 'N/A'),
        'Date': input_msg.get('Date', 'N/A')
    }

    print_header_if_exists(input_msg, 'Subject')
    print_header_if_exists(input_msg, 'From')
    print_header_if_exists(input_msg, 'To')
    print_header_if_exists(input_msg, 'CC')
    print_header_if_exists(input_msg, 'Date')

    st.write("Body")
    if input_msg.is_multipart():
        for part in input_msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode()
                st.text(body)
    else:
        body = input_msg.get_payload(decode=True).decode()
        st.write(body)
    
    # Extract email body for input into the LLM. 
    return body, email_elements

def text_import_vs(text_input):
    input_msg = email.message_from_string(text_input)

    email_elements = {
        'Subject': input_msg.get('Subject', 'N/A'),
        'From': input_msg.get('From', 'N/A'),
        'To': input_msg.get('To', 'N/A'),
        'CC': input_msg.get('CC', 'N/A'),
        'Date': input_msg.get('Date', 'N/A')
    }

    print_header_if_exists(input_msg, 'Subject')
    print_header_if_exists(input_msg, 'From')
    print_header_if_exists(input_msg, 'To')
    print_header_if_exists(input_msg, 'CC')
    print_header_if_exists(input_msg, 'Date')

    body = input_msg.get_payload(decode=True).decode()
  
    # Extract email body for input into the LLM. 
    return body, email_elements


def email_msg_import(raw_msg):
    # reading the file
    raw_data = raw_msg.read()

    # parsing the message file
    msg_file = extract_msg.Message(io.BytesIO(raw_data))

    email_elements = {
        'Subject': msg_file.subject,
        'From': msg_file.sender,
        'To': msg_file.to,
        'CC': msg_file.cc,
        'Date': msg_file.date
    }

    st.write(f'Subject: {msg_file.subject}')
    st.write(f'From: {msg_file.sender}')
    st.write(f'To: {msg_file.to}')
    st.write(f'CC: {msg_file.cc}')
    st.write(f'Date: {msg_file.date}')

    st.write("Body")
    st.write(f'Body: {msg_file.body}')
    
    body = msg_file.body
    msg_file.close()

    # Extract email body for input into the LLM.
    return body, email_elements

def generate_checksum(query):
    return hashlib.md5(query.encode()).hexdigest()[:8]

async def async_os_path_exists(path):
    return await aiofiles.os.path.exists(path)