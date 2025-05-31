from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, status, Depends
from fastapi import Request
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import os
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")  # Replace in prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")  # Change to your PostgreSQL URI in production
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table for user access to designs
user_design_access = Table(
    'user_design_access', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('design_id', Integer, ForeignKey('designs.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    designs = relationship("Design", secondary=user_design_access, back_populates="users")

class Design(Base):
    __tablename__ = "designs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    users = relationship("User", secondary=user_design_access, back_populates="designs")

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/api/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    if request.password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    bytes = request.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes, salt)

    new_user = User(email=request.email, password=hashed.decode('utf-8'))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/api/login")
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = create_access_token(data={"sub": str(user.id)})
    response = JSONResponse(content={
        "message": "Login successful", 
        "id": user.id, 
        "email": user.email
    })
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True ,
        secure=False, # set to true when using HTTPS in production
        samesite="Lax",
        path="/"
    )

    return response

@app.get("/api/me")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token payload invalid")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
    }
        

@app.get("/api/mockup")
async def placeholder_mockup():
    return {"message": "This is a placeholder endpoint for mockup processing."}
