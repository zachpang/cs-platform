from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

import pytest
from attr import s
from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken
from users.services import LoginUserService
from users.tests.conftest import UserFactory, email, password


@pytest.fixture
def some_user(email, password):
    return UserFactory.build(email=email, password=password)


@pytest.fixture
def refresh(some_user):
    return SimpleJWTRefreshToken.for_user(some_user)


@pytest.fixture
def access(refresh):
    return refresh.access_token


class TestLoginUserService:
    def test_init_should_set_args_correctly(self, email, password):
        # when
        service = LoginUserService(email, password)

        # then
        assert service.email == email
        assert service.password == password
        assert service.refresh is None
        assert service.access is None

        # when
        service = LoginUserService(user=some_user)

        # then
        assert service.email is None
        assert service.password is None
        assert service.user == some_user
        assert service.refresh is None
        assert service.access is None

    def test_login_should_raise_error_given_null_credentials(self):
        # when
        with pytest.raises(ValueError) as excinfo:
            LoginUserService().login()

        # then
        assert "Missing email and/or password" in str(excinfo)

    def test_login_should_call_authenticate_and_set_jwt_when_successful(
        self, email, password, mocker, some_user, refresh, access
    ):
        # given
        service = LoginUserService(email, password)

        mock_authenticate = mocker.patch(
            "users.services.authenticate",
            autospec=True,
            return_value=some_user,
        )
        mock_refresh_token_for_user = mocker.patch(
            "users.services.RefreshToken.for_user", autospec=True, return_value=refresh
        )
        mock_access_token_property = mocker.patch(
            "users.services.RefreshToken.access_token", autospec=True
        )
        mock_access_token_property.__get__ = mocker.Mock(return_value=access)

        # when
        user = service.login()

        # then
        mock_authenticate.assert_called_once_with(email=email, password=password)
        mock_refresh_token_for_user.assert_called_once_with(some_user)
        mock_access_token_property.__get__.assert_called_once()
        assert service.refresh == refresh
        assert service.access == access
        assert user == some_user

    def test_login_should_raise_exception_when_authentication_fails(
        self, email, password, mocker
    ):
        # given
        service = LoginUserService(email, password)

        mock_authenticate = mocker.patch(
            "users.services.authenticate",
            autospec=True,
            return_value=None,
        )

        # when
        with pytest.raises(AuthenticationFailed) as excinfo:
            service.login()

        # then
        mock_authenticate.assert_called_once()
        assert "Incorrect authentication credentials" in str(excinfo.value)

    def test_prepare_jwt_should_raise_error_given_null_user(self):
        # when
        with pytest.raises(ValueError) as excinfo:
            LoginUserService().login()

        # then
        assert "Missing email and/or password" in str(excinfo)

    def test_prepare_jwt_should_create_tokens(self, some_user, refresh, access, mocker):
        # given
        mock_refresh_token_for_user = mocker.patch(
            "users.services.RefreshToken.for_user", autospec=True, return_value=refresh
        )
        mock_access_token_property = mocker.patch(
            "users.services.RefreshToken.access_token", autospec=True
        )
        mock_access_token_property.__get__ = mocker.Mock(return_value=access)

        # when
        service = LoginUserService(user=some_user)
        service.prepare_jwt()

        # then
        mock_refresh_token_for_user.assert_called_once_with(some_user)
        mock_access_token_property.__get__.assert_called_once()
        assert service.refresh == refresh
        assert service.access == access

    def test_set_cookies_for_response_should_set_cookies(self, refresh, access):
        # given
        service = LoginUserService(email, password)
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
