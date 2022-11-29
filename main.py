import io
import sympy
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
import cv2
import datetime
import numpy as np
from typing import Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette.responses import StreamingResponse

fake_users_db = {
    "janNowak": {
        "username": "janNowak",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    }
}

app = FastAPI()


@app.get("/prime/{number}", status_code=200)
async def check_prime(number: int):
    return sympy.isprime(number)


@app.post("/picture/invert", status_code=201)
async def invert(file: UploadFile = File(...)):
    image = await file.read()
    npAr = np.frombuffer(image, np.uint8)
    imagev2 = cv2.imdecode(npAr, cv2.IMREAD_COLOR)
    invertedImg = cv2.bitwise_not(imagev2)
    retval, buffer = cv2.imencode('.png', invertedImg)
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/png")


@app.post("/picture/invert")
async def invert_picture_colors(file: UploadFile = File(...)):
    content = await file.read()
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_inverted = cv2.bitwise_not(img)
    retval, buffer = cv2.imencode('.png', img_inverted)
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/png")


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/time")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return datetime.datetime.now()
