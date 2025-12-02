import re
import unicodedata
import fitz  # PyMuPDF

def clean_md(md: str):
    md = md.replace("\r\n", "\n")

    # Fix hyphenated line breaks
    md = re.sub(r"(\w+)-\n(\w+)", r"\1\2", md)

    # Remove multiple empty lines
    md = re.sub(r"\n\s*\n\s*\n+", "\n\n", md)

    # Remove trailing spaces
    md = re.sub(r"[ \t]+$", "", md, flags=re.MULTILINE)

    # Remove page numbers
    md = re.sub(r'^_?\d+_?$', '', md, flags=re.MULTILINE)

    # Remove isolated underscores or weird formatting
    md = re.sub(r'^_+$', '', md, flags=re.MULTILINE)

    # Collapse double spaces
    md = re.sub(r" {2,}", " ", md)

    # Normalize unicode
    md = unicodedata.normalize("NFKC", md)

    # Remove CHAPTER/SECTION headers
    md = re.sub(r"^(CHAPTER|Chapter|SECTION|Section)\s+\d+.*$", "", md, flags=re.MULTILINE)

    # Remove bullet symbols
    md = re.sub(r"[•▪‣]", "", md)

    # ------------------------
    # Merge lines into paragraphs
    # ------------------------
    lines = md.split("\n")
    merged = []
    buffer = ""

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if buffer:
                merged.append(buffer.strip())
                buffer = ""
            continue

        if stripped[-1] in ".!?":
            buffer += " " + stripped
            merged.append(buffer.strip())
            buffer = ""
        else:
            buffer += " " + stripped

    if buffer.strip():
        merged.append(buffer.strip())

    md = "\n\n".join(merged)
    return md.strip() + "\n"


def detect_headers_footers(pdf_path, threshold=0.5):
    doc = fitz.open(pdf_path)
    header_counts = {}
    footer_counts = {}

    for page in doc:
        blocks = page.get_text("blocks")
        page_height = page.rect.height

        # Top 12% of page = header zone
        header_zone = page_height * 0.12

        # Bottom 12% of page = footer zone
        footer_zone = page_height * 0.88

        for b in blocks:
            x0, y0, x1, y1, text, *_ = b
            stripped = text.strip()

            if not stripped:
                continue

            # HEADER DETECTION
            if y0 < header_zone:
                header_counts[stripped] = header_counts.get(stripped, 0) + 1

            # FOOTER DETECTION (MULTI-LINE + FLOATING)
            if y1 > footer_zone:
                footer_counts[stripped] = footer_counts.get(stripped, 0) + 1

    total_pages = len(doc)

    headers = {t for t, c in header_counts.items() if c / total_pages >= threshold}
    footers = {t for t, c in footer_counts.items() if c / total_pages >= threshold}

    return headers, footers


def remove_headers_footers(md: str, headers, footers):
    cleaned = []
    for line in md.split("\n"):
        stripped = line.strip()
        if stripped in headers or stripped in footers:
            continue
        cleaned.append(line)

    return "\n".join(cleaned)

