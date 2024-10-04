import os
import streamlit as st
from openai import OpenAI
from lxml import etree
from bs4 import BeautifulSoup
from ebooklib import epub
from title_page import generate_title_page_html, save_title_page_html
from copywright import generate_copyright_page_html, save_copyright_page_html


def get_response(chapter, font_style):
    # Set up OpenAI API client
    api_key = st.secrets["Openai_api"]
    client = OpenAI(
        # This is the default and can be omitted
        api_key = api_key
    )

     # Set up OpenAI model and prompt
    model="gpt-4o-mini-2024-07-18"
    max_chars = 37000
    if len(chapter) <= max_chars:
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
    
    
        Here is the target chapter: <<CHAPTER_TEXT>>
    """
        prompt = prompt_template.replace("<<CHAPTER_TEXT>>", chapter).replace("<<font_style>>", font_style)
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
    
    else:
        # If the chapter exceeds the limit, split into two parts
        split_pos = chapter.rfind('.', 0, max_chars)
        first_part = chapter[:split_pos + 1]
        second_part = chapter[split_pos + 1:]
        prompt_template_1 = """You are an expert book formatter.
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
    
    
        Here is the target chapter: <<CHAPTER_TEXT>> """
        prompt_1 = prompt_template_1.replace("<<CHAPTER_TEXT>>", first_part).replace("<<lineheight>>", line_height_val)

        chat_completion_1 = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_1,
                }
            ],
            model=model,
            temperature=0
        )

        response_1 = chat_completion_1.choices[0].message.content
        prompt_template_2 = """
        You are an expert book formatter.
        Continue formatting the book chapter into HTML following the same styles as before. Do not include the <!DOCTYPE html> declaration, <html>, <head>, or <body> tags. Start directly with the paragraph tags and ensure consistency in formatting with the previous part.
        Line height = <<lineheight>>
        Include these features in html:
        1. Paragraph Formatting
        Indentation: Use a small indent (about 1 em) for the first line of each paragraph, or opt for a larger spacing between paragraphs if not using indentation.
        2. Line Length
        Optimal Line Length: Aim for 50-75 characters per line (including spaces). Lines that are too long or too short can make reading difficult.
        3.Line Spacing (Leading)
        Comfortable Reading: The line spacing should be the same as given in the example.
        4. Proper margins and spaces. The top and Bottom margin for paragraph tag should be 0.1 and 0.2em.
        8. Left and Right margins are minimum so the pdf looks like a book.
        7.  Consistency
        Uniformity: Maintain consistent styles for similar elements (e.g., headings, captions, and block quotes) throughout the book.
        8. format special segments correctly and similarly such as a poetry, quotes or exclamatory expressions etc (use italics ) for them
        9. Use various of html tags like heading bold etc wherever suitable but dont use colours for text
        Keep this in mind : Left and Right margins are minimum.
        10. Do not write anything else like ```html in the response, directly start with the paragraph tags.
        11. No need to bold names and use italics for even single words in sentences that are in other languages like Hindi or spanish.

        Here is the continuation of the chapter:
        <<CHAPTER_TEXT>>
        """
        prompt_2 = prompt_template_2.replace("<<CHAPTER_TEXT>>", second_part).replace("<<fontsize>>", font_size_px).replace("<<lineheight>>", line_height_val)

        chat_completion_2 = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_2,
                }
            ],
            model=model,
            temperature=0
        )

        response_2 = chat_completion_2.choices[0].message.content

        # Now, merge the two responses
        # Extract the <body> content from the first response and append the second response

        # Find the closing </body> and </html> tags in the first response
        body_close_index = response_1.rfind("</body>")
        html_close_index = response_1.rfind("</html>")

        if body_close_index != -1:
            # Insert the second response before the closing </body> tag
            merged_html = response_1[:body_close_index] + "\n" + response_2 + "\n" + response_1[body_close_index:]
        elif html_close_index != -1:
            # Insert before </html> if </body> is not found
            merged_html = response_1[:html_close_index] + "\n" + response_2 + "\n" + response_1[html_close_index:]
        else:
            # If no closing tags are found, simply concatenate
            merged_html = response_1 + "\n" + response_2

        return merged_html

def save_response(response, chapter_number):
    html_pth = f'chapter_{chapter_number}.html'
    with open(html_pth, 'w', encoding='utf-8') as file:
        file.write(response)
    return html_pth

def create_epub(pages, title, author):
    """
    Creates an EPUB book from additional pages and chapters.

    Parameters:
    - pages: List of dictionaries with keys 'title', 'content', and 'number'.
             Additional pages should have 'number' set to 0 or another value to ensure ordering.
    - title: Title of the book.
    - author: Author of the book.

    Returns:
    - output_file_name: The name of the generated EPUB file.
    """
    # Create an EPUB book
    book = epub.EpubBook()

    # Set metadata
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)
    image = epub.EpubImage()
    image.set_content(open("Screenshot (53).png", 'rb').read())
    image.file_name = "images/copywright.png"  # Save with a specific name in EPUB
    book.add_item(image)

    epub_items = []
    toc = []

    # Sort pages based on 'number' to ensure correct order
    sorted_pages = sorted(pages, key=lambda x: x['number'])

    for page in sorted_pages:
        page_title = page['title']
        page_number = page['number']
        html_content = page['content']

        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        if page_number == 0:
            # For additional pages like Title Page, use a specific naming convention
            file_name = f'page_{page_title.replace(" ", "_").lower()}.xhtml'
        else:
            file_name = f'chapter_{page_number}.xhtml'

        # Create an EPUB HTML item
        epub_page = epub.EpubHtml(title=page_title, file_name=file_name, lang='en')
        epub_page.content = str(soup)

        # Add page to the book
        book.add_item(epub_page)
        epub_items.append(epub_page)

        # Add to Table of Contents
        toc.append(epub.Link(file_name, page_title, file_name))

    # Define Table of Contents
    book.toc = tuple(toc)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define Spine
    spine_items = ['nav'] + epub_items
    book.spine = spine_items

    # Write the EPUB file
    output_file_name = f'{title.replace(" ", "_")}.epub'
    epub.write_epub(output_file_name, book, {})
    return output_file_name
    
