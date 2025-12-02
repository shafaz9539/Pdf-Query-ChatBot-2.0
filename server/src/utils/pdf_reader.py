import fitz  # PyMuPDF
from ..utils.cleaner import clean_md, detect_headers_footers, remove_headers_footers

def extract_clean_markdown(pdf_path):
    """
    FAST extraction of text from PDF, cleans headers/footers,
    and returns structured pages.
    """

    # 1. Detect headers and footers (uses PyMuPDF anyway)
    headers, footers = detect_headers_footers(pdf_path)
    print(f"Detected {len(headers)} headers, {len(footers)} footers.")

    doc = fitz.open(pdf_path)
    cleaned_pages = []

    # 2. FAST extraction: page.get_text("text")
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract plain text (FAST)
        text = page.get_text("text")  

        # Remove headers/footers
        if headers or footers:
            text = remove_headers_footers(text, headers, footers)
            print(f"Removed headers/footers from page {page_num + 1}.")

        # Optional markdown cleanup if needed
        text = clean_md(text)

        cleaned_pages.append({
            "page_number": page_num + 1,
            "text": text
        })
    
    doc.close()

    print(f"Extracted & cleaned {len(cleaned_pages)} pages.")
    return cleaned_pages
