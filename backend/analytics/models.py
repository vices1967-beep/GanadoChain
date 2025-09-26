# backend/analytics/models.py - REEMPLAZAR contenido actual
from django.db import models

class ConsumerAnalytics(models.Model):
    """Analítica de comportamiento de consumidores"""
    date = models.DateField()
    total_scans = models.IntegerField()
    premium_upgrades = models.IntegerField()
    most_accessed_animals = models.JSONField()

class CarbonFootprint(models.Model):
    """Huella de carbono por animal/lote"""
    animal = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE)
    co2_kg = models.DecimalField(max_digits=10, decimal_places=2)
    calculation_method = models.CharField(max_length=100)
    certification = models.ForeignKey('certification.Certification', on_delete=models.CASCADE)