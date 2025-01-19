import streamlit as st
import os
import re  # For sanitizing filenames
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

# Set wide layout for the page
st.set_page_config(layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .title {
        font-size: 50px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
    }
    .subtitle {
        font-size: 30px;
        color: #3498db;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        color: #2C3E50;
        margin-bottom: 10px;
        text-align: center;
    }
    .upload-label {
        font-size: 16px;
        color: #2C3E50;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5em 1.5em;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# Selenium setup
prefs = {"profile.default_content_settings.popups": 0,
         "download.prompt_for_download": False,
         "directory_upgrade": True,
         "safebrowsing.enabled": False}

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(2)

# Function to scrape the website
def FindDoc(TENDER_ID: str):
    URL = 'https://hptenders.gov.in/nicgep/app'
    driver.get(URL)
    driver.find_element(By.ID, 'SearchDescription').send_keys(TENDER_ID)
    driver.find_element(By.ID, 'Go').click()
    driver.find_element(By.ID, 'DirectLink_0').click()
    table = driver.find_element(By.ID, 'packetTableView')
    rows = table.find_elements(By.TAG_NAME, "tr")

    table_data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        cols_data = [col.text for col in cols]
        table_data.append(cols_data)

    table_data.remove(table_data[0])  # Remove header
    DATA = {}
    j = 1
    for col in table_data:
        if col[0] == str(j):
            curr_type = col[1]
            DATA[col[1]] = [[col[2], col[3]]]
            j += 1
        else:
            DATA[curr_type].append([col[2], col[3]])

    driver.quit()
    return DATA

# Function to sanitize the filename
def sanitize_filename(filename):
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return sanitized.replace(' ', '_')

# Function to save file locally
def save_file_locally(tender_id, file, file_name, cover_type, clientID, file_extension):
    try:
        sanitized_file_name = sanitize_filename(file_name)
        save_dir = os.path.join('results', f'{clientID}_{tender_id}', sanitize_filename(cover_type))
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"{sanitized_file_name}{file_extension.lower()}")
        with open(file_path, 'wb') as f:
            f.write(file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file {file_name}: {str(e)}")
        return None

# Streamlit app design
st.markdown('<div class="title">Tender Filing By VYVSAI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Secured and Fast Tender Filing Service</div>', unsafe_allow_html=True)

# Step 1: Input Tender ID
client_id = st.text_input('Client ID : ')
tender_id = st.text_input("Enter the Tender ID : ")

if tender_id:
    # Step 2: Fetch document requirements
    with st.spinner(f"Fetching document requirements for Tender ID: {tender_id}..."):
        required_documents = FindDoc(tender_id)

    if required_documents:
        st.success(f"Found {len(required_documents)} cover types with document requirements for Tender ID: {tender_id}")

        uploaded_files = {}

        # Step 3: Display document requirements
        for cover_type, documents in required_documents.items():
            st.markdown(f'<div class="section-title">{cover_type}</div>', unsafe_allow_html=True)

            if len(documents) > 1:
                cols = st.columns(2)
                for i, doc in enumerate(documents):
                    doc_name = doc[0]
                    doc_format = doc[1].replace('.', '')  # Remove dot from format
                    with cols[i % 2]:
                        st.file_uploader(f"{doc_name}", type=doc_format.lower(), label_visibility="visible")
            else:
                doc_name = documents[0][0]
                doc_format = documents[0][1].replace('.', '')
                st.markdown(f'<div class="upload-label">{doc_name}</div>', unsafe_allow_html=True)
                st.file_uploader(f"Upload {doc_name}", type=doc_format.lower(), label_visibility="visible")

        # Step 4: Submit the uploaded documents
        if st.button("Submit Tender Documents"):
            missing_files = [doc_name for (cover_type, doc_name, doc_format), file in uploaded_files.items() if file is None]

            if missing_files:
                st.error(f"Please upload the following missing documents: {', '.join(missing_files)}")
            else:
                st.toast("All documents uploaded successfully! Saving files locally...", icon="✅", duration=10)

                for (cover_type, doc_name, doc_format), file in uploaded_files.items():
                    file_path = save_file_locally(tender_id, file, doc_name, cover_type, client_id, '.' + doc_format.lower())
                    if file_path is None:
                        st.error(f"Failed to save {doc_name}")

                st.toast(f"Tender submission initiated for Client with ID {client_id}, Tender ID {tender_id}. Our team will contact you soon for further information.", icon="✅", duration=15)
    else:
        st.error(f"No document requirements found for Tender ID: {tender_id}.")
