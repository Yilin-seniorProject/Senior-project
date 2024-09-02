import requests
url = 'http://127.0.0.1:5000/update_data'
headers = {'Content-Type': 'application/json'} 
response = requests.get(url, headers=headers)
print(f'Status Code: {response.status_code}')
print(f'Response: {response.json()}')