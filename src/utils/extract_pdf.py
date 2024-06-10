import fitz 

def extract_text_from_pdf(pdf_file: bytes) -> str:
    pdf_document = fitz.open(stream=pdf_file, filetype="pdf")
    
    text = ""

    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
        
    pdf_document.close()

    return text
