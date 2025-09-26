# backend/core/management/commands/migrate_to_multichain.py
from django.core.management.base import BaseCommand
from cattle.multichain_models import AnimalMultichain, AnimalNFTMirror
from users.multichain_models import UserMultichainProfile
from cattle.models import Animal
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando migración a multichain...')
        
        # 1. Migrar usuarios existentes
        users = User.objects.all()
        for user in users:
            if not hasattr(user, 'multichain_profile'):
                UserMultichainProfile.objects.create(
                    user=user,
                    primary_wallet_address=user.wallet_address
                )
        
        # 2. Migrar animales existentes
        animals = Animal.objects.all()
        for animal in animals:
            if animal.token_id:  # Si ya tiene NFT en Polygon
                # Crear registro multichain
                multichain_data, created = AnimalMultichain.objects.get_or_create(
                    animal=animal,
                    defaults={'primary_network': polygon_network}
                )
                
                # Crear espejo para el NFT existente
                if created and animal.token_id:
                    AnimalNFTMirror.objects.create(
                        animal_multichain=multichain_data,
                        network=polygon_network,
                        token_id=animal.token_id,
                        mirror_transaction_hash=animal.mint_transaction_hash
                    )