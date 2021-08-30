from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.test import APIRequestFactory

import pytest
from rest_framework_simplejwt.exceptions import InvalidToken
from users.authentication import JWTCookieAuthentication


class TestJWTCookieAuthentication:
    def test_authenticate_given_valid_access_token(self, mocker, given_user, access):
        # given
        request = APIRequestFactory().post("/", {}, secure=True)
        request.COOKIES[settings.JWT_ACCESS_TOKEN_COOKIE_NAME] = str(access)

        mock_csrf_authenticate = mocker.patch(
            "users.authentication.CsrfAuthentication.authenticate", autospec=True
        )
        mock_get_validated_token = mocker.patch(
            "users.authentication.JWTAuthentication.get_validated_token",
            autospec=True,
            return_value=access,
        )
        mock_get_user = mocker.patch(
            "users.authentication.JWTAuthentication.get_user",
            autospec=True,
            return_value=given_user,
        )

        # when
        auth_instance = JWTCookieAuthentication()
        user, token = auth_instance.authenticate(request)

        # then
        mock_csrf_authenticate.assert_called_once_with(auth_instance, request)
        mock_get_validated_token.assert_called_once_with(auth_instance, str(access))
        mock_get_user.assert_called_once_with(auth_instance, access)
        assert user == given_user
        assert token == access

    def test_authenticate_given_no_access_token(self, mocker):
        # given
        request = APIRequestFactory().post("/", {}, secure=True)

        mock_csrf_authenticate = mocker.patch(
            "users.authentication.CsrfAuthentication.authenticate", autospec=True
        )

        # when
        auth_instance = JWTCookieAuthentication()

        with pytest.raises(NotAuthenticated) as excinfo:
            auth_instance.authenticate(request)

        # then
        mock_csrf_authenticate.assert_called_once_with(auth_instance, request)
        assert "Authentication credentials were not provided" in str(excinfo.value)
        assert "not_authenticated" == excinfo.value.get_codes()
        assert status.HTTP_401_UNAUTHORIZED == excinfo.value.status_code

    def test_authenticate_given_invalid_token(self, mocker):
        # given
        invalid_token = "invalid_token"
        request = APIRequestFactory().post("/", {}, secure=True)
        request.COOKIES[settings.JWT_ACCESS_TOKEN_COOKIE_NAME] = invalid_token

        mock_csrf_authenticate = mocker.patch(
            "users.authentication.CsrfAuthentication.authenticate", autospec=True
        )
        mock_get_validated_token = mocker.patch(
            "users.authentication.JWTAuthentication.get_validated_token",
            autospec=True,
            side_effect=InvalidToken,
        )

        # when
        auth_instance = JWTCookieAuthentication()
        with pytest.raises(InvalidToken) as excinfo:
            auth_instance.authenticate(request)

        # then
        mock_csrf_authenticate.assert_called_once_with(auth_instance, request)
        mock_get_validated_token.assert_called_once_with(auth_instance, invalid_token)
        assert "Token is invalid or expired" in str(excinfo.value)
        assert "token_not_valid" == excinfo.value.get_codes()["code"]
        assert status.HTTP_401_UNAUTHORIZED == excinfo.value.status_code
