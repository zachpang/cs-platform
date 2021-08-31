from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from users.authentication import JWTCookieAuthentication

from .models import Resource
from .serializers import ResourceSerializer


class ResourceViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = ResourceSerializer

    def get_queryset(self):
        return Resource.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
