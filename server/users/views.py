from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView


class CsrfCookieView(APIView):
    """
    AJAX endpoint to set CSRF-token in cookie.
    - FE should make a request here
    - supply the csrf token value in the `X-CSRFToken` header
    - only required for AllowAny/unauthenticated views
    """

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        """
        Return a response to set csrf token in a cookie
        """
        return Response({"details": "CSRF cookie is set"})


class RegisterView(CreateModelMixin, GenericAPIView):
    # TODO:
    pass


class LoginView(RetrieveModelMixin, GenericAPIView):
    # TODO:
    pass
