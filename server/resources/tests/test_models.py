from django.db import IntegrityError

import pytest
from resources.models import Resource


@pytest.mark.django_db
class TestResource:
    def test_model_definition(self, given_user):
        # given
        title = "Bitcoin is Sound Money"

        # when
        resource = Resource.objects.create(title=title, owner=given_user)

        # then
        assert resource.title == title
        assert resource.owner == given_user
        assert str(resource) == title
        assert repr(resource) == f"<Resource: title={title}, owner={given_user.email}>"

        # when
        with pytest.raises(IntegrityError) as excinfo:
            Resource.objects.create(title=title)

        # then
        assert "violates not-null constraint" in str(excinfo)
