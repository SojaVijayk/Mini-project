import requests

# Test if the reading history routes are accessible
try:
    # Test the reading history JSON endpoint
    response = requests.get('http://127.0.0.1:5000/reading_history')
    print(f"Reading history JSON endpoint: {response.status_code}")
    print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"Error accessing reading history JSON endpoint: {e}")

try:
    # Test the reading history page endpoint
    response = requests.get('http://127.0.0.1:5000/reading_history_page')
    print(f"Reading history page endpoint: {response.status_code}")
    print(f"Content type: {response.headers.get('content-type')}")
except Exception as e:
    print(f"Error accessing reading history page endpoint: {e}")