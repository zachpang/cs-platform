import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import exceptions, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users.services import LoginUserService

from .authentication import CsrfAuthentication
from .serializers import CreateUserSerializer, LoginUserSerializer

logger = logging.getLogger(__name__)


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


class UserViewSet(GenericViewSet):
    authentication_classes = [CsrfAuthentication]
    serializer_class = CreateUserSerializer

    def register(self, request, *args, **kwargs):
        # validate then create user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # prepare response
        response = Response(serializer.data, status=status.HTTP_201_CREATED)

        # set JWT cookie on response
        login_user_service = LoginUserService(user=user)
        login_user_service.login()
        login_user_service.set_cookies_for_response(response)

        return response


class LoginUserView(GenericViewSet):
    authentication_classes = [CsrfAuthentication]
    serializer_class = LoginUserSerializer

    def login(self, request, *args, **kwargs):
        """
        A request needs to provide registered email and password in return for JWT
        refresh and access token
        """
        # validate email and password with serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email, password = (
            serializer.validated_data["email"],
            serializer.validated_data["password"],
        )

        # pass to LoginUserService and retrieve user and jwt
        login_user_service = LoginUserService(email, password)
        try:
            user = login_user_service.authenticate()
        except exceptions.AuthenticationFailed as e:
            logger.error(f"{e.__class__} - {e.default_detail} - Email Used: {email}")
            raise

        login_user_service.login()

        # set jwt tokens on cookies
        response = Response({"details": "User authenticated successfully."})
        login_user_service.set_cookies_for_response(response)

        return response
