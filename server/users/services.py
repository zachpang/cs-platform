from django.contrib.auth import authenticate
from rest_framework import exceptions

from rest_framework_simplejwt.tokens import RefreshToken


class LoginUserService:
    def __init__(self, email=None, password=None, user=None):
        self.email = email
        self.password = password
        self.user = user
        self.refresh = None
        self.access = None

    def login(self):
        if self.email is None or self.password is None:
            raise ValueError(
                "Missing email and/or password. Initialize service with email and password. "
            )

        user = authenticate(email=self.email, password=self.password)

        if user is None:
            # permission denied: user does not exist or bad password
            raise exceptions.AuthenticationFailed

        self.user = user
        self.prepare_jwt()

        return user

    def prepare_jwt(self):
        if self.user is None:
            raise ValueError("Missing user. Initialize service with user instance.")

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
