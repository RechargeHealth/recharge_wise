import requests
from datetime import datetime, timedelta
import os

# Wise API credentials
API_TOKEN = os.getenv('WISE_API_TOKEN')
PROFILE_ID = os.getenv('WISE_PROFILE_ID')

# Wise API endpoint
BASE_URL = 'https://api.transferwise.com'

def get_transactions(start_date, end_date):
    endpoint = f"{BASE_URL}/v1/profiles/{PROFILE_ID}/transactions"
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'interval': 'MONTH',
        'offset': 0,
        'limit': 100,  # Adjust based on Wise's pagination limits
        'type': 'TRANSACTIONS',
        'createdDateStart': start_date.isoformat(),
        'createdDateEnd': end_date.isoformat()
    }
    
    all_transactions = []
    
    while True:
        response = requests.get(endpoint, headers=headers, params=params)
        
        if response.status_code == 200:
            transactions = response.json()
            all_transactions.extend(transactions)
            
            if len(transactions) < params['limit']:
                break
            
            params['offset'] += params['limit']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    
    return all_transactions

def main():
    # Set the date range for fetching transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Fetch last 30 days of transactions
    
    transactions = get_transactions(start_date, end_date)
    
    print(f"Fetched {len(transactions)} transactions")
    for transaction in transactions:
        print(f"Date: {transaction['date']}, Amount: {transaction['amount']}, Description: {transaction['description']}")

if __name__ == "__main__":
    main()