import requests
import time

def test_app():
    try:
        # Test if the app is running
        response = requests.get('http://127.0.0.1:5000', timeout=5)
        print(f"App is running! Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Test the save_rating endpoint
        rating_data = {
            'book_id': 1,
            'rating': 5
        }
        
        # Since we can't actually log in, we'll just test if the endpoint exists
        try:
            response = requests.post('http://127.0.0.1:5000/save_rating', 
                                   json=rating_data, 
                                   timeout=5)
            print(f"Save rating endpoint response: {response.status_code}")
            print(f"Response content: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error testing save_rating endpoint: {e}")
            
        # Test the recently_rated endpoint
        try:
            response = requests.get('http://127.0.0.1:5000/recently_rated', 
                                  timeout=5)
            print(f"Recently rated endpoint response: {response.status_code}")
            print(f"Response content: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error testing recently_rated endpoint: {e}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to app: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_app()