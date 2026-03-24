from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated 
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import Depends
from database import get_db 
import os
from dotenv import load_dotenv
import logging
#Это 3ий коммит
#Это 4ый коммит
db_dep = Annotated[Session, Depends(get_db)]
# "login" — это название нашего роута для входа
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

import models
from database import engine, get_db

# Создаем таблицы при запуске (если еще не созданы)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- НАСТРОЙКА CORS (чтобы фронтенд работал) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Вместо bcrypt используем pbkdf2_sha256. 
# Он работает "из коробки" и не требует компиляторов.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

load_dotenv()

#Настройка дебагера
logging.basicConfig(level=logging.DEBUG, filename="backend_log.txt", filemode="w", format="%(asctime)s %(levelname)s %(message)s")

# Настройки остаются прежними
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict):
    to_encode = data.copy()
    # Используем время с учетом часового пояса (timezone.utc)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Генерируем токен через PyJWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class UserCreate(BaseModel):
    username: Annotated[str, Query(min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")] = None
    password: Annotated[str | None, Query(min_length=3, max_length=50)] = None


@app.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_pwd = pwd_context.hash(user_data.password)

    new_user = models.User(username=user_data.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Пользователь успешно создан", "user_id": new_user.id}

@app.post("/login")
def login_user(user_data: UserCreate, db: Session = Depends(get_db)):
    
    # 1. Ищем пользователя по имени
    user = db.query(models.User).filter(models.User.username == user_data.username).first()

    if not user:
        logging.info("Попытка входа "+user_data.username+ " пользователь не найден")
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    # 3. Проверяем пароль (сравниваем хеши через нашу pbkdf2_sha256)
    if not pwd_context.verify(user_data.password, user.hashed_password):
        logging.info("Попытка входа "+user_data.username+ " неверный пароль")
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    # 4. Если всё ок — создаем токен
    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    # 5. Возвращаем токен фронтенду
    logging.info("Пользователь "+user_data.username+" успешно вошел в систему")
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dep):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Не удалось подтвердить личность",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Расшифровываем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        logging.warning("Ошибка потверждения токена для:"+username)
        # Если токен подделан, просрочен или поврежден
        raise credentials_exception

    # 2. Ищем пользователя в базе данных
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if user is None:
        logging.info("Пользоваель "+username+" не найден при потверждении токена")
        raise credentials_exception
        
    return user # Возвращаем полноценный объект пользователя из БД

# Убедись, что тут написано именно /users/me (со всеми слэшами)
@app.get("/users/me") 
def read_users_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return {
        "id": current_user.id, 
        "username": current_user.username
    }
@app.get("/home")
def return_all_user():
    with Session(engine) as session:
        stmt = select(func.count(models.User.id))
        count = session.execute(stmt).scalar()
        
    return {"total_users": count}
def check_admin_role(current_user: Annotated[models.User, Depends(get_current_user)]):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ только для администраторов")
    return current_user

# Теперь твой роут станет очень коротким и чистым:
@app.get("/admin/stats")
def get_admin_stats(admin: Annotated[models.User, Depends(check_admin_role)]):
    return {"status": "success", "data": "Секреты раскрыты!"}



from typing import Annotated, Optional

# Используем @app.delete, так как фронтенд шлет DELETE запрос
@app.delete("/admin/delete-user") 
def delete_user(
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    db: Annotated[Session, Depends(get_db)] = None,
    admin: Annotated[models.User, Depends(check_admin_role)] = None,
):
    # 1. Проверяем, переданы ли данные
    if user_id is None and username is None:
        raise HTTPException(status_code=400, detail="Нужен ID или имя пользователя")

    query = db.query(models.User)
    
    # 2. Поиск пользователя
    user = None
    if user_id is not None:
        # Ищем строго по ID
        user = query.filter(models.User.id == user_id).first()
    elif username:
        # Ищем по имени
        user = query.filter(models.User.username == username).first()
    
    # 3. Если после всех проверок пользователя нет
    if not user:
        # Исправлено: status_code (было sttus)
        raise HTTPException(status_code=404, detail="Пользователь не найден в базе данных")

    # 4. Проверка на удаление самого себя
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Вы не можете удалить свой собственный аккаунт")

    # 5. Удаление
    username_for_log = user.username # Сохраняем имя для лога перед удалением
    db.delete(user)
    db.commit()

    logging.info(f"Админ {admin.username} успешно удалил пользователя {username_for_log}")
    return {"detail": f"Пользователь {username_for_log} успешно удален"}

class PurchaseCreate(BaseModel):
    item_name: str
    price: float



@app.post("/admin/add-purchases")
def add_purchases(
    user_data: UserCreate,
    purchase_data: PurchaseCreate,
    db: Annotated[Session, Depends(get_db)] = None,
    admin: Annotated[models.User, Depends(check_admin_role)] = None,
    current_user: Annotated[models.User, Depends(get_current_user)] = None


):

    new_purchase = models.Purchase(
        item_name = purchase_data.item_name,
        price=purchase_data.price,
        user_id= current_user.id
    )

    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)

    return {"message": "Успешная покупка", "purchase_id": new_purchase.id}