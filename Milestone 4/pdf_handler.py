import pypdf

def extract_text(pdf_path):
    text = ""
    try:
        # Open the PDF file in binary read mode
        reader = pypdf.PdfReader(pdf_path)
        
        # Iterate over every page and extract text
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
                
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""
        
    return text