from django.db import models

class SystemMetrics(models.Model):
    """Métricas del sistema para dashboard"""
    date = models.DateField(unique=True)
    total_animals = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    total_transactions = models.IntegerField(default=0)
    active_devices = models.IntegerField(default=0)
    average_gas_price = models.FloatField(default=0)
    blockchain_events = models.IntegerField(default=0)
    health_alerts = models.IntegerField(default=0)
    
    # Métricas por tipo de usuario
    producer_count = models.IntegerField(default=0)
    vet_count = models.IntegerField(default=0)
    frigorifico_count = models.IntegerField(default=0)
    auditor_count = models.IntegerField(default=0)
    
    # Métricas de rendimiento
    avg_response_time = models.FloatField(default=0)
    error_rate = models.FloatField(default=0)
    system_uptime = models.FloatField(default=100.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Métrica del Sistema"
        verbose_name_plural = "Métricas del Sistema"
        ordering = ['-date']