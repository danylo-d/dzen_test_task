from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
import jwt
from django.conf import settings
from django.contrib import messages

from users.forms import TokenForm


def create_token(user):
    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(days=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class LoginView(View):
    template_name = "users/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("comments:comment-list")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.redirect_authenticated_user:
            return HttpResponseRedirect(self.success_url)
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                token = create_token(user)
                request.session["jwt_token"] = token
                return JsonResponse({"token": token}, status=200)
            else:
                messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {"form": form})


class RefreshTokenView(View):
    template_name = "users/refresh_token.html"
    form_class = TokenForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get("token")
            try:
                leeway = timedelta(days=1)
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"],
                    options={"leeway": leeway},
                )
                user_id = payload["user_id"]

                expiration = datetime.utcfromtimestamp(payload["exp"])
                if datetime.utcnow() > expiration:
                    new_payload = {
                        "user_id": user_id,
                        "exp": datetime.utcnow() + timedelta(days=1),
                    }
                    new_token = jwt.encode(
                        new_payload, settings.SECRET_KEY, algorithm="HS256"
                    )
                    return JsonResponse({"token": new_token})
                else:
                    new_payload = {
                        "user_id": user_id,
                        "exp": datetime.utcnow() + timedelta(days=1),
                    }
                    new_token = jwt.encode(
                        new_payload, settings.SECRET_KEY, algorithm="HS256"
                    )
                    return JsonResponse({"token": new_token})

            except jwt.ExpiredSignatureError:
                form.add_error(
                    "token", "Token expired and is outside the grace period."
                )
            except jwt.InvalidTokenError:
                form.add_error("token", "Invalid Token")
        return render(request, self.template_name, {"form": form})
