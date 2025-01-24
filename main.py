import os
import streamlit as st
from openai import OpenAI
from lxml import etree
from bs4 import BeautifulSoup
from ebooklib import epub


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
    12. The chapter heading should be centrally aligned and apply Heading 1 to chapter titles.
    13. The chapter heading can be anything like just a number and can also include just special characters like Chapter ^. 
    14. Do not make any changes to the provided chapter heading and use the heading as it is given only. Do not write the word chapter before the heading if it is not given. Here is the chapter title which can also have the chapter subtitle sometimes so format accordingly. <<title>>
    15. There should be some additional space between the chapter heading and the first paragraph.
    16. The font style should be : <<font_style>>
    17. The chapter can also be a collection of poems. For these format the lines accordingly so that each line ends in the original way and the next line starts after that. Start a new poem from a new page. Each poem will have a seperate subheading apart from the name of the chapter, so use Heading 3 for them. If the heading is not given do not randomly insert headings like 'poem 1' or 'poem section'.
    18. When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
    19. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.
    
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
    
    elif(len(chapter) > max_chars and len(chapter) <= 74000):
        # If the chapter exceeds the limit, split into two parts
        split_pos = chapter.rfind('.', 0, max_chars)
        first_part = chapter[:split_pos + 1]
        second_part = chapter[split_pos + 1:]
        prompt_template_1 = """
    
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
    12. The chapter heading should be centrally aligned and apply Heading 1 to chapter titles.
    13. The chapter heading can be anything like just a number and can also include just special characters like Chapter ^. 
    14. Do not make any changes to the provided chapter heading and use the heading as it is given only. Do not write the word chapter before the heading if it is not given. Here is the chapter title which can also have the chapter subtitle sometimes so format accordingly. <<title>>
    15. There should be some additional space between the chapter heading and the first paragraph.
    16. The font style should be : <<font_style>>
    17. The chapter can also be a collection of poems. For these format the lines accordingly so that each line ends in the original way and the next line starts after that. Start a new poem from a new page. Each poem will have a seperate subheading apart from the name of the chapter, so use Heading 3 for them. If the heading is not given do not randomly insert headings like 'poem 1' or 'poem section'.
    18.When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
    19. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.
    
        Here is the target chapter: <<CHAPTER_TEXT>>
    """
        prompt_1 = prompt_template_1.replace("<<CHAPTER_TEXT>>", first_part).replace("<<font_style>>", font_style)

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
        Continue formatting the book chapter into HTML following the same styles as before. Do not include the <!DOCTYPE html> declaration, <html>,     <head>, or <body> tags. Start directly with the paragraph tags and ensure consistency in formatting with the previous part.
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
        12. The font style should be : <<font_style>>
        13. When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
        14. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.
        
        Here is the continuation of the chapter:
        <<CHAPTER_TEXT>>
        """
        prompt_2 = prompt_template_2.replace("<<CHAPTER_TEXT>>", second_part).replace("<<font_style>>", font_style)

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
    
    elif(len(chapter) > 74000 and len(chapter) <= 111000):
        # If the chapter exceeds the limit, split into two parts
        split_pos_1 = chapter.rfind('.', 0, max_chars)
        split_pos_2 = chapter.rfind('.', max_chars, 74000)
        first_part = chapter[:split_pos_1 + 1]
        second_part = chapter[split_pos_1 + 1 : split_pos_2 + 1]
        third_part = chapter[split_pos_2 + 1:]
        prompt_template_1 = """
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
    12. The chapter heading should be centrally aligned and apply Heading 1 to chapter titles.
    13. The chapter heading can be anything like just a number and can also include just special characters like Chapter ^. 
    14. Do not make any changes to the provided chapter heading and use the heading as it is given only. Do not write the word chapter before the heading if it is not given. Here is the chapter title which can also have the chapter subtitle sometimes so format accordingly. <<title>>
    15. There should be some additional space between the chapter heading and the first paragraph.
    16. The font style should be : <<font_style>>
    17. The chapter can also be a collection of poems. For these format the lines accordingly so that each line ends in the original way and the next line starts after that. Start a new poem from a new page. Each poem will have a seperate subheading apart from the name of the chapter, so use Heading 3 for them. If the heading is not given do not randomly insert headings like 'poem 1' or 'poem section'.
    18. When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
    19. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.
    
        Here is the target chapter: <<CHAPTER_TEXT>> """
        prompt_1 = prompt_template_1.replace("<<CHAPTER_TEXT>>", first_part).replace("<<font_style>>", font_style)

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
        Continue formatting the book chapter into HTML following the same styles as before. Do not include the <!DOCTYPE html> declaration, <html>,     <head>, or <body> tags. Start directly with the paragraph tags and ensure consistency in formatting with the previous part.
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
        12. The font style should be : <<font_style>>
        13. When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
        14. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.
        
        Here is the continuation of the chapter:
        <<CHAPTER_TEXT>>
        """
        prompt_2 = prompt_template_2.replace("<<CHAPTER_TEXT>>", second_part).replace("<<font_style>>", font_style)

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
        
        prompt_template_3 = """
        You are an expert book formatter.
        Continue formatting the book chapter into HTML following the same styles as before. Do not include the <!DOCTYPE html> declaration, <html>,     <head>, or <body> tags. Start directly with the paragraph tags and ensure consistency in formatting with the previous part.
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
        12. The font style should be : <<font_style>>
        13. When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
        14. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.
        
        Here is the continuation of the chapter:
        <<CHAPTER_TEXT>>
        """
        prompt_3 = prompt_template_3.replace("<<CHAPTER_TEXT>>", second_part).replace("<<font_style>>", font_style)

        chat_completion_3 = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_3,
                }
            ],
            model=model,
            temperature=0
        )

        response_3 = chat_completion_3.choices[0].message.content

        # Now, merge the two responses
        # Extract the <body> content from the first response and append the second response

        # Find the closing </body> and </html> tags in the first response
        body_close_index = response_1.rfind("</body>")
        html_close_index = response_1.rfind("</html>")

        if body_close_index != -1:
            merged_html = response_1[:body_close_index] + "\n" + response_2 + "\n" + response_3 + "\n" + response_1[body_close_index:]
        elif html_close_index != -1:
            merged_html = response_1[:html_close_index] + "\n" + response_2 + "\n" + response_3 + "\n" + response_1[html_close_index:]
        else:
            merged_html = response_1 + "\n" + response_2 + "\n" + response_3
            
        return merged_html
    
    else:
        # If the chapter exceeds the limit, split into two parts
        split_pos_1 = chapter.rfind('.', 0, max_chars)
        split_pos_2 = chapter.rfind('.', max_chars, 74000)
        split_pos_3 = chapter.rfind('.', 74000, 111000)
        first_part = chapter[:split_pos_1 + 1]
        second_part = chapter[split_pos_1 + 1 : split_pos_2 + 1]
        third_part = chapter[split_pos_2 + 1 : split_pos_3 + 1]
        fourth_part = chapter[split_pos_3 + 1:]
        prompt_template_1 = """
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
    12. The chapter heading should be centrally aligned and apply Heading 1 to chapter titles.
    13. The chapter heading can be anything like just a number and can also include just special characters like Chapter ^. 
    14. Do not make any changes to the provided chapter heading and use the heading as it is given only. Do not write the word chapter before the heading if it is not given. Here is the chapter title which can also have the chapter subtitle sometimes so format accordingly. <<title>>
    15. There should be some additional space between the chapter heading and the first paragraph.
    16. The font style should be : <<font_style>>
    17. The chapter can also be a collection of poems. For these format the lines accordingly so that each line ends in the original way and the next line starts after that. Start a new poem from a new page. Each poem will have a seperate subheading apart from the name of the chapter, so use Heading 3 for them. If the heading is not given do not randomly insert headings like 'poem 1' or 'poem section'.
    18. When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
    19. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.
    
        Here is the target chapter: <<CHAPTER_TEXT>> """
        prompt_1 = prompt_template_1.replace("<<CHAPTER_TEXT>>", first_part).replace("<<font_style>>", font_style)

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
        Continue formatting the book chapter into HTML following the same styles as before. Do not include the <!DOCTYPE html> declaration, <html>,     <head>, or <body> tags. Start directly with the paragraph tags and ensure consistency in formatting with the previous part.
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
        12. The font style should be : <<font_style>>
        13. When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
        14. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.
        
        Here is the continuation of the chapter:
        <<CHAPTER_TEXT>>
        """
        prompt_2 = prompt_template_2.replace("<<CHAPTER_TEXT>>", second_part).replace("<<font_style>>", font_style)

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
        
        prompt_template_3 = """
        You are an expert book formatter.
        Continue formatting the book chapter into HTML following the same styles as before. Do not include the <!DOCTYPE html> declaration, <html>,     <head>, or <body> tags. Start directly with the paragraph tags and ensure consistency in formatting with the previous part.
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
        12. The font style should be : <<font_style>>
        13. When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
        14. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.
        
        Here is the continuation of the chapter:
        <<CHAPTER_TEXT>>
        """
        prompt_3 = prompt_template_3.replace("<<CHAPTER_TEXT>>", third_part).replace("<<font_style>>", font_style)

        chat_completion_3 = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_3,
                }
            ],
            model=model,
            temperature=0
        )

        response_3 = chat_completion_3.choices[0].message.content

        prompt_template_4 = """
        You are an expert book formatter.
        Continue formatting the book chapter into HTML following the same styles as before. Do not include the <!DOCTYPE html> declaration, <html>,     <head>, or <body> tags. Start directly with the paragraph tags and ensure consistency in formatting with the previous part.
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
        12. The font style should be : <<font_style>>
        13. When the text contains footnotes, include a superscript reference in the paragraph (e.g., `<sup><a href="#fn1">1</a></sup>`). At the end of the chapter, add a `div` with a class of `footnotes` that lists the footnotes using an ordered list (`<ol>`). Use the `id` attribute to link the superscripts in the text to the corresponding footnotes. Each footnote should include a backlink (`<a href="#fnref1">↩</a>`) to the reference in the text. It is not necessary that the text always contains footnotes. Use this only when needed and not everytime.
        14. In the text italicize whatever text you find in between these tags <Italics> </Italics> and bold whatever text you find in between these tags <Bold> </Bold> by adding the <i> and <b> tags of html.

        Here is the continuation of the chapter:
        <<CHAPTER_TEXT>>
        """
        prompt_4 = prompt_template_4.replace("<<CHAPTER_TEXT>>", fourth_part).replace("<<font_style>>", font_style)

        chat_completion_4 = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_4,
                }
            ],
            model=model,
            temperature=0
        )

        response_4 = chat_completion_4.choices[0].message.content

        # Now, merge the four responses
        # Extract the <body> content from the first response and append the second response

        # Find the closing </body> and </html> tags in the first response
        body_close_index = response_1.rfind("</body>")
        html_close_index = response_1.rfind("</html>")

        if body_close_index != -1:
            merged_html = (response_1[:body_close_index] + "\n" + response_2 + "\n" + response_3 + "\n" + response_4 + "\n" + response_1[body_close_index:])
        elif html_close_index != -1:
            merged_html = (response_1[:html_close_index] + "\n" + response_2 + "\n" + response_3 + "\n" + response_4 + "\n" + response_1[html_close_index:])
        else:
            merged_html = response_1 + "\n" + response_2 + "\n" + response_3 + "\n" + response_4
        return merged_html

def save_response(response, chapter_number):
    html_pth = f'chapter_{chapter_number}.html'
    with open(html_pth, 'w', encoding='utf-8') as file:
        file.write(response)
    return html_pth



def extract_styled_text_with_positions(html):
    """
    Extract styled text (italicized <em> and bold <strong>) from the HTML along with their positions.
    Returns a list of dictionaries containing the text, style, and its start and end positions.
    """
    soup = BeautifulSoup(html, "html.parser")
    plain_text = html_to_plain_text_with_newlines(html)
    styled_text_positions = []

    # Extract italicized text
    for em in soup.find_all("em"):
        italic_text = em.get_text()
        start_idx = plain_text.find(italic_text)
        while start_idx != -1:
            match_plain = plain_text[start_idx:start_idx + len(italic_text)]
            if match_plain == italic_text:
                styled_text_positions.append({
                    "text": italic_text,
                    "style": "Italics",
                    "start": start_idx,
                    "end": start_idx + len(italic_text)
                })
                break
            start_idx = plain_text.find(italic_text, start_idx + 1)
    
    # Extract bold text
    for strong in soup.find_all("strong"):
        bold_text = strong.get_text()
        start_idx = plain_text.find(bold_text)
        while start_idx != -1:
            match_plain = plain_text[start_idx:start_idx + len(bold_text)]
            if match_plain == bold_text:
                styled_text_positions.append({
                    "text": bold_text,
                    "style": "Bold",
                    "start": start_idx,
                    "end": start_idx + len(bold_text)
                })
                break
            start_idx = plain_text.find(bold_text, start_idx + 1)
    
    # Sort by start position to ensure correct processing order
    styled_text_positions.sort(key=lambda x: x['start'])
    return styled_text_positions
    

def html_to_plain_text_with_newlines(html):
        """
        Convert HTML to plain text while preserving new paragraphs as line breaks.
        """
        soup = BeautifulSoup(html, "html.parser")
        lines = []
        for paragraph in soup.find_all("p"):  # Find all paragraph tags
            lines.append(paragraph.get_text())  # Extract text from each paragraph
        return "\n".join(lines)


def add_styled_tags(chapter_text, styled_words):
    """
    Add <Italics> and <Bold> tags before and after the respective styled text in the chapter_text.
    """
    offset = 0  # To account for the changing positions due to added tags
    for word in styled_words:
        start = word['start'] + offset
        end = word['end'] + offset
        if word['style'] == "Italics":
            chapter_text = (
                chapter_text[:start] + "<Italics>" +
                chapter_text[start:end] + "</Italics>" +
                chapter_text[end:]
            )
            offset += len("<Italics></Italics>")
        elif word['style'] == "Bold":
            chapter_text = (
                chapter_text[:start] + "<Bold>" +
                chapter_text[start:end] + "</Bold>" +
                chapter_text[end:]
            )
            offset += len("<Bold></Bold>")
    return chapter_text
