from django.db import IntegrityError

import pytest
from resources.models import Quota, Resource


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


@pytest.mark.django_db
class TestQuota:
    def test_model_definition(self, given_user):
        # given
        amount = 3

        # when
        quota = Quota.objects.create(amount=amount, user=given_user)

        # then
        assert quota.amount == amount
        assert quota.user == given_user
        assert given_user.quota.amount == amount
        assert str(quota) == str(amount)
        assert repr(quota) == f"<Quota: amount={amount}, user={given_user.email}>"

        # when
        with pytest.raises(IntegrityError) as excinfo:
            Quota.objects.create(amount=amount, user=given_user)

        # then
        assert "duplicate key value violates unique constraint" in str(excinfo)

    def test_create_default_amount(self, given_user):
        # when
        quota = Quota.objects.create(user=given_user)

        # then
        assert quota.amount == 0

    def test_create_negative_integer_amount(self, given_user):
        # given
        amount = -3

        # when
        with pytest.raises(IntegrityError) as excinfo:
            Quota.objects.create(amount=amount, user=given_user)

        # then
        assert "violates check constraint" in str(excinfo)
