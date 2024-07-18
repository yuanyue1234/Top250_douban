import requests

# 正常的请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'http://github.com',
    'Accept-Language': 'en-US,en;q=0.9'
}

response = requests.get('http://your_internal_ip:8000', headers=headers)
print(response.status_code)  # 应该返回200

# 模拟爬虫的请求头
headers = {
    'User-Agent': 'python-requests/2.25.1',
    'Referer': '',
    'Accept-Language': ''
}

response = requests.get('http://your_internal_ip:8000', headers=headers)
print(response.status_code)  # 应该返回403
