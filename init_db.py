from database import engine, Base
import models

print("Создаю базу данных...")
# Эта команда создает все таблицы, которые описаны в 
Base.metadata.create_all(bind=engine)
print("Готово! Проверь проводник в VS Code.")