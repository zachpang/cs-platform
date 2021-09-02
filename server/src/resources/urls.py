from rest_framework.routers import SimpleRouter

from resources.views import ResourceViewSet

app_name = "resources"

router = SimpleRouter()
router.register(r"resources", ResourceViewSet, basename="resource")

urlpatterns = []

urlpatterns += router.urls
