import os
import streamlit as st
from openai import OpenAI
from lxml import etree
from bs4 import BeautifulSoup
from ebooklib import epub


def get_response(chapter, font_size, font_style):
    # Set up OpenAI API client
    api_key = st.secrets["Openai_api"]
    client = OpenAI(
        # This is the default and can be omitted
        api_key = api_key
    )

    # Set up OpenAI model and prompt
    model="gpt-4o-mini-2024-07-18"
    
    prompt_template = """

You are an expert book formatter.
This is a book chapter. your job is to output a typesetted file (USING HTML) which can be converted to a epub book. So ensure that this book is formatted beautifully following all rules of formatting books. The book should be able to be read easily in a web browser. Include these features in html:
1. Paragraph Formatting
Indentation: Use a small indent (about 1 em) for the first line of each paragraph, or opt for a larger spacing between paragraphs if not using indentation.
2. Line Length
Optimal Line Length: Aim for 50-75 characters per line (including spaces). Lines that are too long or too short can make reading difficult.
3.Line Spacing (Leading)
Comfortable Reading: Set line spacing (leading) to around 120-145% of the font size. This prevents the text from looking too cramped or too loose.
4. Proper margins and spaces. The top and Bottom margin for paragraph tag should be 0.1 and 0.2em.
8. Left and Right margins are minimum so the pdf looks like a book.
7.  Consistency
Uniformity: Maintain consistent styles for similar elements (e.g., headings, captions, and block quotes) throughout the book.
8. format special segments correctly and similarly such as a poetry, quotes or exclamatory expressions etc (use italics ) for them
9. Use various of html tags like heading bold etc wherever suitable but dont use colours for text
Keep this in mind : Left and Right margins are minimum.
10. Do not write anything else like ```html in the response, directly start with the doctype line.
11. No need to bold names and use italics for even single words in sentences that are in other languages like Hindi or spanish.
12. The chapter heading should be centrally aligned and apply Heading 1 to chapter titles
13. There should be some additional space between the chapter heading and the first paragraph.
14. The font style should be : <<font_style>>
15. The font size should be : <<font_size>>


    Here is the target chapter: <<CHAPTER_TEXT>>
"""
    prompt = prompt_template.replace("<<CHAPTER_TEXT>>", chapter).replace("<<font_size>>", font_size + "px").replace("font_style", font_style)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )

    response = chat_completion.choices[0].message.content
    return response

def save_response(response):
    html_pth = 'neww.html'
    with open(html_pth, 'w', encoding='utf-8') as file:
        file.write(response)
    return html_pth

def create_epub(html_pth, title, author, chapter_title, chapter_number):
    # Load the HTML file
    with open(html_pth, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Create an EPUB book
    book = epub.EpubBook()

    # Set metadata
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)

    # Create an EPUB chapter from HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    chapter_file_name = f'chapter{chapter_number}.xhtml'
    chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_file_name, lang='en')
    chapter.content = str(soup)
    
    # Add chapter to the book
    book.add_item(chapter)
    
    # Define Table of Contents
    book.toc = (epub.Link(chapter_file_name, chapter_title, f'chapter{chapter_number}'),)
    
    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Create spine
    book.spine = ['nav', chapter]
    
    # Write the EPUB file
    output_file_name = f'{title.replace(" ", "_")}.epub'
    epub.write_epub(output_file_name, book, {})
    return output_file_name
    