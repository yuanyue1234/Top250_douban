from django.http import HttpResponseForbidden, HttpResponse
import time
from django.core.cache import cache
from django.conf import settings

class CheckUserAgentMiddleware:
    """
    中间件来检查请求中的User-Agent标头。
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查User-Agent头
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not user_agent or 'python-requests' in user_agent.lower():
            return HttpResponseForbidden("禁止：不允许自动请求.")

        # 如果User-Agent有效，则继续处理响应
        response = self.get_response(request)
        return response

class RateLimitMiddleware:
    """
    中间件来限制IP请求速率，并将超限IP加入黑名单。
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        if self.is_blacklisted(ip):
            return HttpResponse("禁止", status=403)
        if self.is_rate_limited(ip):
            return HttpResponse("请求太多", status=429)
        return self.get_response(request)

    def get_client_ip(self, request):
        # 获取客户端IP地址
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_blacklisted(self, ip):
        # 检查IP是否在黑名单中
        return cache.get(f"blacklist:{ip}") is not None

    def is_rate_limited(self, ip):
        rate_limit_key = f"rl:{ip}"
        blacklist_key = f"blacklist:{ip}"
        requests = cache.get(rate_limit_key, [])  # 获取 get请求记录
        now = time.time()

        # 删除过期的请求
        requests = [req for req in requests if now - req < 60]

        if len(requests) >= settings.RATE_LIMIT_THRESHOLD:
            if len(requests) > settings.BLACKLIST_THRESHOLD:
                # 将IP添加到黑名单，并设置黑名单持续时间
                cache.set(blacklist_key, True, timeout=settings.BLACKLIST_DURATION)
            return True

        # 记录新的请求时间
        requests.append(now)
        cache.set(rate_limit_key, requests, timeout=60)
        return False
