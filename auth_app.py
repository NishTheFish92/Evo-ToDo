from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId
import os

#Loading the environment variables

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

router = APIRouter(prefix="/auth")

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
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["todo"]
users = db["users"]

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
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await users.find_one({"_id" : ObjectId(user_id)})
    if not user:
        raise credentials_exception

    return user


#Routes

@router.post("/register")
async def register(user: UserCreate):
    userexist = await users.find_one({"username" : user.username })
    print("User exist value:", userexist, flush=True)
    print("\n\n")
    if userexist:
        raise HTTPException(status_code=400, detail="User already exists")

    result = users.insert_one({
        "username" : user.username,
        "password" : hash_password(user.password)
    })

    return {"message": "User created successfully"}
#Oauth2Passwordreqform requires data in urlencoded format.
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users.find_one({"username": form_data.username})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username")

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")

    access_token = create_access_token(data={"user_id": str(user["_id"])})

    return {"access_token": access_token, "token_typ": "bearer"}

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}, you are authenticated"}