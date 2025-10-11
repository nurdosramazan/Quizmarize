import io
from docx import Document
from PyPDF2 import PdfReader

def parse_pdf(file_buffer: io.BytesIO) -> str:
    """Extracts text from a PDF file buffer."""
    try:
        pdf_reader = PdfReader(file_buffer)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def parse_docx(file_buffer: io.BytesIO) -> str:
    """Extracts text from a DOCX file buffer."""
    try:
        document = Document(file_buffer)
        text = "\n".join([para.text for para in document.paragraphs])
        return text
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""

def parse_content(file_buffer: io.BytesIO, content_type: str) -> str:
    """
    Detects the file type from content_type and calls the appropriate parser.
    """
    if content_type == "application/pdf":
        return parse_pdf(file_buffer)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return parse_docx(file_buffer)
    # Add more parsers here for other types like .pptx, .txt etc.
    else:
        print(f"Unsupported content type: {content_type}")
        return ""