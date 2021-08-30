"""
Two methods of authentication is required to secure the backend api.

For views that allow unauthenticated access, we need to prevent Login CSRF.
- Login is performed on 2 views i.e. register (UsersViewSet) and login (LoginUserView)
- FE client should perform an AJAX request to fetch csrftoken before loading User
registration or login pages.
- Supply csrftoken value in custom HTTP header (X-CSRFToken) when making register/login
requests
- upon successful login, csrftoken is reset to a new csrf token. JWT Refresh and Access
token cookies are also set.

For views that require client to be authenticated, we need to ensure JWT access token
cookie is valid.
- In addition, we need to perform csrf checks since cookies are sent on requests to the
same host that set them.
- While `samesite` setting can be applied on cookies, it only applies to newer browsers
- Since FE client may be hosted on a different domain from the api service, `samesite`
cannot be relied on.
"""

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from rest_framework_simplejwt.authentication import JWTAuthentication

REASON_NO_HTTPS = "Request scheme failed - Request is not HTTPS."


class CsrfAuthentication(SessionAuthentication):
    """
    `csrf_exempt` is applied to DRF APIView and it's subclasses by default. Therefore,
    all requests to DRF views would bypass django's CsrfViewMiddleware.

    Only session authenticated requests in DRF are enforced with csrf checks by
    default. We need csrf checks on non-session requests as well to prevent Login CSRF

    This class should ONLY be used in DRF views to enforce csrf checks on non-session
    views i.e. register, login
    """

    def authenticate(self, request):
        """
        Returns an `AnonymousUser` if the HTTPS request passes csrf check
        """
        # Reject HTTP requests since CsrfViewMiddleware allows HTTP requests
        if not request.is_secure():
            reason = REASON_NO_HTTPS
            raise PermissionDenied("CSRF Failed: %s" % reason)

        # Perform CSRF validation first
        self.enforce_csrf(request)

        # CSRF passed with anonymous user
        return (AnonymousUser(), None)


class JWTCookieAuthentication(CsrfAuthentication, JWTAuthentication):
    """
    Custom authentication that combines CSRF checks and authenticating JWT via cookies.
    - A full CSRF check is actually unnecessary. To prevent CSRF, we only need to check
    the Referer header sent from the browser is from our trusted origins, in addition
    to checking the JWT cookie.
    - However, rewriting only the logic to check Referer header would require writing
    tests as well to validate the logic's correctness.
    - Therefore, it is more secure and less costly to reuse the checks already written
    in CsrfViewMiddleware
    """

    def authenticate(self, request):
        # Perform csrf auth first
        super().authenticate(request)

        access_token = request.COOKIES.get(settings.JWT_ACCESS_TOKEN_COOKIE_NAME)

        if access_token is None:
            # no token, auth fails
            raise NotAuthenticated

        validated_token = self.get_validated_token(access_token)

        return self.get_user(validated_token), validated_token
