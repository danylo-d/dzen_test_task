from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("User"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("Parent comment"),
    )
    text = models.TextField(verbose_name=_("Text"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return f'Comment by {self.user.username} on {self.created_at.strftime("%Y-%m-%d %H:%M")}'

    @property
    def rate(self):
        return self.likes.count() - self.dislikes.count()


class Vote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name=_("User"),
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name=_("Comment"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        abstract = True
        unique_together = ("user", "comment")
        verbose_name = _("Vote")
        verbose_name_plural = _("Votes")


class Like(Vote):
    class Meta(Vote.Meta):
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")


class Dislike(Vote):
    class Meta(Vote.Meta):
        verbose_name = _("Dislike")
        verbose_name_plural = _("Dislikes")


class Metric(models.Model):
    action = models.CharField(max_length=100)
    user_id = models.IntegerField()
    comment_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
