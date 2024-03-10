from django.contrib import admin
from django.conf import settings

from users.models import User

admin.site.register(User)
