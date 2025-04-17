from django.http import HttpResponseForbidden, HttpResponse
import time
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
import datetime

class CheckUserAgentMiddleware:
    """
    这个中间件类用于检查请求中的 User-Agent 头部。

    在初始化方法中，定义了一个常见机器人（爬虫）的列表。

    在 process_request 方法中：
    - 从请求中获取 User-Agent 头部的值。
    - 如果 User-Agent 为空、包含 'python-requests' 或包含常见爬虫的字符串，返回禁止响应。

    在 is_common_bot 方法中，检查 User-Agent 是否包含常见爬虫的字符串。
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.common_bots = [
            'Googlebot', 'Bingbot', 'Slurp', 'DuckDuckBot', 'Baiduspider',
            'YandexBot', 'Sogou', 'Exabot', 'facebot', 'ia_archiver',
            'MJ12bot', 'AhrefsBot', 'SEMrushBot', 'DotBot', 'Gigablast',
            'Surdotlybot', 'SeznamBot', 'Qwantify', 'CensysInspect',
            'ZumBot', 'PetalBot'
        ]

    def __call__(self, request):
        """
        处理请求。
        获取 User-Agent 并进行检查，如果不符合条件则禁止请求。
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not user_agent or 'python-requests' in user_agent.lower() or self.is_common_bot(user_agent):
            return HttpResponseForbidden("禁止：不允许自动请求或爬虫.")

        response = self.get_response(request)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response['X-Current-Time'] = current_time
        return response

    def is_common_bot(self, user_agent):
        """
        检查 User-Agent 是否为常见爬虫。
        返回 True 表示是，False 表示否。
        """
        return any(bot in user_agent for bot in self.common_bots)


class RateLimitMiddleware:
    """
    这个中间件类用于限制 IP 的请求速率，并处理超限和黑名单情况。

    在初始化方法中，接收 get_response 函数。

    在 __call__ 方法中：
    - 获取客户端 IP 地址。
    - 检查 IP 是否在黑名单中，如果是则返回禁止响应。
    - 检查 IP 是否请求速率超限，如果是则返回相应响应。
    - 否则，正常处理请求。

    在 get_client_ip 方法中，根据请求元数据获取客户端 IP 地址。

    在 is_blacklisted 方法中，检查 IP 是否在黑名单缓存中。

    在 is_rate_limited 方法中：
    - 获取 IP 的请求记录。
    - 删除过期的请求记录。
    - 根据剩余请求记录数量判断是否超限。
    - 如果超限且超过黑名单阈值，将 IP 加入黑名单。
    - 记录新的请求时间并更新缓存。
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        主处理逻辑。
        获取 IP 并进行各种检查和处理。
        """
        ip = self.get_client_ip(request)
        if self.is_blacklisted(ip):
            return HttpResponse("禁止", status=403)
        if self.is_rate_limited(ip):
            return HttpResponse("请求太多", status=429)
        return self.get_response(request)

    def get_client_ip(self, request):
        """
        获取客户端 IP 地址。
        根据不同的请求头获取 IP。
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_blacklisted(self, ip):
        """
        检查 IP 是否在黑名单中。
        通过缓存获取判断。
        """
        return cache.get(f"blacklist:{ip}") is not None

    def is_rate_limited(self, ip):
        """
        检查 IP 是否请求速率超限。
        处理请求记录，判断是否超限，并进行相应处理。
        """
        rate_limit_key = f"rl:{ip}"
        blacklist_key = f"blacklist:{ip}"
        requests = cache.get(rate_limit_key, [])  # 获取 get 请求记录
        now = time.time()

        # 删除过期的请求
        requests = [req for req in requests if now - req < 60]

        if len(requests) >= settings.RATE_LIMIT_THRESHOLD:
            if len(requests) > settings.BLACKLIST_THRESHOLD:
                # 将 IP 添加到黑名单，并设置黑名单持续时间
                cache.set(blacklist_key, True, timeout=settings.BLACKLIST_DURATION)
            return True

        # 记录新的请求时间
        requests.append(now)
        cache.set(rate_limit_key, requests, timeout=60)
        return False