from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

User._meta.get_field("email")._unique = True
User._meta.get_field("email").blank = False
User._meta.get_field("email").null = False


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class PlayerPosition(models.TextChoices):
    ATTACKER = "attacker"
    DEFENDER = "defender"
    GOALKEEPER = "goalkeeper"


class Team(models.Model):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey("auth.User", related_name="team", on_delete=models.CASCADE)
    wins = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    draws = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    loses = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    coins = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=128)
    preferred_position = models.CharField(choices=PlayerPosition.choices, max_length=32)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    overall = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    stamina_left = models.IntegerField(
        default=100, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    matches_played = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    goals_scored = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    assists_made = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name


class TeamSheet(models.Model):
    name = models.CharField(max_length=128)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    right_attacker = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="right_attacker"
    )
    left_attacker = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="left_attacker"
    )
    right_defender = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="right_defender"
    )
    left_defender = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="left_defender"
    )
    goalkeeper = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="goalkeeper"
    )

    def __str__(self):
        return self.name


class MatchResult(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    player_team = models.ForeignKey(Team, related_name="team", on_delete=models.CASCADE)
    player_score = models.IntegerField(validators=[MinValueValidator(0)])
    cpu_score = models.IntegerField(validators=[MinValueValidator(0)])
    cpu_average_overall = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)]
    )

    def __str__(self):
        return f"{self.player_score} : {self.cpu_score} ({self.cpu_average_overall})"
