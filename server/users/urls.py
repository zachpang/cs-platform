from django.urls import path

from .views import CsrfCookieView, UserViewSet

app_name = "users"

urlpatterns = [
    path("csrf-cookie/", CsrfCookieView.as_view(), name="get-csrf-cookie"),
    path("register/", UserViewSet.as_view({"post": "register"}), name="register"),
]
