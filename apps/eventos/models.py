from django.db import models
from apps.users.models import User
from apps.parches.models import Parche

class Evento(models.Model):
    SPLIT_CHOICES = [
        ('equal',  'Partes iguales'),
        ('custom', 'Monto personalizado'),
    ]

    parche       = models.ForeignKey(Parche, on_delete=models.CASCADE, related_name='eventos')
    name         = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    split_type   = models.CharField(max_length=10, choices=SPLIT_CHOICES, default='equal')
    responsible  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='responsible_eventos')
    receipt      = models.ImageField(upload_to='receipts/', blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.parche.name}"


class EventoParticipant(models.Model):
    evento         = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='participants')
    user           = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_owed    = models.DecimalField(max_digits=12, decimal_places=2)
    paid           = models.BooleanField(default=False)
    payment_proof  = models.ImageField(upload_to='proofs/', blank=True, null=True)
    paid_at        = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('evento', 'user')

    def __str__(self):
        return f"{self.user.username} en {self.evento.name}"


class Suscripcion(models.Model):
    parche      = models.ForeignKey(Parche, on_delete=models.CASCADE, related_name='suscripciones')
    name        = models.CharField(max_length=100)
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    cutoff_date = models.DateField()
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='responsible_suscripciones')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.parche.name}"