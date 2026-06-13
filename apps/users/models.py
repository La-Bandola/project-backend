from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nickname    = models.CharField(max_length=50, unique=True, blank=True, null=True)
    bio         = models.TextField(blank=True, null=True)
    photo       = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class BankAccount(models.Model):
    BANK_CHOICES = [
        ('nequi',       'Nequi'),
        ('daviplata',   'Daviplata'),
        ('bancolombia', 'Bancolombia'),
        ('otro',        'Otro'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    bank       = models.CharField(max_length=50, choices=BANK_CHOICES)
    number     = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.bank}"
