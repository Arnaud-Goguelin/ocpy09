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
            "csrf_token": lambda request: get_token(request),
        }
    )
    return env


def user_context(request):
    """Context processor to pass 'user' objet in Jinja2"""
    return {"user": request.user if hasattr(request, "user") else None}
