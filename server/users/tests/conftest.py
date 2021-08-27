import factory
import pytest
from users.models import EmailUser


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
