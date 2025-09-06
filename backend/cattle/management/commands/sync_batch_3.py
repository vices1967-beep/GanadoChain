# management/commands/sync_batch_3.py
import os
from django.core.management.base import BaseCommand
from web3 import Web3
from django.conf import settings
from cattle.models import Animal, Batch
import json

class Command(BaseCommand):
    help = 'Sincronizar el batch 3 recién creado'
    
    def handle(self, *args, **options):
        w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER))
        
        # 1. Verificar conexión
        if not w3.is_connected():
            self.stdout.write(self.style.ERROR('❌ No conectado a blockchain'))
            return
        
        # 2. Cargar ABI con ruta absoluta
        abi_path = os.path.join(settings.BASE_DIR, '..', 'artifacts', 'contracts', 'GanadoRegistryUpgradeable.sol', 'GanadoRegistryUpgradeable.json')
        try:
            with open(abi_path, 'r') as f:
                contract_data = json.load(f)
                abi = contract_data.get('abi', [])
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('❌ Archivo ABI no encontrado'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('❌ Error leyendo ABI'))
            return
        
        # 3. Verificar que tenemos la dirección del contrato
        if not hasattr(settings, 'CONTRACT_ADDRESS') or not settings.CONTRACT_ADDRESS:
            self.stdout.write(self.style.ERROR('❌ CONTRACT_ADDRESS no configurado en settings'))
            return
        
        registry = w3.eth.contract(
            address=settings.CONTRACT_ADDRESS,
            abi=abi
        )
        
        # 4. Verificar si el lote 3 existe en blockchain
        try:
            batch_count = registry.functions.loteCount().call()
            self.stdout.write(f'📊 Total lotes en blockchain: {batch_count}')
            
            if batch_count < 3:
                self.stdout.write(self.style.WARNING('⚠️ El lote 3 no existe en blockchain'))
                return
            
            # 5. Obtener datos del lote 3
            batch_data = registry.functions.lotes(3).call()
            self.stdout.write(f'📦 Datos del lote 3: {batch_data}')
            
            # 6. Debug: Ver estructura real de los datos
            lote_func = registry.functions.lotes(3)
            input_names = lote_func.abi['inputs'] if 'inputs' in lote_func.abi else []
            output_names = lote_func.abi['outputs'] if 'outputs' in lote_func.abi else []
            
            self.stdout.write(f'📝 Inputs: {input_names}')
            self.stdout.write(f'📝 Outputs: {output_names}')
            
            # 7. Procesar según la estructura real (ajusta esto)
            # Asumiendo la estructura: [loteId, ipfsHash, amount, status]
            if len(batch_data) >= 4:
                batch_id, ipfs_hash, amount, status = batch_data[:4]
                
                batch, created = Batch.objects.get_or_create(
                    name=f"Batch {batch_id} - Blockchain",
                    defaults={
                        'ipfs_hash': ipfs_hash,
                        'status': status.upper(),
                        'created_by_id': 1,
                        'origin': 'Blockchain',
                        'destination': 'Blockchain',
                        'on_blockchain': True
                    }
                )
                
                # 8. Agregar animales
                animal_token_ids = [10, 11]
                added_count = 0
                
                for token_id in animal_token_ids:
                    try:
                        animal = Animal.objects.get(token_id=token_id)
                        batch.animals.add(animal)
                        added_count += 1
                        self.stdout.write(f'✅ Animal {token_id} agregado')
                    except Animal.DoesNotExist:
                        self.stdout.write(f'⚠️ Animal {token_id} no existe')
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✅ Batch {batch_id} creado con {added_count} animales'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'✅ Batch {batch_id} actualizado con {added_count} animales'))
                    
            else:
                self.stdout.write(self.style.ERROR(f'❌ Estructura de datos inesperada: {batch_data}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())