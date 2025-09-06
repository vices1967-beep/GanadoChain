# management/commands/sync_batch_3.py
from django.core.management.base import BaseCommand
from web3 import Web3
from django.conf import settings
from cattle.models import Animal, Batch
import json

class Command(BaseCommand):
    help = 'Sincronizar el batch 3 recién creado'
    
    def handle(self, *args, **options):
        w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER))
        
        # Cargar ABI correctamente
        with open('../artifacts/contracts/GanadoRegistryUpgradeable.sol/GanadoRegistryUpgradeable.json', 'r') as f:
            contract_data = json.load(f)
            abi = contract_data['abi']  # ← Extraer solo la parte del ABI
        
        registry = w3.eth.contract(
            address=settings.CONTRACT_ADDRESS,
            abi=abi  # ← Usar solo el array ABI, no el JSON completo
        )
        
        # Verificar batch 3
        try:
            batch_data = registry.functions.lotes(3).call()
            
            # Estructura: [loteId, ipfsHash, amount, status] 
            # (basado en el ABI: uint256 loteId, string ipfsHash, uint256 amount, string status)
            batch_id, ipfs_hash, amount, status = batch_data
            
            batch, created = Batch.objects.get_or_create(
                name=f"Batch {batch_id} - Blockchain",
                defaults={
                    'ipfs_hash': ipfs_hash,
                    'status': status.upper(),  # Convertir a mayúsculas para coincidir con choices
                    'created_by_id': 1,   # ID del usuario vices
                    'origin': 'Blockchain',
                    'destination': 'Blockchain'
                }
            )
            
            # Agregar animales al batch (token IDs 10 y 11)
            animal_token_ids = [10, 11]
            
            for token_id in animal_token_ids:
                try:
                    animal = Animal.objects.get(token_id=token_id)
                    batch.animals.add(animal)
                    self.stdout.write(f'✅ Animal {token_id} agregado al batch')
                except Animal.DoesNotExist:
                    self.stdout.write(f'⚠️ Animal con token_id {token_id} no encontrado')
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Batch {batch_id} creado y sincronizado'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ Batch {batch_id} actualizado'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error sincronizando batch 3: {e}'))