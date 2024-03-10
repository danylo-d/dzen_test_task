import jwt
from django.http import JsonResponse
from django.conf import settings


def jwt_required(f):
    def wrap(request, *args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return JsonResponse({"error": "No token provided"}, status=401)
        try:
            token = token.split(" ")[1]
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            return JsonResponse({"error": str(e)}, status=403)
        return f(request, *args, **kwargs)

    return wrap
