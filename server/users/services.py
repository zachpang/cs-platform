from django.contrib.auth import authenticate
from rest_framework import exceptions

from rest_framework_simplejwt.tokens import RefreshToken


class LoginUserService:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.refresh = None
        self.access = None

    def login(self):
        user = authenticate(email=self.email, password=self.password)

        if user is None:
            # permission denied: user does not exist or bad password
            raise exceptions.AuthenticationFailed

        self.refresh = RefreshToken.for_user(user)
        self.access = self.refresh.access_token

        return user

    def set_cookies_for_response(self, response):
        cookie_settings = {
            "secure": True,
            "httponly": True,
            "samesite": "None",  # samesite cannot be set due to conflict with CORS
        }

        response.set_cookie("refresh", self.refresh, **cookie_settings)
        response.set_cookie("access", self.access, **cookie_settings)
