def generate_others_page_html(heading, text, font_style, heading_font_size, content_font_size):
    # Create HTML content for the Others Page
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: '{font_style}', sans-serif;
                text-align: left;
                margin: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .others {{
                margin-top: 60px;
                font-size: {content_font_size}px;
                width: 100%;
                max-width: 800px;
                text-align: left;
            }}
            h1 {{
                text-align: center;  /* Centering the heading */
                font-size: {heading_font_size}px;
                width: 100%;
                max-width: 800px;
                margin: 0; /* Remove default margin */
            }}
        </style>
    </head>
    <body>
        <h1>{heading}</h1>
        <div class="others">
            <p>{text}</p>
        </div>
    </body>
    </html>
    """
    return html_content

def save_others_page_html(html_content):
    # Save the generated HTML content to a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as f:
        f.write(html_content)
        return f.name