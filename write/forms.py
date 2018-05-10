from django.forms import ModelForm, forms
from write.models import MtComment


class CommentForm(ModelForm):
    captcha_code = forms.TextInput()

    class Meta:
        model = MtComment
        fields = ['author', 'email', 'ip', 'text', 'url', 'parent', 'entry']

