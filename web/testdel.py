import requests
url = 'http://127.0.0.1:5000/delete_data?key=1'
headers = {'Content-Type': 'application/json'} # 设置请求头为JSON类型
response = requests.get(url, headers=headers)
print(f'Status Code: {response.status_code}')
print(f'Response: {response.json()}')