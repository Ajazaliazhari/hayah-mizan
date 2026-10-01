from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib.auth.views import redirect_to_login


def staff_required(view_func):
    """Only allow staff users. Redirect non-logged-in to login, 403 for non-staff."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            raise PermissionDenied("You don't have permission to access the dashboard.")
        return view_func(request, *args, **kwargs)
    return wrapper
