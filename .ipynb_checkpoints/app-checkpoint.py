import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from main import get_response, save_response, html_to_plain_text_with_newlines, extract_styled_text_with_positions_italics, add_italics_tags, add_bold_tags, extract_styled_text_with_positions_bold
from streamlit_quill import st_quill
import json

# Setup Google Sheets API client using credentials from secrets

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client


# Access the Google Sheet
def get_google_sheet(client, spreadsheet_url):
    sheet = client.open_by_url(spreadsheet_url).sheet1  # Opens the first sheet
    return sheet

# Read the password from the first cell
def read_password_from_sheet(sheet):
    password = sheet.cell(1, 1).value  # Reads the first cell (A1)
    return password

# Update the password in the first cell
def update_password_in_sheet(sheet, new_password):
    sheet.update_cell(1, 1, new_password)  # Updates the first cell (A1) with the new password

# Initialize gspread client and access the sheet
client = get_gspread_client()
sheet = get_google_sheet(client, st.secrets["spreadsheet"])
PASSWORD = read_password_from_sheet(sheet)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'password' not in st.session_state:
    st.session_state['password'] = PASSWORD
if 'reset_mode' not in st.session_state:
    st.session_state['reset_mode'] = False

# Function to check password
def check_password(password):
    return password == st.session_state['password']

# Password reset function
def reset_password(new_password, confirm_password):
    if new_password != confirm_password:
        st.error("Passwords do not match!")
    else:
        st.session_state['password'] = new_password
        update_password_in_sheet(sheet, new_password)
        st.session_state['reset_mode'] = False
        st.success("Password reset successfully!")

# Authentication block
if not st.session_state['authenticated']:
    st.title("Login to HTML Creator")

    password_input = st.text_input("Enter Password", type="password")
    
    if st.button("Login"):
        if check_password(password_input):
            st.session_state['authenticated'] = True
            st.success("Login successful!")
        else:
            st.error("Incorrect password!")

    if st.button("Reset Password?"):
        st.session_state['reset_mode'] = True

# Reset password block
if st.session_state['reset_mode']:
    st.title("Reset Password")

    old_password = st.text_input("Enter Old Password", type="password")
    new_password = st.text_input("Enter New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    if st.button("Reset Password"):
        if old_password == st.session_state['password']:
            reset_password(new_password, confirm_password)
        else:
            st.error("Incorrect old password!")
    
    if st.button("Back to Login"):
        st.session_state['reset_mode'] = False

if st.session_state['authenticated'] and not st.session_state['reset_mode']:
    # Initialize session state variables
    if 'html_created' not in st.session_state:
        st.session_state['html_created'] = False
        st.session_state['html_files'] = []

    st.title("HTML Creator")

    # Sidebar for better layout (optional)
    st.sidebar.header("Book Details")

    # Book Details Inputs
    book_title = st.sidebar.text_input("Book Title", value="My Book Title")
    author = st.sidebar.text_input("Author", value="Author Name")

    # Formatting Options
    fonts = ["Helvetica", "Helvetica-Bold", "Courier", "Times-Roman"]
    font_style = st.sidebar.selectbox('Select Font Style:', fonts)

    # Number of Chapters
    num_chapters = st.number_input('How many chapters do you want to add?', min_value=1, max_value=50, step=1, value=1)

    # Initialize list to store chapter data
    chapters = []

    st.header("Enter Chapter Details")

    for i in range(1, num_chapters + 1):
        with st.expander(f"Chapter {i}"):
            chapter_title = st.text_area(f'Chapter {i} Title:', value=f'Chapter {i}', key=f'chapter_title_{i}')
            raw_data = st_quill(placeholder="Enter your text with formatting", key=f'editor_{i}', html=True)
            chapter_text = html_to_plain_text_with_newlines(raw_data)
            styled_words_italics = extract_styled_text_with_positions_italics(raw_data)
            chapter_text_with_italics = add_italics_tags(chapter_text, styled_words_italics)
            styled_words_bold = extract_styled_text_with_positions_bold(raw_data, chapter_text_with_italics)
            chapter_text_with_styles = add_bold_tags(chapter_text_with_italics, styled_words_bold)
            footnotes = st.checkbox("Contains Footnotes?", value=False,  key=f'footnotes_{i}')
            chapters.append({
                'title': chapter_title,
                'text': chapter_text_with_styles,
                'number': i,
                'footnotes' : footnotes
            })

    # Generate HTML Button
    if st.button("Create HTML"):
        # Validate inputs
        missing_fields = []
        if not book_title:
            missing_fields.append("Book Title")
        for chapter in chapters:
            if not chapter['title']:
                missing_fields.append(f"Title for Chapter {chapter['number']}")
            if not chapter['text']:
                missing_fields.append(f"Text for Chapter {chapter['number']}")

        if missing_fields:
            st.error(f"Please fill in the following fields: {', '.join(missing_fields)}")
        else:
            with st.spinner('Generating HTML...'):
                try:
                    # Clear previous html_files
                    st.session_state['html_files'] = []
                    # Process chapters
                    for chapter in chapters:
                        st.write(f"Processing Chapter {chapter['number']}")
                        response = get_response(chapter['text'], chapter['title'], font_style, chapter['footnotes'])
                        html_pth = save_response(response, chapter['number'])
                        # Read the saved HTML content
                        with open(html_pth, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        # Store the content in session state
                        st.session_state['html_files'].append({
                            'number': chapter['number'],
                            'title': chapter['title'],
                            'content': html_content
                        })
                    # Set the flag to True
                    st.session_state['html_created'] = True
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    # Display download buttons if HTML has been created
    if st.session_state['html_created']:
        st.header("Download Generated HTML Files")
        for file in st.session_state['html_files']:
            # Provide a download button
            st.download_button(
                label=f"Download Chapter {file['number']} HTML",
                data=file['content'],
                file_name=f"{file['number']}.html",
                mime="text/html"
            )
