from typing import Annotated

from fastapi import Depends, FastAPI, Form, Response, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config.settings import settings
from .database import get_db
from .dependencies import get_current_user
from .models import User
from .processing import (
    ClaudeError,
    CourseMismatchError,
    FileTooLargeError,
    NotASyllabusError,
    UnsupportedFileError,
    processing_file,
    processing_syllabus,
)
from .schemas import LoginRequest, Syllabus, UserCreate, UserRead
from .security import ACCESS_TOKEN_COOKIE, create_access_token
from .services import UserAlreadyExistsError, authenticate_user, create_user

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type'],  # Needed for JSON bodies sent from the browser
    allow_credentials=True,  # Lets the browser send the auth cookie
)

@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, data)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.post("/auth/login", response_model=UserRead)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username_or_email, data.password.get_secret_value())
    if user is None:
        # Same message whether the user exists or not, so attackers can't probe accounts
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
        )
    # The token travels only in this cookie, never in the JSON body
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=create_access_token(user.id),
        httponly=True,                 # JavaScript can't read it (protects against XSS)
        samesite="strict",             # Only sent from our own site (protects against CSRF)
        secure=settings.cookie_secure, # HTTPS only in production
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return user

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    # JavaScript can't delete an HttpOnly cookie, so the server does it
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
        httponly=True,
        samesite="strict",
        secure=settings.cookie_secure,
        path="/",
    )

@app.get("/auth/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    # get_current_user already answers 401 when the cookie is missing or invalid
    return current_user

@app.post("/processing-mesh")
async def processing_mesh(file: UploadFile, current_user: User = Depends(get_current_user)):
    try:
        data = await file.read()

        processed_file = await processing_file(data, file.content_type)

        return processed_file
    except UnsupportedFileError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except ClaudeError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/processing-syllabus", response_model=Syllabus)
async def processing_syllabus_endpoint(
    file: UploadFile,
    courses: Annotated[list[str], Form(min_length=1)],  # Course names of the selected cycle
    current_user: User = Depends(get_current_user),
):
    try:
        data = await file.read()
        return await processing_syllabus(data, file.content_type, courses)
    except FileTooLargeError as e:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=str(e))
    except (NotASyllabusError, CourseMismatchError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))
    except UnsupportedFileError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except ClaudeError as e:
        raise HTTPException(status_code=502, detail=str(e))
