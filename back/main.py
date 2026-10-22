from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .processing import processing_file, ClaudeError, UnsupportedFileError

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['POST']
)

@app.post("/base-processing")
async def base_processing(file: UploadFile):
    try:
        data = await file.read()

        processed_file = await processing_file(data, file.content_type)

        return {"name": file.filename, "type": file.content_type, "size": len(data), "response": processed_file}
    except UnsupportedFileError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except ClaudeError as e:
        raise HTTPException(status_code=502, detail=str(e))
