from django.http import HttpResponseForbidden

class CheckHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查请求头信息
        if not self.is_valid_request(request):
            return HttpResponseForbidden("Forbidden: Invalid request headers")
        response = self.get_response(request)
        return response

    def is_valid_request(self, request):
        # 检查 User-Agent 是否存在且包含关键字
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not user_agent or 'Mozilla' not in user_agent:
            return False

        # 检查 Referer 是否存在且包含关键字
        referer = request.META.get('HTTP_REFERER', '')
        if not referer or 'your_domain.com' not in referer:
            return False

        # 检查 Accept-Language 是否存在
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if not accept_language:
            return False

        return True
