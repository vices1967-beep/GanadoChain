# management/commands/import_animals.py
from django.core.management.base import BaseCommand
from cattle.models import Animal
from users.models import User
import json
from django.utils import timezone

class Command(BaseCommand):
    help = 'Importar animales desde backup JSON a PostgreSQL'
    
    def handle(self, *args, **options):
        # Datos de tus animales del backup
        animals_data = [
            {
                'ear_tag': 'BOV-TEST-002',
                'breed': 'Angus',
                'birth_date': '2020-05-15',
                'weight': '450.50',
                'health_status': 'HEALTHY',
                'location': 'Campo Principal',
                'ipfs_hash': 'QmExampleHash123',
                'token_id': 10,
                'mint_transaction_hash': '0x358560d2d2867b8abaeeba034b4d621cc0ed3755418fbabaafd2993ca9fbbf39',
                'nft_owner_wallet': '0xF27c409539AC5a5deB6fe0FCac5434AD9867B310'
            },
            {
                'ear_tag': 'BOV-TEST-003',
                'breed': 'Hereford',
                'birth_date': '2021-03-20',
                'weight': '380.00',
                'health_status': 'HEALTHY',
                'location': 'Campo Secundario',
                'ipfs_hash': 'QmExampleHash123',
                'token_id': 11,
                'mint_transaction_hash': '0x3c30f59aa5bddb05c85085a9396c33e0bcd77505af6552913cc167a90e30d0ba',
                'nft_owner_wallet': '0xF27c409539AC5a5deB6fe0FCac5434AD9867B310'
            }
        ]
        
        # Obtener el usuario owner (vices)
        try:
            owner = User.objects.get(username='vices')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Usuario "vices" no encontrado'))
            return
        
        for animal_data in animals_data:
            # Verificar si el animal ya existe
            if not Animal.objects.filter(token_id=animal_data['token_id']).exists():
                animal = Animal.objects.create(
                    ear_tag=animal_data['ear_tag'],
                    breed=animal_data['breed'],
                    birth_date=animal_data['birth_date'],
                    weight=animal_data['weight'],
                    health_status=animal_data['health_status'],
                    location=animal_data['location'],
                    owner=owner,
                    ipfs_hash=animal_data['ipfs_hash'],
                    token_id=animal_data['token_id'],
                    mint_transaction_hash=animal_data['mint_transaction_hash'],
                    nft_owner_wallet=animal_data['nft_owner_wallet'],
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Animal {animal.ear_tag} importado'))
            else:
                self.stdout.write(f'⚠️ Animal {animal_data["ear_tag"]} ya existe')