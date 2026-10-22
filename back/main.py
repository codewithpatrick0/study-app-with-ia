from fastapi import Depends, FastAPI, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db
from .processing import processing_file, ClaudeError, UnsupportedFileError
from .schemas import UserCreate, UserRead
from .services import UserAlreadyExistsError, create_user

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['POST'],
    allow_headers=['Content-Type'],  # Needed for JSON bodies sent from the browser
)

@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, data)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.post("/base-processing")
async def base_processing(file: UploadFile):
    try:
        data = await file.read()

        processed_file = await processing_file(data, file.content_type)

        return processed_file
    except UnsupportedFileError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except ClaudeError as e:
        raise HTTPException(status_code=502, detail=str(e))
