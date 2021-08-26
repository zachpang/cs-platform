from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied

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
