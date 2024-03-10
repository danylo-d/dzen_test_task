from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DetailView
from comments.forms import CommentForm
from comments.models import Comment, Like, Dislike
from rabbitmq_utils.messaging import send_metric
from users.decorators import jwt_required
from django.core.cache import cache


@method_decorator(jwt_required, name="dispatch")
class CreateCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "comments/create_comment.html"
    success_url = reverse_lazy("comments:comment-list")

    def get_initial(self):
        initial = super().get_initial()
        initial["parent_id"] = self.request.GET.get("parent_id", "")
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        parent_id = form.cleaned_data.get("parent_id")
        if parent_id:
            form.instance.parent_id = parent_id
        form.save()

        comments_cache = Comment.objects.all()
        cache.set("comments_cache", comments_cache, timeout=60 * 15)
        send_metric(
            "comment_created",
            {"user_id": form.instance.user.id, "comment_id": form.instance.id},
        )
        return super().form_valid(form)


@method_decorator(jwt_required, name="dispatch")
class ListCommentView(ListView):
    model = Comment
    template_name = "comments/comment_list.html"
    context_object_name = "comments"

    def get_queryset(self):
        comments_cache = cache.get("comments_cache")

        if not comments_cache:
            comments = Comment.objects.all()
            cache.set("comments_cache", comments, timeout=60 * 15)

        return comments_cache


@method_decorator(jwt_required, name="dispatch")
class RetrieveCommentView(DetailView):
    model = Comment
    template_name = "comments/comment_detail.html"
    context_object_name = "comment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["child_comments"] = self.object.replies.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        action = request.POST.get("action")
        if action == "like":
            self.vote(Like, request.user, self.object)
        elif action == "dislike":
            self.vote(Dislike, request.user, self.object)

        return redirect("comments:comment-detail", pk=self.object.pk)

    def vote(self, model, user, comment):
        vote, created = model.objects.get_or_create(user=user, comment=comment)
        if not created:
            messages.error(self.request, "You have already voted on this comment.")
        else:
            messages.success(self.request, "Your vote has been recorded.")
            comments_cache = Comment.objects.all()
            cache.set("comments_cache", comments_cache, timeout=60 * 15)
            send_metric("comment_voted", {"user_id": user.id, "comment_id": comment.id})
