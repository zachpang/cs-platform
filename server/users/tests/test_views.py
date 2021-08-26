from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

import pytest


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
        csrf_enforced_client.credentials()

        data = {"email": email, "password": password}

        # when
        response = csrf_enforced_client.post(
            reverse("users:register"),
            data,
            HTTP_X_CSRFTOKEN=csrftoken,
            HTTP_REFERER=TRUSTED_REFERER,
            secure=True,  # to mimic a HTTPS request sent by browser.
        )

        # then
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {"email": email}
