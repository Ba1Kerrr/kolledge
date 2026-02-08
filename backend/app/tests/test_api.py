import sys
import os
import time
import requests
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_api_endpoints():
    base_url = "http://localhost:8000/api"
    test_user = None
    token = None
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("Health check failed")
            return False
        
        test_email = f"api_test_{int(time.time())}@fitlog.com"
        reg_data = {
            "email": test_email,
            "username": f"apitest{int(time.time())}",
            "password": "ApiTest123",
            "full_name": "API Test"
        }
        
        response = requests.post(f"{base_url}/users/register", json=reg_data, timeout=5)
        if response.status_code != 200:
            print("Register failed")
            return False
        
        test_user = response.json()
        
        login_data = {"username": reg_data["username"], "password": reg_data["password"]}
        login_response = requests.post(f"{base_url}/users/login", data=login_data, timeout=5)
        
        if login_response.status_code != 200:
            print("Login failed")
            return False
        
        token_data = login_response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("No token")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        endpoints = [
            ("GET /users/me", f"{base_url}/users/me", "GET"),
            ("GET /users/all", f"{base_url}/users/all", "GET"),
            ("GET /workouts/", f"{base_url}/workouts/", "GET"),
            ("GET /meals/", f"{base_url}/meals/", "GET"),
            ("GET /measurements/", f"{base_url}/measurements/", "GET"),
            ("GET /goals/", f"{base_url}/goals/", "GET"),
            ("GET /stats/dashboard", f"{base_url}/stats/dashboard", "GET"),
            ("GET /stats/workouts/monthly", f"{base_url}/stats/workouts/monthly", "GET"),
        ]
        
        for name, url, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=5)
                elif method == "POST":
                    response = requests.post(url, headers=headers, timeout=5, json={})
                
                if response.status_code not in [200, 201, 204]:
                    print(f"{name}: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"{name}: {e}")
                return False
        
        workout_data = {
            "name": "Тестовая тренировка",
            "date": "2024-01-01",
            "duration": 60,
            "exercises": [{
                "name": "Приседания",
                "category": "legs",
                "sets": [{"set_number": 1, "reps": 10, "weight": 80}]
            }]
        }
        
        response = requests.post(f"{base_url}/workouts/", headers=headers, json=workout_data, timeout=5)
        if response.status_code not in [200, 201]:
            print("Create workout failed")
            return False
        
        workout = response.json()
        
        goal_data = {
            "title": "Тестовая цель",
            "goal_type": "weight",
            "target_value": 80,
            "current_value": 85,
            "unit": "кг"
        }
        
        response = requests.post(f"{base_url}/goals/", headers=headers, json=goal_data, timeout=5)
        if response.status_code not in [200, 201]:
            print("Create goal failed")
            return False
        
        goal = response.json()
        
        meal_data = {
            "name": "Тестовый обед",
            "meal_type": "lunch",
            "calories": 600,
            "protein": 30,
            "carbs": 80,
            "fat": 20
        }
        
        response = requests.post(f"{base_url}/meals/", headers=headers, json=meal_data, timeout=5)
        if response.status_code not in [200, 201]:
            print("Create meal failed")
            return False
        
        measurement_data = {
            "date": "2024-01-01",
            "weight": 75.5,
            "body_fat": 15.0
        }
        
        response = requests.post(f"{base_url}/measurements/", headers=headers, json=measurement_data, timeout=5)
        if response.status_code not in [200, 201]:
            print("Create measurement failed")
        return False
        
        return True
        
    except Exception as e:
        print(f"API test error: {e}")
        return False
    finally:
        if token and test_user:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                requests.delete(f"{base_url}/users/{test_user.get('id')}", headers=headers, timeout=5)
            except:
                pass

if __name__ == "__main__":
    success = test_api_endpoints()
    print(f"API тест: {'Пройден' if success else 'Не пройден'}")
    sys.exit(0 if success else 1)