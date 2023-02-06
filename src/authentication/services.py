import uuid

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

from src.users.models import User
from src.users.serializers import UserOutputSerializer
from src.users.tokens import account_activation_token
from django.conf import settings

def auth_user_get_jwt_secret_key(user: User) -> str:
    return str(user.jwt_key)


def auth_jwt_response_payload_handler(token, user=None, request=None, issued_at=None):
    """
    Default implementation. Add whatever suits you here.
    """
    user_serializer = UserOutputSerializer(user)
    if not user.is_active:
        raise ValidationError("User not verified!")
    return {"user": user_serializer.data, "token": token}


def activate_email(*, user: User, team_name: str):
    mail_subject = "Verify email for Futsal Ultimate Manager!"
    activation_url = f"{settings.FE_DOMAIN}{settings.FE_EMAIL_ACTIVATE_URL}"
    message = render_to_string(
        "template_activate_account_pretty.html",
        {
            "team_name": team_name,
            "fe_activation_url": activation_url,
            "fe_domain_url": settings.FE_DOMAIN,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if settings.DEBUG else "http",
        },
    )
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = "html"
    if not email.send():
        raise ValueError("Error sending mail!")


def auth_logout(user: User) -> User:
    user.jwt_key = uuid.uuid4()
    user.full_clean()
    user.save(update_fields=["jwt_key"])

    return user
