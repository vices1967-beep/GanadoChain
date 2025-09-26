# backend/market/models.py - REEMPLAZAR contenido actual
from django.db import models

class InternationalMarket(models.Model):
    """Mercados internacionales destino"""
    country = models.CharField(max_length=100)
    import_requirements = models.JSONField()
    certification_requirements = models.JSONField()
    tariff_codes = models.JSONField()

class ExportCertificate(models.Model):
    """Certificados de exportación"""
    batch = models.ForeignKey('cattle.Batch', on_delete=models.CASCADE)
    destination_market = models.ForeignKey(InternationalMarket, on_delete=models.CASCADE)
    issued_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    certificate_data = models.JSONField()
    blockchain_hash = models.CharField(max_length=255)