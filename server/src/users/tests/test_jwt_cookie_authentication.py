from django.conf import settings
from django.urls import path
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

import pytest
from config.urls import urlpatterns
from conftest import TRUSTED_REFERER
from rest_framework_simplejwt.exceptions import InvalidToken
from users.authentication import JWTCookieAuthentication


class TestJWTCookieAuthentication:
    @pytest.mark.django_db
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


"""
Integration Tests with DRF APIView
"""


@pytest.fixture
def credentialed_client(csrftoken, csrf_enforced_client, refresh, access):
    csrf_enforced_client.defaults.update(
        HTTP_REFERER=TRUSTED_REFERER, HTTP_X_CSRFTOKEN=csrftoken
    )

    cookie_settings = {"secure": True, "httponly": True, "samesite": "None"}

    csrf_enforced_client.cookies["refresh"] = str(refresh)
    csrf_enforced_client.cookies["refresh"].update(cookie_settings)
    csrf_enforced_client.cookies["access"] = str(access)
    csrf_enforced_client.cookies["access"].update(cookie_settings)

    return csrf_enforced_client


class SomeAPIView(APIView):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return Response(
            "authenticated request received by view", status=status.HTTP_200_OK
        )


urlpatterns += [path("test-view/", SomeAPIView.as_view())]


@pytest.mark.urls(__name__)
@pytest.mark.django_db
class TestJWTCookieAuthenticationAPIViewIntegration:
    def test_post_should_succeed_given_full_credentials(self, credentialed_client):
        # when
        response = credentialed_client.post("/test-view/", {}, secure=True)

        # then
        assert response.status_code == status.HTTP_200_OK
        assert response.data == "authenticated request received by view"
