import requests
import os

# Wise Sandbox API credentials
API_TOKEN = os.getenv('WISE_SANDBOX_API_TOKEN')

# Wise Sandbox API endpoint
BASE_URL = 'https://api.sandbox.transferwise.tech'

def test_api_access():
    endpoint = f"{BASE_URL}/v1/profiles"
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            profiles = response.json()
            print("API access successful!")
            print(f"Number of profiles: {len(profiles)}")
            for profile in profiles:
                print(f"Profile ID: {profile['id']}, Type: {profile['type']}")
        else:
            print(f"API access failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if not API_TOKEN:
        print("WISE_SANDBOX_API_TOKEN environment variable is not set.")
    else:
        test_api_access()
