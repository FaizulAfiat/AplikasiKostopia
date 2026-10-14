import jwt
from datetime import datetime, timedelta

# Pengaturan token JWT: kunci rahasia, algoritma, dan masa berlaku (24 jam)
SECRET_KEY = "rahasia_kostopia_super_aman_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Membuat token login (JWT) berisi data user dan waktu kedaluwarsa
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt