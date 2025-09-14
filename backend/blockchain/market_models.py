# backend/blockchain/market_models.py
from django.db import models
from django.conf import settings

class MarketListing(models.Model):
    animal = models.OneToOneField('cattle.Animal', on_delete=models.CASCADE, related_name='market_listing')
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='listings')
    price = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=10, default='USDC')
    listing_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    blockchain_listing_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'blockchain_market_listing'

class Trade(models.Model):
    listing = models.ForeignKey(MarketListing, on_delete=models.CASCADE, related_name='trades')
    buyer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='purchases')
    transaction_hash = models.CharField(max_length=255)
    trade_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=20, default='COMPLETED')

    class Meta:
        db_table = 'blockchain_trade'