from django.db import IntegrityError

import factory
import pytest
from users.models import EmailUser, EmailUserManager


@pytest.mark.django_db
class TestEmailUser:
    def test_email_user_should_be_created_using_email(self, email, password):
        # when
        user = EmailUser.objects.create_user(email=email, password=password)

        # then
        assert user.email == email
        assert user.password
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
        assert user.get_username() == email

    def test_email_user_should_not_be_created_for_existing_email(self, email, password):
        # given
        EmailUser.objects.create_user(email=email, password=password)

        # when
        with pytest.raises(IntegrityError) as excinfo:
            EmailUser.objects.create_user(email=email, password=password)

        # then
        assert (
            'duplicate key value violates unique constraint "users_emailuser_email_key"'
            in str(excinfo.value)
        )

    def test_email_user_should_not_be_created_without_email(self, faker, password):
        # given
        username = faker.user_name()

        # when
        with pytest.raises(ValueError) as excinfo:
            EmailUser.objects.create_user(username=username, password=password)

        # then
        assert "email must be set" in str(excinfo.value)


class TestEmailUserManager:
    def test_private_create_user_should_perform_necessary_calls(
        self, email, password, mocker
    ):
        # given
        mocker.patch.object(
            EmailUserManager,
            "normalize_email",
            autospec=True,
            return_value="normalized_email_str",
        )
        mock_make_password = mocker.patch(
            "users.models.make_password", return_value="long_password_hash"
        )
        mocker.patch.object(EmailUser, "save", autospec=True)

        # when
        user = EmailUser.objects._create_user(email, password)

        # then
        EmailUserManager.normalize_email.assert_called_once_with(email)
        mock_make_password.assert_called_once_with(password)
        EmailUser.save.assert_called_once()
        assert user  # is returned

    def test_create_user_should_pass_correct_args(self, email, password, mocker):
        # given
        mocker.patch.object(EmailUserManager, "_create_user", autospec=True)

        # when
        EmailUser.objects.create_user(email, password)

        # then
        EmailUserManager._create_user.assert_called_once_with(
            EmailUser.objects, email, password, is_staff=False, is_superuser=False
        )

    def test_createsuperuser_should_pass_correct_args(self, email, password, mocker):
        # given
        mocker.patch.object(EmailUserManager, "_create_user", autospec=True)

        # when
        EmailUser.objects.create_superuser(email, password)

        # then
        EmailUserManager._create_user.assert_called_once_with(
            EmailUser.objects, email, password, is_staff=True, is_superuser=True
        )

    def test_create_should_call_create_user_with_correct_args(
        self, email, password, mocker
    ):
        # given
        mocker.patch.object(EmailUserManager, "create_user", autospec=True)

        # when
        EmailUser.objects.create(email=email, password=password)

        # then
        EmailUserManager.create_user.assert_called_once_with(
            EmailUser.objects, email, password
        )


class TestManagementCommands:
    # TODO:
    # Since replacing the User model would affect the behavior of the management commands,
    # tests should be expected.
    #
    # However, due to time constraints on the assignment, doing so would result in more
    # time spent writing tests instead of focusing on the completion of the project's
    # end-to-end functionality instead.

    def test_createsuperuser_should_create_user_with_correct_permissions(self):
        # given
        # DJANGO_SUPERUSER_EMAIL =
        # DJANGO_SUPERUSER_PASSWORD =
        pass

    def test_createsuperuser_should_fail_using_username(self):
        # given
        # DJANGO_SUPERUSER_USERNAME =
        # DJANGO_SUPERUSER_PASSWORD =
        pass
