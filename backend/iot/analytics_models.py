from django.db import models
from .models import IoTDevice

class DeviceAnalytics(models.Model):
    """Métricas analíticas de dispositivos IoT"""
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    total_readings = models.IntegerField(default=0)
    avg_battery_level = models.FloatField(default=0)
    connectivity_uptime = models.FloatField(default=0)  # porcentaje
    data_quality_score = models.FloatField(default=0)   # 0-100
    alerts_triggered = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['device', 'date']
        verbose_name = "Métrica de Dispositivo"
        verbose_name_plural = "Métricas de Dispositivos"