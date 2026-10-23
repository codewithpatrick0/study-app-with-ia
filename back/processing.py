import base64
from collections.abc import Sequence

import anthropic
from pydantic import BaseModel

from .config.settings import settings
from .schemas import Mesh

MODEL = 'claude-haiku-5-5'
PDF_TYPE = 'application/pdf'
IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}

MESH_PROMPT = (
    "Extract the career, university, and every cycle with its courses. "
    "Use course names exactly as written in the document. "
    "Only include what appears in the document."
)

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

class ClaudeError(Exception):
    pass

class UnsupportedFileError(Exception):
    pass

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
