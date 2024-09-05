
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

EXEMPT_URLS = [settings.LOGIN_URL.lstrip('/')]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [x for x in settings.LOGIN_EXEMPT_URLS]

class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')

        if not request.user.is_authenticated:
            if not any(url == path for url in EXEMPT_URLS):
                messages.info(request, 'You must be logged in to access that page.')
                return redirect(settings.LOGIN_URL)