from django.urls import path

from .views import CsrfCookieView, LoginUserView, UserViewSet

app_name = "users"

urlpatterns = [
    path("csrf-cookie/", CsrfCookieView.as_view(), name="get-csrf-cookie"),
    path("register/", UserViewSet.as_view({"post": "register"}), name="register"),
    path("login/", LoginUserView.as_view({"post": "login"}), name="login"),
]
