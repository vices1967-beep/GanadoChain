# backend/analytics/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from consumer.models import QRCodeScan
from .models import ConsumerAnalytics

@receiver(post_save, sender=QRCodeScan)
def update_analytics_on_scan(sender, instance, created, **kwargs):
    """Actualizar analíticas cuando se escanea un QR"""
    if created:
        # Actualizar analítica del día
        today = timezone.now().date()
        analytics, _ = ConsumerAnalytics.objects.get_or_create(date=today)
        analytics.total_qr_scans += 1
        analytics.save()