import streamlit as st
from main import get_response, save_response, create_epub

st.title("EPUB Creator")

# Inputs
chapter_text = st.text_area('Enter the Chapter text:')
title = st.text_input("Book Title")
author = st.text_input("Author")
chapter_title = st.text_input("Chapter Title")
chapter_number = st.number_input("Chapter Number", min_value=0, step=1)
font_size = st.text_input('Enter the Font Size:')
fonts = [
    'Courier', 'Courier-Bold', 'Courier-BoldOblique', 'Courier-Oblique',
    'Helvetica', 'Helvetica-Bold', 'Helvetica-BoldOblique', 'Helvetica-Oblique',
    'Times-Roman', 'Times-Bold', 'Times-BoldItalic', 'Times-Italic',
    'Symbol', 'ZapfDingbats'
]
font_style = st.selectbox('Select Font Style:', fonts)

# Generate EPUB
if st.button("Create EPUB"):
    if chapter_text and title and author and chapter_title:
        response = get_response(chapter_text, font_size, font_style)
        html_pth = save_response(response)
        output_file = create_epub(html_pth, title, author, chapter_title, chapter_number)
        st.success(f"EPUB created: {output_file}")
        st.download_button("Download EPUB", data=open(output_file, "rb"), file_name=output_file, mime="application/epub+zip")
    else:
        st.error("Please fill in all the fields.")

