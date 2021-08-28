from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

import pytest
from users.views import logger

from .conftest import UserFactory


@pytest.fixture
def data(email, password):
    return {"email": email, "password": password}


TRUSTED_REFERER = "https://test-domain.com/path/to/"


@pytest.fixture
def csrf_enforced_client():
    return APIClient(enforce_csrf_checks=True)


@pytest.fixture
def csrftoken(csrf_enforced_client):
    response = csrf_enforced_client.get(reverse("users:get-csrf-cookie"))
    assert response.status_code == status.HTTP_200_OK
    return response.cookies["csrftoken"].value


@pytest.mark.django_db
class TestUserViewSet:
    def test_post_should_create_user(self, email, password):
        # given
        client = APIClient()
        data = {"email": email, "password": password}

        # when
        response = client.post(reverse("users:register"), data, secure=True)

        # then
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {"email": email}

    def test_post_should_fail_without_csrf_token_header(
        self, email, password, csrf_enforced_client
    ):
        # given
        data = {"email": email, "password": password}

        # when
        response = csrf_enforced_client.post(
            reverse("users:register"),
            data,
            HTTP_REFERER=TRUSTED_REFERER,
            secure=True,
        )

        # then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "permission_denied" == response.data["detail"].code
        assert "CSRF Failed: CSRF cookie not set." in str(response.data["detail"])

    def test_post_should_successfully_register_user_given_csrf_token_header(
        self, email, password, csrf_enforced_client, csrftoken
    ):
        # given
        data = {"email": email, "password": password}

        # when
        response = csrf_enforced_client.post(
            reverse("users:register"),
            data,
            HTTP_X_CSRFTOKEN=csrftoken,
            HTTP_REFERER=TRUSTED_REFERER,
            secure=True,
        )

        # then
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {"email": email}
        assert response.cookies["refresh"]
        assert response.cookies["access"]


class TestLoginUserView:
    def test_post_should_fail_without_csrf_token_header(
        self, email, password, csrf_enforced_client
    ):
        # given
        data = {"email": email, "password": password}

        # when
        response = csrf_enforced_client.post(
            reverse("users:login"),
            data,
            HTTP_REFERER=TRUSTED_REFERER,
            secure=True,
        )

        # then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "permission_denied" == response.data["detail"].code
        assert "CSRF Failed: CSRF cookie not set." in str(response.data["detail"])

    def test_post_should_400_given_malformed_email(self, password):
        # given
        client = APIClient()
        data = {"email": "bad_email", "password": password}

        # when
        response = client.post(reverse("users:login"), data, secure=True)

        # then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" == response.data["email"][0].code
        assert "Enter a valid email address" in str(response.data["email"][0])

    def test_post_should_log_failed_login_attempts(self, email, password, mocker):
        # given
        client = APIClient()
        data = {"email": email, "password": password}
        mock_login_method = mocker.patch(
            "users.views.LoginUserService.login",
            autospec=True,
            side_effect=AuthenticationFailed,
        )
        mock_logger_error = mocker.patch("logging.Logger.error", autospec=True)
        e = AuthenticationFailed()

        # when
        response = client.post(reverse("users:login"), data, secure=True)

        # then
        mock_login_method.assert_called_once()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "authentication_failed" == response.data["detail"].code
        assert "Incorrect authentication credentials" in str(response.data["detail"])
        mock_logger_error.assert_called_once_with(
            logger, f"{e.__class__} - {e.default_detail} - Email Used: {email}"
        )

    @pytest.mark.django_db
    def test_post_should_succeed_given_correct_inputs(
        self, email, password, csrf_enforced_client, csrftoken
    ):
        # given
        data = {"email": email, "password": password}
        user = UserFactory.create(email=email, password=password)

        # when
        response = csrf_enforced_client.post(
            reverse("users:login"),
            data,
            HTTP_X_CSRFTOKEN=csrftoken,
            HTTP_REFERER=TRUSTED_REFERER,
            secure=True,
        )

        # then
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"details": "User authenticated successfully."}
        assert response.cookies["refresh"]
        assert response.cookies["access"]
