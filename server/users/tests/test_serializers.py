from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

import pytest
from users.serializers import CreateUserSerializer


@pytest.mark.django_db
class TestCreateUserSerializer:
    def test_deserialize_should_return_correct_fields(self, email, password):
        # given
        data = {"email": email, "password": password}

        # when
        serializer = CreateUserSerializer(data=data)

        # then
        assert serializer.is_valid()
        assert serializer.validated_data == data

    def test_deserialize_is_not_valid_given_existing_email(self, email, password):
        # given
        data = {"email": email, "password": password}
        user_model = get_user_model()
        user_model.objects.create_user(**data)

        # when
        serializer = CreateUserSerializer(data=data)

        # then
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert "A user with that email address already exists" in str(excinfo.value)

    def test_deserialize_is_not_valid_given_malformed_email(self, password):
        # given
        data = {"email": "bad_email", "password": password}

        # when
        serializer = CreateUserSerializer(data=data)

        # then
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert "Enter a valid email address" in str(excinfo.value)

    def test_serialize_should_not_include_password(self, email, password):
        # given
        data = {"email": email, "password": password}

        # when
        serializer = CreateUserSerializer(data=data)
        serializer.is_valid()
        serializer.save()

        # then
        assert serializer.data["email"] == email
        assert "password" not in serializer.data


@pytest.mark.django_db
class TestLoginUserSerializer:
    def test_deserialize_should_return_correct_fields(self, email, password):
        # given
        data = {"email": email, "password": password}

        # when
        serializer = CreateUserSerializer(data=data)

        # then
        assert serializer.is_valid()
        assert serializer.validated_data == data

    def test_deserialize_is_not_valid_given_malformed_email(self, password):
        # given
        data = {"email": "bad_email", "password": password}

        # when
        serializer = CreateUserSerializer(data=data)

        # then
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
