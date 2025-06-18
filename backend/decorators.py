from django.contrib.auth.decorators import user_passes_test, login_required


def _in_groups(groups):
    """Return True if user is authenticated and belongs to any of groups or is superuser."""
    def predicate(user):
        return user.is_authenticated and (
            user.is_superuser or user.groups.filter(name__in=groups).exists()
        )

    return predicate


def role_required(groups):
    """Decorator that requires user to be in given Django groups.

    Example:
        @role_required(["Profesor"])
        def my_view(request):
            ...
    """

    def decorator(view_func):
        return login_required(user_passes_test(_in_groups(groups))(view_func))

    return decorator
