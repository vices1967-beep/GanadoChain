# backend/certification/models.py - ¡CREAR ESTE ARCHIVO!
from django.db import models

class GlobalCertificationBody(models.Model):
    """Organismos de certificación global (ISO, GlobalG.A.P., etc.)"""
    name = models.CharField(max_length=200)
    standards = models.JSONField()  # ['ISO22000', 'GLOBALGAP']
    accreditation_level = models.CharField(max_length=50)
    countries = models.JSONField()  # Países donde opera
    is_active = models.BooleanField(default=True)

class Certification(models.Model):
    """Certificación multi-nivel para productores/frigoríficos"""
    GRADES = [('A', 'Premium'), ('B', 'Standard'), ('C', 'Basic')]
    
    certified_entity = models.ForeignKey('users.User', on_delete=models.CASCADE)
    certification_body = models.ForeignKey(GlobalCertificationBody, on_delete=models.CASCADE)
    standard = models.CharField(max_length=50)
    grade = models.CharField(max_length=1, choices=GRADES)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    blockchain_proof = models.CharField(max_length=255)
    metadata_ipfs = models.CharField(max_length=255)

class Auditor(models.Model):
    """Auditores públicos/privados"""
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100)
    certification_bodies = models.ManyToManyField(GlobalCertificationBody)