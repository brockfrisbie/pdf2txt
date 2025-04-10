from flask import Flask, request, render_template
import requests
import os
import PyPDF2
import re
from io import BytesIO

app = Flask(__name__)

def clean_text(text):
    """Format text for readability by fixing line breaks and spacing."""
    lines = text.split('\n')
    formatted_text = []
    buffer = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            if buffer:
                formatted_text.append(buffer)
                buffer = ""
            continue
        
        if re.match(r"^[A-Z ]+$", line) and len(line) < 50:  # Detect headings
            if buffer:
                formatted_text.append(buffer)
                buffer = ""
            formatted_text.append(f"<h2>{line}</h2>")
            continue
        
        if buffer and not buffer.endswith(tuple(".!?")):
            buffer += " " + line
        else:
            if buffer:
                formatted_text.append(buffer)
            buffer = line
    
    if buffer:
        formatted_text.append(buffer)
    
    return "<p>" + "</p><p>".join(formatted_text) + "</p>"

def extract_text_from_pdf(pdf_bytes):
    try:
        reader = PyPDF2.PdfReader(pdf_bytes)
        raw_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return clean_text(raw_text)
    except Exception as e:
        return f"<p>Error processing the PDF: {e}</p>"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdf_url = request.form.get('pdf_url')
        if pdf_url:
            try:
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    pdf_text = extract_text_from_pdf(BytesIO(response.content))
                    return render_template('result.html', text=pdf_text)
                else:
                    return "<p>Error: Unable to fetch PDF.</p>"
            except Exception as e:
                return f"<p>Error: {e}</p>"
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
