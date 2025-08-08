from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height = models.PositiveIntegerField("키(cm)", blank=True, null=True)
    weight = models.PositiveIntegerField("몸무게(kg)", blank=True, null=True)
    age = models.PositiveIntegerField("나이", blank=True, null=True)
    gender = models.CharField(
        "성별",
        max_length=1,
        choices=[("M", "남"), ("F", "여")],
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.user.username} 프로필'
