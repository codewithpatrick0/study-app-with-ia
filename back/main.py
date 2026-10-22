from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import base64
import anthropic

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['POST']
)

client = anthropic.AsyncAnthropic()

# TEST

@app.post("/base-processing")
async def hello(file: UploadFile):
    data = await file.read()
    return {"name": file.filename, "type": file.content_type, "size": len(data)}

#data = ''
#encoded = base64.standard_b64encode(data).decode('UTF-8')