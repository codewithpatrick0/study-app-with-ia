import base64
import anthropic

from .config.settings import settings

PDF_TYPE = 'application/pdf'
IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

class ClaudeError(Exception):
    pass

class UnsupportedFileError(Exception):
    pass

async def processing_file(data: bytes, media_type: str) -> str:
    if media_type == PDF_TYPE:
        block_type = 'document'
    elif media_type in IMAGE_TYPES:
        block_type = 'image'
    else:
        raise UnsupportedFileError(f'Unsupported file type: {media_type}')

    encoded = base64.standard_b64encode(data).decode('UTF-8')
    response = await client.messages.create(
        model='claude-haiku-4-5',
        max_tokens=10000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": block_type,
                    "source": {"type": "base64", "media_type": media_type, "data": encoded},
                },
                {"type": "text", "text": "Lista los ciclos y cursos de esta malla curricular."},
            ],
        }],
    )
    if response.stop_reason == "refusal":
        raise ClaudeError("Claude declined the request")

    text = next((b.text for b in response.content if b.type == "text"), None)
    if text is None:
        raise ClaudeError("Claude returned no text")

    return text
