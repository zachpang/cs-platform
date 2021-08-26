from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer


class CreateUserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["email", "password"]
        extra_kwargs = {"password": {"write_only": True}}
