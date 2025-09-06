# management/commands/update_old_batches.py
from django.core.management.base import BaseCommand
from web3 import Web3
from django.conf import settings
from cattle.models import Batch
import json

class Command(BaseCommand):
    help = 'Actualizar lotes antiguos (1 y 2) con estado CREATED'
    
    def handle(self, *args, **options):
        w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER))
        
        # Cargar ABI
        with open('../artifacts/contracts/GanadoRegistryUpgradeable.sol/GanadoRegistryUpgradeable.json', 'r') as f:
            contract_data = json.load(f)
            abi = contract_data['abi']
        
        registry = w3.eth.contract(
            address=settings.CONTRACT_ADDRESS,
            abi=abi
        )
        
        # Actualizar lotes 1 y 2
        for batch_id in [1, 2]:
            try:
                # Obtener datos del lote desde blockchain
                batch_data = registry.functions.lotes(batch_id).call()
                lote_id, ipfs_hash, amount, status = batch_data
                
                # Si el estado está vacío, asignar "CREATED"
                final_status = status.upper() if status else 'CREATED'
                
                batch, created = Batch.objects.get_or_create(
                    name=f"Batch {batch_id} - Blockchain",
                    defaults={
                        'ipfs_hash': ipfs_hash,
                        'status': final_status,
                        'created_by_id': 1,  # ID del usuario vices
                        'origin': 'Blockchain',
                        'destination': 'Blockchain'
                    }
                )
                
                # Si el batch ya existía pero tenía estado diferente, actualizarlo
                if not created and batch.status != final_status:
                    batch.status = final_status
                    batch.save()
                    self.stdout.write(f'✅ Batch {batch_id} actualizado a: {final_status}')
                elif created:
                    self.stdout.write(self.style.SUCCESS(f'✅ Batch {batch_id} creado con estado: {final_status}'))
                else:
                    self.stdout.write(f'✅ Batch {batch_id} ya tiene estado: {final_status}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error con batch {batch_id}: {e}'))