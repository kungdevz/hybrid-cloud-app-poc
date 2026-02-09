
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def wait_for_server():
    print("Waiting for server to be ready...")
    for _ in range(10):
        try:
            requests.get(f"{BASE_URL}/users")
            print("Server is ready.")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    print("Server failed to start.")
    return False

def verify_backend_update():
    if not wait_for_server():
        return

    print("Verifying backend update consistency...")
    
    # 1. Create a user
    print("Creating user...")
    user_data = {"handle": "ui_test_user"}
    try:
        resp = requests.post(f"{BASE_URL}/users", json=user_data)
        resp.raise_for_status()
        user = resp.json()
        user_id = user['id']
        print(f"User created: {user}")
    except Exception as e:
        print(f"Failed to create user: {e}")
        return

    # 2. Update the user
    print("Updating user...")
    update_data = {"handle": "ui_test_user_updated"}
    try:
        resp = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
        resp.raise_for_status()
        updated_user = resp.json()
        print(f"User updated response: {updated_user}")
    except Exception as e:
        print(f"Failed to update user: {e}")
        return

    # 3. Fetch all users immediately
    print("Fetching all users immediately...")
    try:
        resp = requests.get(f"{BASE_URL}/users")
        resp.raise_for_status()
        users = resp.json()
        
        # Find our user
        found_user = next((u for u in users if str(u['id']) == str(user_id)), None)
        
        if found_user:
            print(f"Fetched user from list: {found_user}")
            if found_user['handle'] == "ui_test_user_updated":
                print("SUCCESS: Backend returned updated data.")
            else:
                print("FAILURE: Backend returned OLD data.")
        else:
            print("FAILURE: User not found in list.")
            
    except Exception as e:
        print(f"Failed to fetch users: {e}")

if __name__ == "__main__":
    verify_backend_update()
