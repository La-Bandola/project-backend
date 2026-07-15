from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.finanzas.models import Transaccion
from apps.eventos.models import EventoParticipant
from apps.users.models import Notification

@receiver(post_save, sender=Transaccion)
def notify_transaccion(sender, instance, created, **kwargs):
    if created and instance.type == 'pago':
        # Notify the receiver
        if instance.to_user and instance.to_user != instance.from_user:
            message = f"Has recibido un pago de ${int(instance.amount)} de {instance.from_user.username}."
            if instance.evento:
                message += f" (Evento: {instance.evento.name})"
            Notification.objects.create(
                user=instance.to_user,
                message=message,
                parche_id=instance.parche_id if instance.parche else None,
                related_type='transaccion',
                related_id=instance.id
            )

@receiver(post_save, sender=EventoParticipant)
def notify_evento_debt(sender, instance, created, **kwargs):
    if created and instance.amount_owed > 0:
        if instance.evento.responsible and instance.user != instance.evento.responsible:
            message = f"Tienes una nueva deuda de ${int(instance.amount_owed)} en el evento '{instance.evento.name}'."
            Notification.objects.create(
                user=instance.user,
                message=message,
                parche_id=instance.evento.parche_id,
                related_type='evento',
                related_id=instance.evento.id
            )

from apps.eventos.models import Suscripcion
from apps.ahorros.models import AporteAhorro

@receiver(post_save, sender=Suscripcion)
def notify_suscripcion(sender, instance, created, **kwargs):
    if created:
        from apps.parches.models import Membership
        # Notify all members of the parche except the responsible
        members = Membership.objects.filter(parche=instance.parche)
        for member in members:
            if instance.responsible and member.user == instance.responsible:
                continue
            Notification.objects.create(
                user=member.user,
                message=f"Nueva suscripción agregada: '{instance.name}' de ${int(instance.amount)}.",
                parche_id=instance.parche.id,
                related_type='suscripcion',
                related_id=instance.id
            )

@receiver(post_save, sender=AporteAhorro)
def notify_aporte_ahorro(sender, instance, created, **kwargs):
    if created:
        # Notify the creator of the saving space, or all members? Just a general notification to members
        from apps.parches.models import Membership
        if not instance.ahorro.parche: return
        members = Membership.objects.filter(parche=instance.ahorro.parche)
        for member in members:
            if member.user == instance.user:
                continue
            Notification.objects.create(
                user=member.user,
                message=f"{instance.user.username} aportó ${int(instance.amount)} al ahorro '{instance.ahorro.name}'.",
                parche_id=instance.ahorro.parche.id,
                related_type='ahorro',
                related_id=instance.ahorro.id
            )
