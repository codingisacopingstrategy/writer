#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.forms import ModelForm, CharField, ValidationError, EmailInput, URLInput, TextInput, Textarea, HiddenInput
from write.models import MtComment


class CommentForm(ModelForm):
    captcha_code = CharField(label='Anti-Spam: It’s not Strasbourg but the other city where the members of ' +
                                   'the Euro parliament hang out',
                             widget=TextInput(attrs={'size': '30', 'required': 'required', 'placeholder': 'Solution…'}))

    class Meta:
        model = MtComment
        widgets = {
            'author': TextInput(attrs={'size': '30', 'required': 'required', 'placeholder': 'Name (required)'}),
            'email': EmailInput(attrs={'size': '30', 'required': 'required', 'placeholder': 'Email (required)'}),
            'url': URLInput(attrs={'size': '30', 'placeholder': 'URL'}),
            'text': Textarea(attrs={'rows': '15', 'style': 'width:100%', 'required': 'required', 'placeholder': 'Leave a comment'}),
            'parent': HiddenInput(),
            'entry': HiddenInput()
        }
        fields = ['author', 'email', 'text', 'url', 'parent', 'captcha_code', 'entry']

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
        if not captcha_passed.strip().lower() in ['bruxelles', 'brussel', 'brussels']:
            raise ValidationError(
                "Incorrect response to tight pants captcha riddle.")
        return captcha_passed
