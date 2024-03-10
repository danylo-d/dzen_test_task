from captcha.fields import CaptchaField
from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    captcha = CaptchaField()

    class Meta:
        model = Comment
        fields = ["text", "parent_id", "captcha"]

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")

        if not text:
            raise forms.ValidationError("This field is required.")

        return cleaned_data
