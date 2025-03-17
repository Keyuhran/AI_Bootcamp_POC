# pages/1_Methodology.py
import streamlit as st
from nav_modules.nav import MenuButtons
from pages.Account import get_roles

st.title("Methodology")
st.subheader("Data Flow Chart")
st.write("The below chart illustrates how infomation is processed within the application framework.")
st.image('data/Data_Flow.png')
MenuButtons(get_roles())
st.subheader("Application Processes")
st.write("The below chart illustrates the core processes of the AI Chatbot application, mainly: \n 1) Retrieve WQ & Regulatory Information \n 2) Generate Responses to Email Queries")
st.image('data/Application_Flow.png')