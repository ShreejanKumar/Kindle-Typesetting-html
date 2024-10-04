def generate_copyright_page_html(author_name, typesetter_name, printer_name):
    # Create HTML content for the Copyright Page
    html_content = f"""
<html>
<head>
    <style>
        body {{
            font-family: 'Helvetica', sans-serif;
            text-align: center;
        }}
        .copyright {{
            margin: 20px;
        }}
        .logo {{
            width: 200px;  /* Increase width */
            height: auto;  /* Maintain aspect ratio */
        }}
    </style>
</head>
<body>
    <div class="copyright">
        <img src="images/copywright.png" alt="Logo" class="logo"/><br/>
        <p>Copyright © {author_name} 2023</p>
        <p>The moral rights of the author have been asserted. Database right NU VOICE PRESS (maker).</p>
        <p>This is a work of fiction, and all characters and incidents described in this book are the product of the author's imagination. Any resemblance to actual persons, living or dead, is entirely coincidental.</p>
        <p>All rights reserved. Enquiries concerning reproduction outside the scope of the above should be sent to NU VOICE PRESS at the address above.</p>
        <p>ISBN: 978-81-963184-7-5</p>
        <p>Typeset by {typesetter_name}, Noida</p>
        <p>Printed at {printer_name}</p>
        <p>Published by Nu Voice Press</p>
    </div>
</body>
</html>
"""

    return html_content

def save_copyright_page_html(html_content):
    # Save the generated HTML content to a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as f:
        f.write(html_content)
        return f.name
