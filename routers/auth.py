from datetime import timedelta, datetime, timezone      # datetime modülü tarih ve saat işlemleri için kullanılır.
from typing import Annotated                            # Annotated modülü Pydantic tarafından sağlanır ve veri doğrulama ve dönüştürme için kullanılır.
from fastapi import APIRouter, Depends, HTTPException, Request   # APIRouter modülü FastAPI tarafından sağlanır ve endpointleri gruplamak için kullanılır.
from pydantic import BaseModel                          # BaseModel modülü Pydantic tarafından sağlanır ve veri doğrulama ve dönüştürme için kullanılır.
from sqlalchemy.orm import Session                      # Session modülü SQLAlchemy tarafından sağlanır ve veritabanı işlemleri için kullanılır.
from starlette import status                            # status modülü HTTP durum kodları için kullanılır.
from ..database import SessionLocal                       # SessionLocal modülü veritabanına erişmek için kullanılır.
from ..models import User                                 # models.py'den User modelini import ettik.
from passlib.context import CryptContext                # CryptContext modülü parolaları hashlemek ve doğrulamak için kullanılır.
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # OAuth2PasswordBearer ve OAuth2PasswordRequestForm modülleri JWT token oluşturmak ve doğrulamak için kullanılır.
from jose import JWTError, jwt                          # JWTError ve jwt modülleri JWT token oluşturmak ve doğrulamak için kullanılır.
from fastapi.templating import Jinja2Templates        # Jinja2Templates modülü FastAPI tarafından sağlanır ve HTML dosyalarını render etmek için kullanılır.

router = APIRouter(
    prefix="/auth", # prefix ile tüm endpointlerin başına /auth gelecek.
    tags=["Authentication"] # Authentication tagi Swagger UI'da ilgili enpointlerin başlığı olarak görünecek.
)

templates = Jinja2Templates(directory="templates") # Jinja2Templates modülü ile templates klasörünü belirttik.

SECRET_KEY = "unmt1jy4jmiivg78rfcwxhaz2fnt4bp3s58cngic5xrl2i5n68hxnb3dv18apd7e"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db  # yield return gibidir aynı işi yapar ama generator functır return tek bir değer döndürür ama yield birden fazla değer döndürebilir.
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]  # Veritabanına erişmek için bir dependency oluşturduk. Bunları endpointlerde kullanarak veritabanına erişebiliriz.

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

class CreateUserRequest(BaseModel): # Kullanıcı oluşturmak için kullanılacak request modeli (şeması)
    email: str
    username: str
    password: str
    first_name: str
    last_name: str
    role: str
    phone_number: str

class Token(BaseModel): # Token modeli
    access_token: str
    token_type: str

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta): # JWT token oluşturmak için kullanılan fonksiyon
    payload = {'sub': username, 'id': user_id, 'role': role}
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({'exp': expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str, db):  # Yardımcı kullanıcı kimlik doğrulama fonksiyonu
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.get("/login-page")
async def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
async def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, create_user_request: CreateUserRequest):
    user = User(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        is_active=True,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        phone_number=create_user_request.phone_number
    )
    db.add(user)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}