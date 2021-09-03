from rest_framework.reverse import reverse
from rest_framework.test import APIClient

import pytest


class TestCsrfCookieView:
    def test_get_should_set_csrf_cookie_in_response(self):
        client = APIClient()

        # when
        response = client.get(reverse("users:get-csrf-cookie"))

        # then
        assert response.csrf_cookie_set
        assert response.cookies["csrftoken"]
        assert response.cookies["csrftoken"]["secure"]
