# backend/cattle/multichain_models.py
from django.db import models
from core.multichain.models import ChainSpecificModel

class AnimalMultichain(models.Model):
    """Extensión multichain para el modelo Animal"""
    animal = models.OneToOneField('cattle.Animal', on_delete=models.CASCADE, related_name='multichain_data')
    
    # Primary chain (donde se minteó originalmente)
    primary_network = models.ForeignKey('core.BlockchainNetwork', on_delete=models.PROTECT)
    primary_token_id = models.BigIntegerField(null=True, blank=True)
    
    # Sync status across chains
    is_cross_chain = models.BooleanField(default=False)
    last_cross_chain_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Datos Multichain de Animal"
        verbose_name_plural = "Datos Multichain de Animales"

class AnimalNFTMirror(models.Model):
    """Espejos de NFT en diferentes cadenas"""
    animal_multichain = models.ForeignKey(AnimalMultichain, on_delete=models.CASCADE, related_name='mirrors')
    network = models.ForeignKey('core.BlockchainNetwork', on_delete=models.CASCADE)
    token_id = models.BigIntegerField()
    mirror_transaction_hash = models.CharField(max_length=255)
    mirror_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['animal_multichain', 'network']
        verbose_name = "Espejo de NFT"
        verbose_name_plural = "Espejos de NFT"