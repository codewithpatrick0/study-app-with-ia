import base64
import anthropic

from .config.settings import settings
from .schemas import Mesh

PDF_TYPE = 'application/pdf'
IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

class ClaudeError(Exception):
    pass

class UnsupportedFileError(Exception):
    pass

async def processing_file(data: bytes, media_type: str) -> Mesh:
    if media_type == PDF_TYPE:
        block_type = 'document'
    elif media_type in IMAGE_TYPES:
        block_type = 'image'
    else:
        raise UnsupportedFileError(f'Unsupported file type: {media_type}')

    encoded = base64.standard_b64encode(data).decode('UTF-8')
    response = await client.messages.parse(
        model='claude-haiku-5-5',
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": block_type,
                    "source": {"type": "base64", "media_type": media_type, "data": encoded},
                },
                {"type": "text", "text": (
                    "Extract the career, university, and every cycle with its courses. "
                    "Use course names exactly as written in the document. "
                    "Only include what appears in the document."
                )},
            ],
        }],
        output_format=Mesh
    )
    if response.stop_reason == "refusal":
        raise ClaudeError("Claude declined the request")
    if response.stop_reason == "max_tokens":
        raise ClaudeError("Response was cut off before finishing")

    mesh = response.parsed_output
    if mesh is None:
        raise ClaudeError("Claude returned no structured output")

    return mesh
