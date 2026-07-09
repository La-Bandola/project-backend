from django.db import models
from apps.users.models import User
from apps.parches.models import Parche


class EspacioAhorro(models.Model):
    """RF_20 – Espacio de ahorro colectivo dentro de un parche."""
    parche          = models.ForeignKey(Parche, on_delete=models.CASCADE, related_name='espacios_ahorro')
    creator         = models.ForeignKey(User,   on_delete=models.CASCADE, related_name='espacios_ahorro_creados')
    name            = models.CharField(max_length=100)
    description     = models.TextField(blank=True, null=True)
    goal_amount     = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_date     = models.DateField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.parche.name}"

    @property
    def progress_percentage(self):
        if self.goal_amount <= 0:
            return 0
        return round((self.current_amount / self.goal_amount) * 100, 2)


class AporteAhorro(models.Model):
    """RF_20 – Aporte individual a un espacio de ahorro."""
    espacio    = models.ForeignKey(EspacioAhorro, on_delete=models.CASCADE, related_name='aportes')
    user       = models.ForeignKey(User,          on_delete=models.CASCADE, related_name='aportes_ahorro')
    amount     = models.DecimalField(max_digits=12, decimal_places=2)
    note       = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.espacio.name}: ${self.amount}"
