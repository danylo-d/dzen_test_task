from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("comments/", include("comments.urls", namespace="comments")),
    path("user/", include("users.urls", namespace="users")),
    path("captcha/", include("captcha.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
