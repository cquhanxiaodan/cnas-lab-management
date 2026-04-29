import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cnas_lab.db")
SECRET_KEY = os.getenv("SECRET_KEY", "cnas-lab-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
