from django.db import models
from apps.users.models import User
from apps.parches.models import Parche


class Evento(models.Model):
    SPLIT_CHOICES = [
        ('equal',  'Partes iguales'),
        ('custom', 'Monto personalizado'),
    ]

    STATUS_CHOICES = [
        ('active',  'Activo'),
        ('waiting', 'En espera'),   # RF_16 – ventana de espera
        ('closed',  'Cerrado'),
    ]

    parche          = models.ForeignKey(Parche, on_delete=models.CASCADE, related_name='eventos')
    name            = models.CharField(max_length=100)
    total_amount    = models.DecimalField(max_digits=12, decimal_places=2)
    split_type      = models.CharField(max_length=10, choices=SPLIT_CHOICES, default='equal')
    responsible     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='responsible_eventos')
    pay_immediately = models.BooleanField(default=True)   # RF_15
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')  # RF_16
    receipt         = models.ImageField(upload_to='receipts/', blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

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

    @property
    def amount_paid(self):
        from apps.finanzas.models import Transaccion
        from django.db.models import Sum
        total = Transaccion.objects.filter(
            evento=self.evento,
            from_user=self.user,
            type='pago'
        ).aggregate(t=Sum('amount'))['t']
        return float(total) if total else 0.0

    @property
    def is_fully_paid(self):
        # We also check if amount_owed <= amount_paid
        # to dynamically determine if it's fully paid
        if self.evento.responsible and self.evento.responsible == self.user:
            return True
        return self.amount_paid >= float(self.amount_owed)


class Suscripcion(models.Model):
    parche      = models.ForeignKey(Parche, on_delete=models.CASCADE, related_name='suscripciones')
    name        = models.CharField(max_length=100)
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    cutoff_date = models.DateField()
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='responsible_suscripciones')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.parche.name}"