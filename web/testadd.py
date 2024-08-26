import requests
import json
import base64
from PIL import Image
import io
def image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        # 读取图像文件并将其转换为 Base64 编码
        image_binary = image_file.read()
        image_base64 = base64.b64encode(image_binary).decode('utf-8')
        return image_base64
image_path = 'web\static\img\Black_Dear.jpg'
image_base64 = image_to_base64(image_path)

url = 'http://127.0.0.1:5000/read_data' # 替换为你的Flask应用程序的URL
data = {
    "img": image_base64,
    'Longitude': 10,
    'Latitude': 20,
    'classname':'car',
    'midpoints':5
        }

headers = {'Content-Type': 'application/json'} # 设置请求头为JSON类型
response = requests.post(url, data=json.dumps(data), headers=headers)
print(f'Status Code: {response.status_code}')
print(f'Response: {response.json()}')