from django.db import models
from apps.users.models import User
from apps.parches.models import Parche

class Transaccion(models.Model):
    TYPE_CHOICES = [
        ('pago',    'Pago'),
        ('deuda',   'Deuda'),
        ('ingreso', 'Ingreso'),
    ]

    parche      = models.ForeignKey(Parche, on_delete=models.CASCADE, related_name='transacciones')
    from_user   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacciones_enviadas')
    to_user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacciones_recibidas')
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    concept     = models.CharField(max_length=200, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} → {self.to_user}: ${self.amount}"


class Balance(models.Model):
    parche    = models.ForeignKey(Parche, on_delete=models.CASCADE, related_name='balances')
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balances')
    amount    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('parche', 'user')

    def __str__(self):
        return f"{self.user.username} en {self.parche.name}: ${self.amount}"