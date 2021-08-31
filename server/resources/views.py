from django.db.models import Count, F
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from users.authentication import JWTCookieAuthentication
from users.models import EmailUser

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
        user_with_counts = self._get_user_with_resource_count_and_quota()

        if (
            user_with_counts.quota_amount is None  # quota unset = unlimited
            or user_with_counts.resource_count < user_with_counts.quota_amount
        ):
            serializer.save(owner=self.request.user)
            return

        raise PermissionDenied("User's resources has exceeded quota.")

    def _get_user_with_resource_count_and_quota(self):
        # annotated queryset is used to benefit from DB joins and aggregation
        # instead of performing multiple queries
        return (
            EmailUser.objects.filter(id=self.request.user.id)
            .annotate(resource_count=Count("resource"), quota_amount=F("quota__amount"))
            .get()
        )
