import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_sqlite_file():
    print("Проверка файла базы данных")
    db_path = project_root / "fitlog.db"
    print(f"Путь: {db_path}")
    
    if db_path.exists():
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Таблиц: {len(tables)}")
        conn.close()
        return True
    else:
        print("Файл не найден")
        return False

def test_sqlalchemy_connection():
    print("Проверка SQLAlchemy")
    try:
        from backend.app.database import engine, Base, SessionLocal
        with engine.connect() as conn:
            pass
        
        db = SessionLocal()
        try:
            db.execute("SELECT 1")
        finally:
            db.close()
        
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_user_model():
    print("Тестирование модели User")
    try:
        from backend.app.database import SessionLocal
        from backend.app.models import User
        from backend.app.auth import get_password_hash
        
        db = SessionLocal()
        
        try:
            users = db.query(User).all()
            print(f"Пользователей: {len(users)}")
            
            if not users:
                test_user = User(
                    email="admin@fitlog.com",
                    username="admin",
                    full_name="Администратор",
                    hashed_password=get_password_hash("admin123")
                )
                db.add(test_user)
                db.commit()
                print("Создан тестовый пользователь")
            
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_registration_flow():
    print("Тестирование регистрации")
    try:
        from backend.app.database import SessionLocal
        from backend.app.models import User
        from backend.app.auth import get_password_hash, verify_password
        
        db = SessionLocal()
        
        try:
            test_email = "test_reg@fitlog.com"
            existing = db.query(User).filter_by(email=test_email).first()
            if existing:
                db.delete(existing)
                db.commit()
            
            password = "TestPassword123"
            hashed_pw = get_password_hash(password)
            
            new_user = User(
                email=test_email,
                username="testuser",
                full_name="Тестовый",
                hashed_password=hashed_pw
            )
            
            db.add(new_user)
            db.commit()
            
            password_correct = verify_password(password, new_user.hashed_password)
            print(f"Пароль верен: {password_correct}")
            
            return password_correct
        finally:
            db.close()
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_api_endpoints():
    print("Тестирование API")
    try:
        import requests
        base_url = "http://localhost:8000/api"
        
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health: {response.status_code}")
        
        data = {
            "email": "apitest@fitlog.com",
            "username": "apitest",
            "password": "ApiTest123",
            "full_name": "API Тест"
        }
        response = requests.post(f"{base_url}/users/register", json=data, timeout=5)
        print(f"Register: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def main():
    results = []
    
    results.append(("SQLite файл", test_sqlite_file()))
    results.append(("SQLAlchemy", test_sqlalchemy_connection()))
    results.append(("User модель", test_user_model()))
    results.append(("Регистрация", test_registration_flow()))
    results.append(("API", test_api_endpoints()))
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"ИТОГО: {passed}/{total}")

if __name__ == "__main__":
    main()