from functools import wraps, WRAPPER_ASSIGNMENTS

from django.http import JsonResponse


def permission_required_json(perm, fn=None, login_url=None, raise_exception=False):
        """
        View decorator that checks for the given permissions before allowing the
        view to execute.
        ``perm`` is either a permission name as a string, or a list of permission
        names.
        ``fn`` is an optional callback that receives the same arguments as those
        passed to the decorated view and must return the object to check
        permissions against. If omitted, the decorator behaves just like Django's
        ``permission_required`` decorator, i.e. checks for model-level permissions.
        ``raise_exception`` is a boolean specifying whether to raise a
        ``django.core.exceptions.PermissionDenied`` exception if the check fails.
        You will most likely want to set this argument to ``True`` if you have
        specified a custom 403 response handler in your urlconf. If ``False``,
        the user will be redirected to the URL specified by ``login_url``.
        ``login_url`` is an optional custom URL to redirect the user to if
        permissions check fails. If omitted or empty, ``settings.LOGIN_URL`` is
        used.
        """

        def decorator(view_func):
            @wraps(view_func, assigned=WRAPPER_ASSIGNMENTS)
            def _wrapped_view(request, *args, **kwargs):
                # Normalize to a list of permissions
                if isinstance(perm, str):
                    perms = (perm,)
                else:
                    perms = perm

                # Get the object to check permissions against
                if callable(fn):
                    obj = fn(request, *args, **kwargs)
                else:
                    obj = fn

                # Get the user
                user = request.user
                if user.is_anonymous:
                    return JsonResponse({'success': False, 'reason': 'NotLoggedIn'}, status=403)

                # Check for permissions and return a response
                if user.has_perms(perms, obj):
                    return view_func(request, *args, **kwargs)
                else:
                    return JsonResponse({'success': False, 'reason': 'InsufficientPermissions'}, status=403)

            return _wrapped_view

        return decorator


def direct_object(request, *args, **kwargs):
    """used to turn an object into a callable that returns that object for permissions decorators"""
    return args[0]
