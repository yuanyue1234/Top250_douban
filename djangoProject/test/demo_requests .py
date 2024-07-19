import requests

url = "http://localhost:8000"


def test_request_without_user_agent():
    response = requests.get(url)
    print("没有用户代理的请求:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    print()


def test_request_with_user_agent():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    print("使用用户代理的请求:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    print()


def test_request_with_custom_encoding():
    response = requests.get(url)
    print("使用自定义编码的请求:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print()


def test_ip_rate_limit():
    # 请求次数测试
    for i in range(1):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        print(f"Request {i + 1}: Status Code: {response.status_code}, Response Text: {response.text}")


if __name__ == "__main__":
    test_request_without_user_agent()
    test_request_with_user_agent()
    test_request_with_custom_encoding()
    # test_ip_rate_limit()
