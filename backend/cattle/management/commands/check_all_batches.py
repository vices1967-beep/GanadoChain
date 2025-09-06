# cattle/management/commands/check_all_batches.py
import os
import json
from django.core.management.base import BaseCommand
from web3 import Web3
from django.conf import settings
from cattle.models import Batch

class Command(BaseCommand):
    help = 'Verifica todos los lotes de la base de datos con blockchain'
    
    def handle(self, *args, **options):
        self.stdout.write("🔍 VERIFICANDO LOTES vs BLOCKCHAIN")
        self.stdout.write("==========================================")
        
        try:
            # 1. Conectar a blockchain
            w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER))
            if not w3.is_connected():
                self.stdout.write(self.style.ERROR('❌ No conectado a blockchain'))
                return
            
            # 2. Cargar ABI
            abi_path = os.path.join(settings.BASE_DIR, '..', 'artifacts', 'contracts', 'GanadoRegistryUpgradeable.sol', 'GanadoRegistryUpgradeable.json')
            with open(abi_path, 'r') as f:
                contract_data = json.load(f)
                abi = contract_data.get('abi', [])
            
            # 3. Configurar contrato
            registry = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=abi)
            
            # 4. Obtener el próximo ID de lote (nextLoteId - 1 = cantidad actual)
            next_lote_id = registry.functions.nextLoteId().call()
            batch_count = next_lote_id - 1  # nextLoteId es el próximo ID disponible
            
            self.stdout.write(f'📊 Próximo ID de lote: {next_lote_id}')
            self.stdout.write(f'📊 Lotes existentes en blockchain: {batch_count}')
            
            # 5. Verificar cada batch
            for batch_id in range(1, 4):
                self.stdout.write(f"\n📦 VERIFICANDO BATCH {batch_id}")
                self.stdout.write("-" * 40)
                
                try:
                    # Obtener batch de BD
                    db_batch = Batch.objects.get(id=batch_id)
                    self.stdout.write(f'🏷️  Nombre BD: {db_batch.name}')
                    self.stdout.write(f'📊 Estado BD: {db_batch.status}')
                    self.stdout.write(f'🌐 IPFS BD: {db_batch.ipfs_hash}')
                    self.stdout.write(f'📝 TX Hash BD: {db_batch.blockchain_tx}')
                    
                    # Verificar si existe en blockchain
                    if batch_id <= batch_count:
                        # Obtener datos de blockchain
                        bc_data = registry.functions.lotes(batch_id).call()
                        
                        # Estructura esperada: [loteId, ipfsHash, amount, status]
                        self.stdout.write(f'🏷️  ID Blockchain: {bc_data[0]}')
                        self.stdout.write(f'🌐 IPFS Blockchain: {bc_data[1]}')
                        self.stdout.write(f'💰 Cantidad Blockchain: {bc_data[2]}')
                        self.stdout.write(f'📊 Estado Blockchain: {bc_data[3]}')
                        
                        # Verificar coincidencias
                        matches = True
                        issues = []
                        
                        # Verificar IPFS
                        if db_batch.ipfs_hash != bc_data[1]:
                            matches = False
                            issues.append(f'IPFS diferente: BD="{db_batch.ipfs_hash}" vs BC="{bc_data[1]}"')
                        
                        # Verificar estado (convertir a mayúsculas para comparar)
                        db_status = (db_batch.status or '').upper()
                        bc_status = (bc_data[3] or '').upper()
                        if db_status != bc_status:
                            matches = False
                            issues.append(f'Estado diferente: BD="{db_status}" vs BC="{bc_status}"')
                        
                        # Mostrar resultado
                        if matches:
                            self.stdout.write(self.style.SUCCESS('✅ Coincide con blockchain'))
                        else:
                            self.stdout.write(self.style.ERROR('❌ NO coincide con blockchain'))
                            for issue in issues:
                                self.stdout.write(f'   ⚠️ {issue}')
                                
                        # Verificar animales asignados
                        try:
                            animal_count = 0
                            self.stdout.write('🐄 Animales en blockchain:')
                            # Verificar algunos tokens posibles
                            for token_id in [10, 11]:  # Los que sabemos que existen
                                try:
                                    lote_id = registry.functions.animalToLote(token_id).call()
                                    if lote_id == batch_id:
                                        self.stdout.write(f'   ✅ Token {token_id}: asignado a este lote')
                                        animal_count += 1
                                    elif lote_id > 0:
                                        self.stdout.write(f'   ❌ Token {token_id}: asignado a lote {lote_id}')
                                    else:
                                        self.stdout.write(f'   ⚪ Token {token_id}: no asignado')
                                except:
                                    self.stdout.write(f'   ❓ Token {token_id}: error al verificar')
                            
                            self.stdout.write(f'📊 Total animales en lote: {animal_count}')
                            
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'⚠️ Error verificando animales: {e}'))
                            
                    else:
                        self.stdout.write('🔍 Batch no existe en blockchain')
                        # Verificar si debería existir
                        if db_batch.blockchain_tx:
                            self.stdout.write(self.style.WARNING('⚠️ Tiene TX hash pero no existe en blockchain'))
                        
                except Batch.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'⚠️ Batch {batch_id} no existe en BD'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error verificando batch {batch_id}: {e}'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error general: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
        
        self.stdout.write("\n🎉 VERIFICACIÓN COMPLETADA")
        self.stdout.write("==========================================")