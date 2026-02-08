import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_password_hashing():
    print("Тестирование хеширования паролей")
    try:
        from backend.app.auth import get_password_hash, verify_password
        test_passwords = ["simple123", "ComplexPass!@#123"]
        
        for password in test_passwords:
            hashed = get_password_hash(password)
            is_valid = verify_password(password, hashed)
            print(f"Пароль: {password[:10]} Проверка: {is_valid}")
        
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_jwt_tokens():
    print("Тестирование JWT токенов")
    try:
        from backend.app.auth import create_access_token
        import jwt
        import os
        
        test_data = {"user_id": 1, "username": "testuser"}
        token = create_access_token(test_data)
        
        SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_user_authentication():
    print("Тестирование аутентификации пользователя")
    try:
        from backend.app.database import SessionLocal
        from backend.app.auth import authenticate_user, get_password_hash
        from backend.app.models import User
        
        db = SessionLocal()
        
        try:
            test_email = "auth_test@fitlog.com"
            test_username = "authtest"
            test_password = "AuthTest123"
            
            existing = db.query(User).filter_by(email=test_email).first()
            if existing:
                db.delete(existing)
                db.commit()
            
            new_user = User(
                email=test_email,
                username=test_username,
                full_name="Test User",
                hashed_password=get_password_hash(test_password)
            )
            
            db.add(new_user)
            db.commit()
            
            auth_result = authenticate_user(db, test_username, test_password)
            auth_wrong = authenticate_user(db, test_username, "wrongpassword")
            
            print(f"Правильный пароль: {auth_result}")
            print(f"Неправильный пароль: {auth_wrong}")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_end_to_end_auth():
    print("End-to-end тестирование")
    try:
        import requests
        import time
        
        base_url = "http://localhost:8000/api"
        
        reg_data = {
            "email": f"e2e_test_{int(time.time())}@fitlog.com",
            "username": f"e2etest{int(time.time())}",
            "password": "EndToEndTest123",
            "full_name": "Test User"
        }
        
        reg_response = requests.post(f"{base_url}/users/register", json=reg_data, timeout=5)
        
        if reg_response.status_code != 200:
            return False
        
        login_data = {"username": reg_data["username"], "password": reg_data["password"]}
        login_response = requests.post(f"{base_url}/users/login", data=login_data, timeout=5)
        
        if login_response.status_code != 200:
            return False
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(f"{base_url}/users/me", headers=headers, timeout=5)
        
        return user_response.status_code == 200
            
    except Exception:
        return False

def main():
    results = []
    
    results.append(("Хеширование паролей", test_password_hashing()))
    results.append(("JWT токены", test_jwt_tokens()))
    results.append(("Аутентификация", test_user_authentication()))
    results.append(("End-to-end тест", test_end_to_end_auth()))
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"ИТОГО: {passed}/{total} тестов пройдено")

if __name__ == "__main__":
    main()