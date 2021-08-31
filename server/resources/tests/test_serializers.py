import pytest
from resources.serializers import ResourceSerializer

from .conftest import ResourceFactory


class TestResourceSerializer:
    @pytest.mark.django_db
    def test_serialize(self):
        # given
        resource = ResourceFactory.create()

        # when
        serializer = ResourceSerializer(resource)

        # then
        assert serializer.data == {
            "id": resource.id,
            "title": resource.title,
            "owner": resource.owner.id,
        }

    def test_deserialize(self):
        # given
        title = "Bitcoin is Sound Money"

        # when
        serializer = ResourceSerializer(data={"title": title})

        # then
        assert serializer.is_valid()
