from django.forms import ModelForm, CharField, ValidationError, EmailInput, URLInput, TextInput, Textarea, HiddenInput
from write.models import MtComment


class CommentForm(ModelForm):
    captcha_code = CharField(label='Anti-spam: What is the last name of David?',
                             widget=TextInput(attrs={'size': '30', 'required': 'required'}))

    class Meta:
        model = MtComment
        widgets = {
            'author': TextInput(attrs={'size': '30', 'required': 'required'}),
            'email': EmailInput(attrs={'size': '30', 'required': 'required'}),
            'url': URLInput(attrs={'size': '30'}),
            'text': Textarea(attrs={'rows': '15', 'style': 'width:100%', 'required': 'required'}),
            'parent': HiddenInput(),
            'entry': HiddenInput()
        }
        fields = ['author', 'email', 'ip', 'text', 'url', 'parent', 'captcha_code', 'entry']

    def clean_author(self):
        """
        The author is not required on the back-end, but should be required when creating
        a comment on the site
        """
        author_passed = self.cleaned_data.get("author")
        if not author_passed:
            raise ValidationError(
                "This field is required.")
        return author_passed

    def clean_email(self):
        """
        The e-mail is not required on the back-end, but should be required when creating
        a comment on the site
        """
        email_passed = self.cleaned_data.get("email")
        if not email_passed:
            raise ValidationError(
                "This field is required.")
        return email_passed

    def clean_captcha_code(self):
        """
        This is our super basic captcha
        """
        captcha_passed = self.cleaned_data.get("captcha_code")
        if not captcha_passed.strip().lower() in ['bowie', 'jones', 'duke']:
            raise ValidationError(
                "Incorrect response to tight pants captcha riddle.")
        return captcha_passed
