import streamlit as st
from main import create_epub
from main import get_response, save_response 
import tempfile
import os

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
        chapter_title = st.text_input(f'Chapter {i} Title:', value=f'Chapter {i}', key=f'chapter_title_{i}')
        chapter_text = st.text_area(f'Enter the Chapter {i} Text:', height=200, key=f'chapter_text_{i}')
        chapters.append({
            'title': chapter_title,
            'text': chapter_text,
            'number': i
        })

# Generate EPUB Button
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
                    response = get_response(chapter['text'], font_style)
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
            file_name=f"{file['title']}.html",
            mime="text/html"
        )
