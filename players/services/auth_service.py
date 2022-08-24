from abc import abstractmethod

from django.core.exceptions import ValidationError


class AbstractPasswordValidator:
    @abstractmethod
    def validate(self, password, user=None):
        pass

    @abstractmethod
    def get_help_text(self):
        pass


class NoSpacePasswordAbstractValidator(AbstractPasswordValidator):
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password: str, user=None):
        for char in password:
            if char.isspace():
                raise ValidationError("Password cannot contain spaces")

    def get_help_text(self):
        return "Your password cannot contain any spaces"
