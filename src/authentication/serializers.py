from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator
from rest_framework import serializers


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("validators", [ASCIIUsernameValidator(), MinLengthValidator(6)])
        super().__init__(*args, **kwargs)