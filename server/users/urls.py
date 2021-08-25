from django.urls import path

from .views import CsrfCookieView

app_name = "users"

urlpatterns = [
    path("csrf-cookie/", CsrfCookieView.as_view(), name="get-csrf-cookie"),
]
