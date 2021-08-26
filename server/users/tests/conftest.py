import pytest


@pytest.fixture
def email(faker):
    return faker.company_email()


@pytest.fixture
def password(faker):
    return faker.password(length=16)
