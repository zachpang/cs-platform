from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

import pytest
from resources.models import Quota, Resource
from resources.tests.conftest import ResourceFactory


@pytest.fixture
def authenticated_client(given_user):
    client = APIClient()
    client.force_authenticate(user=given_user)
    return client


@pytest.mark.django_db
class TestResourceViewSet:
    def test_create_should_include_user_as_resource_owner(
        self, authenticated_client, given_user
    ):
        # given
        data = {"title": "Bitcoin is Sound Money"}

        # when
        response = authenticated_client.post(reverse("resources:resource-list"), data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Resource.objects.get(owner=given_user).title == data["title"]

    @pytest.mark.parametrize(
        "resource_count,quota_amount,status",
        [
            (3, None, status.HTTP_201_CREATED),  # quota unset = unlimited
            (3, 0, status.HTTP_403_FORBIDDEN),  # quota set to 0 = no resource
            (2, 3, status.HTTP_201_CREATED),
            (3, 3, status.HTTP_403_FORBIDDEN),
            (4, 3, status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_given_existing_resources_and_quota(
        self, authenticated_client, given_user, resource_count, quota_amount, status
    ):
        # given
        resources = ResourceFactory.create_batch(resource_count, owner=given_user)
        quota = (
            Quota.objects.create(amount=quota_amount, user=given_user)
            if quota_amount is not None
            else None
        )
        data = {"title": "Bitcoin is Sound Money"}

        # when
        response = authenticated_client.post(reverse("resources:resource-list"), data)

        assert response.status_code == status
        assert Resource.objects.get(title=data["title"]) if status == 201 else True

    def test_list_should_return_user_resources_only(
        self, authenticated_client, given_user
    ):
        # given
        user_resources = ResourceFactory.create_batch(3, owner=given_user)
        ResourceFactory.create_batch(5)

        # when
        response = authenticated_client.get(reverse("resources:resource-list"))

        # then
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == len(user_resources)
        assert all(resource["owner"] == given_user.id for resource in response.data)

    def test_retrieve_should_return_user_resource_by_pk(
        self, authenticated_client, given_user
    ):
        # given
        user_resource = ResourceFactory.create(owner=given_user)
        other_resources = ResourceFactory.create_batch(5)

        # when
        response = authenticated_client.get(
            reverse("resources:resource-detail", args=[user_resource.id])
        )

        # then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == user_resource.id
        assert response.data["title"] == user_resource.title
        assert response.data["owner"] == user_resource.owner.id

        # when
        response = authenticated_client.get(
            reverse("resources:resource-detail", args=[other_resources[0].id])
        )

        # then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not_found" == response.data["detail"].code

    def test_destroy_should_delete_user_resource_by_pk(
        self, authenticated_client, given_user
    ):
        # given
        user_resource = ResourceFactory.create(owner=given_user)
        other_resources = ResourceFactory.create_batch(5)

        # when
        response = authenticated_client.delete(
            reverse("resources:resource-detail", args=[user_resource.id])
        )

        # then
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
        assert len(Resource.objects.filter(id=user_resource.id)) == 0

        # when
        response = authenticated_client.delete(
            reverse("resources:resource-detail", args=[other_resources[0].id])
        )

        # then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not_found" == response.data["detail"].code


@pytest.mark.django_db
class TestResourceViewSetAuthenticationIntegration:
    @pytest.mark.parametrize(
        "method,view_name,has_params,has_data,status",
        [
            ("post", "resources:resource-list", False, True, status.HTTP_201_CREATED),
            ("get", "resources:resource-list", False, False, status.HTTP_200_OK),
            ("get", "resources:resource-detail", True, False, status.HTTP_200_OK),
            (
                "delete",
                "resources:resource-detail",
                True,
                False,
                status.HTTP_204_NO_CONTENT,
            ),
        ],
    )
    def test_methods_should_succeed_given_full_credentials(
        self,
        credentialed_client,
        given_user,
        method,
        view_name,
        has_params,
        has_data,
        status,
    ):
        # given
        data = None
        args = []
        if has_data:
            data = {"title": "Bitcoin is Sound Money"}
        if has_params:
            resource = ResourceFactory.create(owner=given_user)
            args = [resource.id]

        # when
        perform_call = getattr(credentialed_client, method)
        response = perform_call(reverse(view_name, args=args), data, secure=True)

        # then
        assert response.status_code == status
