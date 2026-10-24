import base64
import logging
from collections.abc import Sequence
from io import BytesIO

import anthropic
from pydantic import BaseModel
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .config.settings import settings
from .schemas import Mesh, Syllabus, SyllabusResult

# pypdf warns about every odd font or damaged file it meets; we only need its text
logging.getLogger("pypdf").setLevel(logging.ERROR)

MODEL = 'claude-haiku-5-5'
PDF_TYPE = 'application/pdf'
IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}

# Every page sent to Claude costs tokens, so reject oversized syllabi before calling it
MAX_SYLLABUS_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_SYLLABUS_PAGES = 20
SYLLABUS_PAGES_TO_SCAN = 2  # Some syllabi start with a cover page
SYLLABUS_MARKERS = (
    "sílabo", "silabo", "syllabus", "unidad de aprendizaje", "logro",
    "temario", "competencias", "resultados de aprendizaje",
)

MESH_PROMPT = (
    "Extract the career, university, and every cycle with its courses. "
    "Use course names exactly as written in the document. "
    "Only include what appears in the document."
)

SYLLABUS_PROMPT = (
    "First decide whether the document is a course syllabus. "
    "If it is not, set is_syllabus to false and syllabus to null. "
    "If it is, extract the course name, its general learning outcome, and every learning unit with its topics. "
    "Take the topics from each unit's syllabus outline, one per bullet, exactly as written. "
    "A bullet's text can wrap onto several lines; keep it as a single topic until the next bullet starts. "
    "Ignore grading, evaluation percentages, schedule and bibliography. "
    "Only include what appears in the document."
)

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

class ClaudeError(Exception):
    pass

class UnsupportedFileError(Exception):
    pass

class FileTooLargeError(Exception):
    pass

class NotASyllabusError(Exception):
    pass

def looks_like_syllabus(data: bytes, media_type: str) -> bool | None:
    """Free local check before paying for Claude.

    Returns False when the file clearly isn't a syllabus, True when its first pages mention
    syllabus words, and None when it can't tell (images or scanned PDFs without text),
    leaving that decision to Claude.
    """
    if len(data) > MAX_SYLLABUS_BYTES:
        raise FileTooLargeError(f'File is larger than {MAX_SYLLABUS_BYTES // (1024 * 1024)} MB')
    if media_type in IMAGE_TYPES:
        return None  # Images can't be read here
    if media_type != PDF_TYPE:
        raise UnsupportedFileError(f'Unsupported file type: {media_type}')

    if not data.startswith(b'%PDF-'):
        return False  # Claims to be a PDF but isn't one
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted or len(reader.pages) > MAX_SYLLABUS_PAGES:
            return False
        first_pages = reader.pages[:SYLLABUS_PAGES_TO_SCAN]
        text = " ".join(page.extract_text() or "" for page in first_pages).lower()
    except PyPdfError:
        return False  # Damaged or malformed PDF

    if not text.strip():
        return None  # Scanned PDF: no text to search
    return any(marker in text for marker in SYLLABUS_MARKERS)

def build_file_block(data: bytes, media_type: str) -> dict:
    """Turn raw file bytes into the content block Claude expects: 'document' for PDFs, 'image' for pictures."""
    if media_type == PDF_TYPE:
        block_type = 'document'
    elif media_type in IMAGE_TYPES:
        block_type = 'image'
    else:
        raise UnsupportedFileError(f'Unsupported file type: {media_type}')

    encoded = base64.standard_b64encode(data).decode('UTF-8')
    return {
        "type": block_type,
        "source": {"type": "base64", "media_type": media_type, "data": encoded},
    }

async def ask_claude[T: BaseModel](
    prompt: str,
    output_format: type[T],
    files: Sequence[tuple[bytes, str]] = (),
    max_tokens: int = 16000,
) -> T:
    """Send a prompt (plus optional files) to Claude and return its answer validated as output_format."""
    content = [build_file_block(data, media_type) for data, media_type in files]
    content.append({"type": "text", "text": prompt})  # Files go before the instructions

    response = await client.messages.parse(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": content}],
        output_format=output_format,
    )
    if response.stop_reason == "refusal":
        raise ClaudeError("Claude declined the request")
    if response.stop_reason == "max_tokens":
        raise ClaudeError("Response was cut off before finishing")

    if response.parsed_output is None:
        raise ClaudeError("Claude returned no structured output")

    return response.parsed_output

async def processing_file(data: bytes, media_type: str) -> Mesh:
    """Extract the curriculum mesh from an uploaded PDF or image."""
    return await ask_claude(MESH_PROMPT, Mesh, files=[(data, media_type)])

async def processing_syllabus(data: bytes, media_type: str) -> Syllabus:
    """Extract the course outcome and its units with topics from an uploaded syllabus."""
    if looks_like_syllabus(data, media_type) is False:
        raise NotASyllabusError("The file doesn't look like a syllabus")

    result = await ask_claude(SYLLABUS_PROMPT, SyllabusResult, files=[(data, media_type)])
    if not result.is_syllabus or result.syllabus is None:
        raise NotASyllabusError("The file doesn't look like a syllabus")

    return result.syllabus
