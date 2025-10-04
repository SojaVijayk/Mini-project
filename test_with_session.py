import requests

# Test the recently rated functionality with proper session handling
base_url = 'http://127.0.0.1:5000'

# Create a session to maintain cookies
session = requests.Session()

# First, let's try to access the recently rated API endpoint
try:
    response = session.get(f'{base_url}/recently_rated')
    print(f"Recently rated endpoint status: {response.status_code}")
    print(f"Recently rated response: {response.json()}")
except Exception as e:
    print(f"Error testing recently rated endpoint: {e}")

# Test accessing the recently rated page
try:
    response = session.get(f'{base_url}/recently_rated_page')
    print(f"\nRecently rated page status: {response.status_code}")
    if response.status_code == 200:
        print("Recently rated page is accessible")
        # Check if the response contains expected content
        if "Recently Rated Books" in response.text:
            print("Page contains expected title")
        else:
            print("Page doesn't contain expected title")
    else:
        print(f"Error accessing recently rated page: {response.status_code}")
except Exception as e:
    print(f"Error testing recently rated page: {e}")

# Test accessing the user home page
try:
    response = session.get(f'{base_url}/user_home')
    print(f"\nUser home page status: {response.status_code}")
    if response.status_code == 200:
        print("User home page is accessible")
    else:
        print(f"Error accessing user home page: {response.status_code}")
except Exception as e:
    print(f"Error testing user home page: {e}")