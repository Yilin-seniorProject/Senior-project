import requests
import base64
from PIL import Image
from io import BytesIO
url = 'http://127.0.0.1:5000/submit_data'
params = {
    "imagename": "1.jpg",
}
headers = {'Content-Type': 'application/json'} 
# 发送GET请求
response = requests.get(url, params=params, headers=headers)

print(f'Status Code: {response.status_code}')
response_data = response.json()
image_data = response_data['image_data']
image_binary = base64.b64decode(image_data)
image = Image.open(BytesIO(image_binary))
image.show()