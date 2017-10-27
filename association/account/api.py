from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url

DEFAULT_PAGE = "dashboard"


class AnonymousRequiredMixin(object):
    """
    CBV mixin which verifies that the current user is Anonymous.
    """
    __authenticated_redirect_url = DEFAULT_PAGE

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(resolve_url(self.__authenticated_redirect_url))
        return super().dispatch(request, *args, **kwargs)


class AccreditationViewRequiredMixin(LoginRequiredMixin):
    """
    CBV mixin which verifies that the current user has the accreditation required.
    """
    accreditation = 1
    strict = False
    __redirect_url = DEFAULT_PAGE
    raise_exception = False

    def has_accreditation(self, request):
        """
        Customized method that checks the accreditation.
        """
        if self.strict and request.user.accreditation == self.accreditation:
            return True
        elif not self.strict and request.user.accreditation >= self.accreditation:
            return True
        # In case the 403 handler should be called raise the exception
        if self.raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_accreditation(request):
            return HttpResponseRedirect(resolve_url(self.__redirect_url))
        return super().dispatch(request, *args, **kwargs)


def accreditation_view_required(perm=1, strict=False, redirect_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has the accreditation required.
    Redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """

    def check_perms(user):
        if not user.is_authenticated and perm == 0:
            return True
        elif not user.is_authenticated:
            return False
        if (strict and user.accreditation == perm) or (not strict and user.accreditation >= perm):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=redirect_url)
