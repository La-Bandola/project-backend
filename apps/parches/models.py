from django.db import models
from apps.users.models import User

class Parche(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    creator     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_parches')
    invite_code = models.CharField(max_length=12, unique=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = [
        ('creator', 'Creador'),
        ('member',  'Miembro'),
    ]

    parche     = models.ForeignKey(Parche, on_delete=models.CASCADE, related_name='memberships')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('parche', 'user')

    def __str__(self):
        return f"{self.user.username} en {self.parche.name}"