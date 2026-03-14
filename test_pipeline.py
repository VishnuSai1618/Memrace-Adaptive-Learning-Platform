import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def run_test():
    print("Starting test...")
    
    # login first
    session = requests.Session()
    print("1. Logging in...")
    login_res = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    if login_res.status_code != 200:
        print("Login failed. Registering new test user...")
        res = session.post(f"{BASE_URL}/api/auth/signup", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        if res.status_code not in (200, 201, 302):
            print("Failed to register test user:", res.text)
            return
        
        login_res = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
    
    print("Login successful.")
    
    # Create deck with text
    print("\n2. Uploading text content...")
    upload_res = session.post(f"{BASE_URL}/api/content/upload", json={
        "title": "Test AI Deck",
        "description": "Testing the AI generation pipeline",
        "content": "Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy. Here, we describe the general principles of photosynthesis and highlight how scientists are studying this natural process to help develop clean fuels and sources of renewable energy. There are two types of photosynthetic processes: oxygenic photosynthesis and anoxygenic photosynthesis."
    })
    
    if upload_res.status_code != 201:
        print("Upload failed:", upload_res.text)
        return
        
    deck_data = upload_res.json()
    deck_id = deck_data['deck']['id']
    print(f"Deck created successfully with ID: {deck_id}")
    
    # Generate Quizzes
    print("\n3. Generating Quizzes...")
    start_time = time.time()
    quiz_res = session.post(f"{BASE_URL}/api/content/generate-quiz", json={
        "deck_id": deck_id,
        "num_questions": 3
    })
    print(f"Quiz generation took {time.time() - start_time:.2f} seconds")
    
    if quiz_res.status_code != 201:
        print("Quiz Generation FAILED:", quiz_res.status_code, quiz_res.text)
    else:
        print("Quiz Generation SUCCESS:", len(quiz_res.json().get('quizzes', [])), "quizzes generated")
        print(json.dumps(quiz_res.json(), indent=2))
        
if __name__ == "__main__":
    run_test()
