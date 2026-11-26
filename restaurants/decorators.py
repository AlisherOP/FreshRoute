from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def owner_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Admins and staff have universal access to all portals
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if getattr(request.user, "role", None) != "OWNER":
            return HttpResponseForbidden("Restaurant owner access required.")
        return view_func(request, *args, **kwargs)

    return wrapped_view

