from django.db import models
from apps.users.models import User


class Feedback(models.Model):
    """RF_30 – Opiniones, reclamos y sugerencias del usuario."""
    TYPE_CHOICES = [
        ('opinion',     'Opinión'),
        ('reclamo',     'Reclamo'),
        ('sugerencia',  'Sugerencia'),
    ]

    STATUS_CHOICES = [
        ('pendiente',  'Pendiente'),
        ('revisado',   'Revisado'),
        ('resuelto',   'Resuelto'),
    ]

    user       = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='feedbacks'
    )
    type       = models.CharField(max_length=20, choices=TYPE_CHOICES, default='opinion')
    message    = models.TextField()
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.type}] {self.user} – {self.created_at.date()}"
