import requests
from datetime import datetime, timedelta
import os

# Wise API credentials
API_TOKEN = os.getenv('WISE_API_TOKEN')

# Wise API endpoint
BASE_URL = 'https://api.wise.com'

def get_user_profile():
    endpoint = f"{BASE_URL}/v2/profiles"
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        profiles = response.json()
        # Assuming we want the first personal profile
        personal_profile = next((profile for profile in profiles if profile['type'] == 'personal'), None)
        return personal_profile['id'] if personal_profile else None
    else:
        print(f"Error fetching profile: {response.status_code} - {response.text}")
        return None

def get_transactions(profile_id, start_date, end_date):
    endpoint = f"{BASE_URL}/v3/profiles/{profile_id}/transactions"
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'intervalStart': start_date.isoformat(),
        'intervalEnd': end_date.isoformat(),
        'type': 'TRANSACTIONS'
    }
    
    all_transactions = []
    
    while True:
        response = requests.get(endpoint, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('items', [])
            all_transactions.extend(transactions)
            
            if 'nextPage' not in data:
                break
            
            params['page'] = data['nextPage']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    
    return all_transactions

def main():
    profile_id = get_user_profile()
    if not profile_id:
        print("Failed to retrieve user profile.")
        return

    # Set the date range for fetching transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Fetch last 30 days of transactions
    
    transactions = get_transactions(profile_id, start_date, end_date)
    
    print(f"Fetched {len(transactions)} transactions")
    for transaction in transactions:
        print(f"Date: {transaction['date']}, Amount: {transaction['amount']['value']} {transaction['amount']['currency']}, Description: {transaction['details']['description']}")

if __name__ == "__main__":
    main()
