# title_page.py

import os
from pathlib import Path

def generate_title_page_html(title, subtitle, author, title_font_size, subtitle_font_size, author_font_size, font_style):
    """
    Generates HTML content for the Title Page with inline CSS.

    Parameters:
    - title (str): The main title of the book.
    - subtitle (str): The subtitle of the book.
    - author (str): The author's name.
    - title_font_size (int): Font size for the title.
    - subtitle_font_size (int): Font size for the subtitle.
    - author_font_size (int): Font size for the author's name.
    - font_style (str): Font family to be used.

    Returns:
    - html (str): The generated HTML content for the Title Page.
    """
    html = f"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <title>{title}</title>
    </head>
    <body style="display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: '{font_style}', sans-serif; text-align: center;">
        <div style="text-align: center;">
            <div style="font-size: {title_font_size}px; margin: 0;">{title}</div>
            <div style="font-size: {subtitle_font_size}px; margin: 100px 0 0 0;">{subtitle}</div>
            <div style="font-size: {author_font_size}px; margin: 150px 0 0 0;">{author}</div>
        </div>
    </body>
</html>
"""
    return html

def save_title_page_html(html_content, output_dir='temp_pages', file_name='title_page.xhtml'):
    """
    Saves the Title Page HTML content to a file.

    Parameters:
    - html_content (str): The HTML content to save.
    - output_dir (str): Directory where the HTML file will be saved.
    - file_name (str): Name of the HTML file.

    Returns:
    - file_path (str): The path to the saved HTML file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return file_path
