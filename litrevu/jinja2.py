from django.contrib.staticfiles.storage import staticfiles_storage
from django.middleware.csrf import get_token
from django.urls import reverse
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "static": staticfiles_storage.url,
            "url": reverse,
        }
    )
    return env


def user_context(request):
    """Context processor to pass 'user' and 'request' object in Jinja2"""
    return {
        "user": request.user if hasattr(request, "user") else None,
        "request": request,
        "csrf_token": get_token(request),
        "csrf_input": f'<input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">',
    }
