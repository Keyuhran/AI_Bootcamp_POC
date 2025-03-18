# pages/3_File_Upload.py

import streamlit as st
from streamlit import session_state as ss
from nav_modules.nav import MenuButtons
from pages.Account import get_roles
import os

def main():
    if 'authentication_status' not in ss:
        st.switch_page('./pages/Account.py')

    if ss.authentication_status:
        st.write('This content is only accessible for admins.')
    else:
        st.write('Please log in on login page.')

    MenuButtons(get_roles())

    st.title("Upload .msg Outlook Files")
    st.write("Use this page to queue .msg files, and only save them when you press Confirm.")

    if "queued_files" not in st.session_state:
        st.session_state["queued_files"] = []

    uploaded_files = st.file_uploader(
        "Upload .msg file(s)", 
        type=["msg"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        for f in uploaded_files:
            if f.name not in [existing_file.name for existing_file in st.session_state["queued_files"]]:
                st.session_state["queued_files"].append(f)

    if st.session_state["queued_files"]:
        st.write("### Files queued for upload:")
        for f in st.session_state["queued_files"]:
            st.markdown(f"- **{f.name}**")
    else:
        st.write("*No files queued.*")

    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("Confirm", type="primary"):
            if st.session_state["queued_files"]:
                save_dir = "./data/Queries Received and Email Responses"
                os.makedirs(save_dir, exist_ok=True)

                for f in st.session_state["queued_files"]:
                    file_path = os.path.join(save_dir, f.name)
                    with open(file_path, "wb") as out_file:
                        out_file.write(f.getbuffer())

                st.success(
                    f"Uploaded {len(st.session_state['queued_files'])} file(s) to: {save_dir}"
                )
                st.write("Current files in directory:", os.listdir(save_dir))

                st.session_state["queued_files"] = []
            else:
                st.warning("No files in queue to confirm.")

    with col2:
        if st.button("Clear Queue"):
            st.session_state["queued_files"] = []
            st.info("Upload queue cleared.")

if __name__ == "__main__":
    main()
