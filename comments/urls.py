from django.urls import path
from .views import CreateCommentView, RetrieveCommentView, ListCommentView

urlpatterns = [
    path("create", CreateCommentView.as_view(), name="create_comment"),
    path("", ListCommentView.as_view(), name="comment-list"),
    path("<int:pk>/", RetrieveCommentView.as_view(), name="comment-detail"),
]
app_name = "comments"
