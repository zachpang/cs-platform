from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

import factory
import pytest
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import EmailUser


@pytest.fixture
def csrf_enforced_client():
    return APIClient(enforce_csrf_checks=True)


@pytest.fixture
def csrftoken(csrf_enforced_client):
    response = csrf_enforced_client.get(reverse("users:get-csrf-cookie"))
    assert response.status_code == status.HTTP_200_OK
    return response.cookies["csrftoken"].value


TRUSTED_REFERER = "https://test-domain.com/path/to/"


@pytest.fixture
def email(faker):
    return faker.company_email()


@pytest.fixture
def password(faker):
    return faker.password(length=16)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailUser

    email = factory.Faker("company_email")
    password = factory.Faker("password", length=16)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


@pytest.fixture
def given_user(email, password):
    return UserFactory.create(email=email, password=password)


@pytest.fixture
def refresh(given_user):
    return RefreshToken.for_user(given_user)


@pytest.fixture
def access(refresh):
    return refresh.access_token


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
