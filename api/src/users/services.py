from django.contrib.auth import authenticate as authenticate_email_password
from django.middleware.csrf import rotate_token
from rest_framework import exceptions

from rest_framework_simplejwt.tokens import RefreshToken


class LoginUserService:
    def __init__(self, request, email=None, password=None, user=None):
        self.request = request
        self.email = email
        self.password = password
        self.user = user
        self.refresh = None
        self.access = None

    def authenticate(self):
        if self.email is None or self.password is None:
            raise ValueError(
                "Missing email and/or password. Initialize service with email and password. "
            )

        user = authenticate_email_password(email=self.email, password=self.password)

        if user is None:
            # permission denied: user does not exist or bad password
            raise exceptions.AuthenticationFailed

        self.user = user

        return user

    def login(self):
        if self.user is None:
            raise ValueError(
                "Missing user. Initialize service with email, password (and call authenticate) or initialize with user instance."
            )

        self.prepare_jwt()
        rotate_token(self.request)  # reset csrf token

    def prepare_jwt(self):
        self.refresh = RefreshToken.for_user(self.user)
        self.access = self.refresh.access_token

    def set_cookies_for_response(self, response):
        cookie_settings = {
            "secure": True,
            "httponly": True,
            "samesite": "None",  # samesite cannot be set due to conflict with CORS
        }

        response.set_cookie("refresh", self.refresh, **cookie_settings)
        response.set_cookie("access", self.access, **cookie_settings)
