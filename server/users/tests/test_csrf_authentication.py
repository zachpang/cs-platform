from django.contrib.auth.models import AnonymousUser
from django.middleware.csrf import (
    REASON_BAD_REFERER,
    REASON_BAD_TOKEN,
    REASON_INSECURE_REFERER,
    REASON_MALFORMED_REFERER,
    REASON_NO_CSRF_COOKIE,
    REASON_NO_REFERER,
)
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory

import pytest
from users.authentication import REASON_NO_HTTPS, CsrfAuthentication


@pytest.fixture
def request_factory():
    return APIRequestFactory(enforce_csrf_checks=True)


@pytest.fixture
def fixture_request(request):
    return request


API_URL = "api-url/"
TRUSTED_REFERER = "https://test-domain.com/path/to/"


@pytest.fixture
def csrftoken():
    response = APIClient().get(reverse("users:get-csrf-cookie"))
    assert response.status_code == status.HTTP_200_OK
    return response.cookies["csrftoken"].value


@pytest.fixture
def data(email, password):
    return {"email": email, "password": password}


class TestCsrfAuthentication:
    @pytest.mark.parametrize(
        "secure,referer,has_csrfcookie,csrftoken,reason",
        [
            (False, TRUSTED_REFERER, True, "csrftoken", REASON_NO_HTTPS),
            (True, None, True, "csrftoken", REASON_NO_REFERER),
            (
                True,
                "https://malicious.com/",
                True,
                "csrftoken",
                REASON_BAD_REFERER % "https://malicious.com/",
            ),
            (
                True,
                "http://test-domain.com/path/to/",
                True,
                "csrftoken",
                REASON_INSECURE_REFERER,
            ),
            (
                True,
                "test-domain.com/path/to/",
                True,
                "csrftoken",
                REASON_MALFORMED_REFERER,
            ),
            (True, TRUSTED_REFERER, False, "csrftoken", REASON_NO_CSRF_COOKIE),
            (True, TRUSTED_REFERER, True, "", REASON_BAD_TOKEN),
            (True, TRUSTED_REFERER, True, "abc123", REASON_BAD_TOKEN),
        ],
    )
    def test_post_request_should_reject(
        self,
        request_factory,
        data,
        fixture_request,
        secure,
        referer,
        has_csrfcookie,
        csrftoken,
        reason,
    ):
        # given
        try:
            csrftoken = fixture_request.getfixturevalue(csrftoken)
        except pytest.FixtureLookupError:
            # when parameter passed to csrftoken is None or "abc123"
            pass

        request = request_factory.post(
            API_URL,
            data,
            secure=secure,
            HTTP_REFERER=referer,
            HTTP_X_CSRFTOKEN=csrftoken,
        )

        if has_csrfcookie:
            request.COOKIES["csrftoken"] = csrftoken

        # when
        with pytest.raises(PermissionDenied) as excinfo:
            CsrfAuthentication().authenticate(request)

        # then
        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
        assert excinfo.value.default_code == "permission_denied"
        assert reason in str(excinfo.value)

    def test_post_request_should_pass(self, request_factory, data, csrftoken):
        # given
        request = request_factory.post(
            API_URL,
            data,
            secure=True,
            HTTP_REFERER=TRUSTED_REFERER,
            HTTP_X_CSRFTOKEN=csrftoken,
        )

        request.COOKIES["csrftoken"] = csrftoken

        # when
        user, token = CsrfAuthentication().authenticate(request)

        # then
        assert user == AnonymousUser()
        assert token is None

    def test_post_request_should_pass_given_csrf_check_is_off(self, data):
        # given
        request_factory = (
            APIRequestFactory()
        )  # default __init__ does not enforce csrf check

        request = request_factory.post(API_URL, data)

        # when
        user, token = CsrfAuthentication().authenticate(request)

        # then
        assert request.csrf_processing_done
        assert user == AnonymousUser()
        assert token is None
