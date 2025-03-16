# pages/3_File_Upload.py

import streamlit as st
import os

def main():
    st.title("Upload .msg Outlook Files")
    st.write("Use this page to queue .msg files, and only save them when you press Confirm.")

    # 1) Initialize a queue in session state to hold uploaded files.
    if "queued_files" not in st.session_state:
        st.session_state["queued_files"] = []

    # 2) File uploader can now return a list of UploadedFile objects.
    uploaded_files = st.file_uploader(
        "Upload .msg file(s)", 
        type=["msg"], 
        accept_multiple_files=True
    )

    # 3) Add newly uploaded files into the 'queued_files' list in session state.
    if uploaded_files:
        for f in uploaded_files:
            st.session_state["queued_files"].append(f)

    # 4) Show the current list of queued (unwritten) files.
    if st.session_state["queued_files"]:
        st.write("### Files queued for upload:")
        for f in st.session_state["queued_files"]:
            st.markdown(f"- **{f.name}**")
    else:
        st.write("*No files queued.*")

    # 5) The user presses "Confirm" to finalize saving all queued files to disk.
    if st.button("Confirm", type="primary"):
        if st.session_state["queued_files"]:
            # Use a local relative directory on Streamlit Cloud
            save_dir = "./data/Queries Received and Email Responses"
            os.makedirs(save_dir, exist_ok=True)  # Ensure directory exists

            # Write each file in the queue to the local ephemeral storage
            for f in st.session_state["queued_files"]:
                file_path = os.path.join(save_dir, f.name)
                with open(file_path, "wb") as out_file:
                    out_file.write(f.getbuffer())
            
            st.success(
                f"Uploaded {len(st.session_state['queued_files'])} file(s) to: {save_dir}"
            )
            # Display the current directory contents
            st.write("Current files in directory:", os.listdir(save_dir))
            
            # Clear out the list so they're not uploaded again on next Confirm
            st.session_state["queued_files"] = []
        else:
            st.warning("No files in queue to confirm.")

if __name__ == "__main__":
    main()
