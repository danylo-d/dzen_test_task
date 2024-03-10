from django.urls import path
from .views import LoginView, RefreshTokenView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh-token/", RefreshTokenView.as_view(), name="refresh_token"),
]

app_name = "users"
