import streamlit as st
from streamlit import session_state as ss


def HomeNav():
    st.sidebar.page_link("Chatbot.py", label="Chatbot", icon='🤖')

def LoginNav():
    st.sidebar.page_link("pages/account.py", label="Account", icon='🔐')


def Page1Nav():
    st.sidebar.page_link("pages/1_Methodology.py", label="Methodology", icon='🗎')


def Page2Nav():
    st.sidebar.page_link("pages/2_About_Us.py", label="About Us", icon='👋')

def Page3Nav():
    st.sidebar.page_link("pages/3_File_Upload.py", label="File Upload", icon='📂')





def MenuButtons(user_roles=None):
    if user_roles is None:
        user_roles = {}

    if 'authentication_status' not in ss:
        ss.authentication_status = False

    # Always show the relevant navigators.
    LoginNav()
    Page1Nav()
    Page2Nav()


    # Show the other page navigators depending on the users' role.
    if ss["authentication_status"]:

        # (1) Only the admin role can access page 1 and other pages.
        # In a user roles get all the usernames with admin role.
        admins = [k for k, v in user_roles.items() if v == 'admin']

        # Show file upload if the username that logged in is an admin.
        if ss.username in admins:
            Page3Nav()

        # (2) users with user and admin roles have access to chatbot
        HomeNav()   