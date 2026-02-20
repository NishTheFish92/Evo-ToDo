from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from dotenv import load_dotenv
import os

#Loading the environment variables

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

app = FastAPI()

#Pydantic thingy to enforce json rules for user creation
class UserCreate(BaseModel):
    username: str
    password : str

#pwd_context here instantiates the CryptContext class and allows for hashing.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#oauth2_scheme enforces Oauth2 rues and ensures that Bearer <auth_code> is included in
#The header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#Mock DB
users_db = {}

#Password hashing and verification - Easy enough
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

#Returns jwt encoded stuff of the data, secret key and algo.
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#This function is important to ensure that the current user session is valid.
#Gets the user from the access token.
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = users_db.get(username)
    if user is None:
        raise credentials_exception

    return user


#Routes

@app.post("/register")
async def register(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    users_db[user.username] = {
        "username": user.username,
        "hashed_password": hash_password(user.password)
    }

    return {"message": "User created successfully"}
#Oauth2Passwordreqform requires data in urlencoded format.
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["username"]})

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}, you are authenticated"}