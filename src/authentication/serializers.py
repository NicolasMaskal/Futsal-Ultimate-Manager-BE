from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator
from rest_framework import serializers


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "validators",
            [
                ASCIIUsernameValidator(message="Password can only contain ASCII characters."),
                MinLengthValidator(6, message="Ensure password has at least 6 characters."),
            ],
        )
        super().__init__(*args, **kwargs)
