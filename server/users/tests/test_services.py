from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

import pytest
from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken
from users.services import LoginUserService
from users.tests.conftest import UserFactory


@pytest.fixture
def some_user(email, password):
    return UserFactory.build(email=email, password=password)


@pytest.fixture
def post_request():
    factory = APIRequestFactory()
    return factory.post("/", {})


@pytest.fixture
def refresh(some_user):
    return SimpleJWTRefreshToken.for_user(some_user)


@pytest.fixture
def access(refresh):
    return refresh.access_token


class TestLoginUserService:
    def test_init_should_set_args_correctly(
        self, post_request, email, password, some_user
    ):
        # when
        service = LoginUserService(post_request, email, password)

        # then
        assert service.email == email
        assert service.password == password
        assert service.refresh is None
        assert service.access is None

        # when
        service = LoginUserService(post_request, user=some_user)

        # then
        assert service.email is None
        assert service.password is None
        assert service.user == some_user
        assert service.refresh is None
        assert service.access is None

    def test_authenticate_should_raise_error_given_null_credentials(self, post_request):
        # when
        with pytest.raises(ValueError) as excinfo:
            LoginUserService(post_request).authenticate()

        # then
        assert "Missing email and/or password" in str(excinfo)

    def test_authenticate_should_call_authenticate_email_password(
        self, post_request, email, password, mocker, some_user
    ):
        # given
        mock_authenticate_email_password = mocker.patch(
            "users.services.authenticate_email_password",
            autospec=True,
            return_value=some_user,
        )

        # when
        service = LoginUserService(post_request, email, password)
        user = service.authenticate()

        # then
        mock_authenticate_email_password.assert_called_once_with(
            email=email, password=password
        )
        assert user == some_user

    def test_authenticate_should_raise_exception_when_authentication_fails(
        self, post_request, email, password, mocker
    ):
        # given
        mock_authenticate_email_password = mocker.patch(
            "users.services.authenticate_email_password",
            autospec=True,
            return_value=None,
        )

        # when
        service = LoginUserService(post_request, email, password)
        with pytest.raises(AuthenticationFailed) as excinfo:
            service.authenticate()

        # then
        mock_authenticate_email_password.assert_called_once()
        assert "Incorrect authentication credentials" in str(excinfo.value)

    def test_login_should_set_necessary_credentials(
        self, mocker, post_request, some_user, refresh, access
    ):
        # given
        mock_refresh_token_for_user = mocker.patch(
            "users.services.RefreshToken.for_user", autospec=True, return_value=refresh
        )
        mock_access_token_property = mocker.patch(
            "users.services.RefreshToken.access_token", autospec=True
        )
        mock_access_token_property.__get__ = mocker.Mock(return_value=access)
        mock_rotate_token = mocker.patch("users.services.rotate_token", autospec=True)

        # when
        service = LoginUserService(post_request, user=some_user)
        service.login()

        # then
        mock_refresh_token_for_user.assert_called_once_with(some_user)
        mock_access_token_property.__get__.assert_called_once()
        mock_rotate_token.assert_called_once_with(post_request)
        assert service.refresh == refresh
        assert service.access == access

    def test_login_should_raise_error_given_null_user(self, post_request):
        # when
        with pytest.raises(ValueError) as excinfo:
            LoginUserService(post_request).login()

        # then
        assert "Missing user" in str(excinfo)

    def test_prepare_jwt_should_create_tokens(
        self, post_request, some_user, refresh, access, mocker
    ):
        # given
        mock_refresh_token_for_user = mocker.patch(
            "users.services.RefreshToken.for_user", autospec=True, return_value=refresh
        )
        mock_access_token_property = mocker.patch(
            "users.services.RefreshToken.access_token", autospec=True
        )
        mock_access_token_property.__get__ = mocker.Mock(return_value=access)

        # when
        service = LoginUserService(post_request, user=some_user)
        service.prepare_jwt()

        # then
        mock_refresh_token_for_user.assert_called_once_with(some_user)
        mock_access_token_property.__get__.assert_called_once()
        assert service.refresh == refresh
        assert service.access == access

    def test_set_cookies_for_response_should_set_cookies(
        self, post_request, some_user, refresh, access
    ):
        # given
        service = LoginUserService(post_request, user=some_user)
        service.refresh, service.access = refresh, access

        response = Response({"details": "yay!"})

        # when
        service.set_cookies_for_response(response)

        # then
        assert response.cookies["refresh"]
        assert response.cookies["refresh"].value == str(refresh)
        assert response.cookies["refresh"]["domain"] == ""
        assert response.cookies["refresh"]["path"] == "/"
        assert response.cookies["refresh"]["secure"]
        assert response.cookies["refresh"]["httponly"]
        assert response.cookies["refresh"]["samesite"] == "None"

        assert response.cookies["access"]
        assert response.cookies["access"].value == str(access)
        assert response.cookies["access"]["domain"] == ""
        assert response.cookies["access"]["path"] == "/"
        assert response.cookies["access"]["secure"]
        assert response.cookies["access"]["httponly"]
        assert response.cookies["refresh"]["samesite"] == "None"
