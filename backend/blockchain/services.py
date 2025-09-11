from django.conf import settings
from web3 import Web3
import json
from pathlib import Path
import os
import time
from eth_utils import event_abi_to_log_topic
from web3._utils.events import get_event_data
from cattle.models import Animal
from users.models import User
from iot.models import IoTDevice
from cattle.models import AnimalHealthRecord, HealthStatus
# Al inicio del archivo services.py, busca o añade:
import logging
logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
        
        # Verificar que la private key esté configurada
        if not settings.ADMIN_PRIVATE_KEY:
            raise ValueError("ADMIN_PRIVATE_KEY no está configurada en las variables de entorno")
        
        try:
            self.admin_account = self.w3.eth.account.from_key(settings.ADMIN_PRIVATE_KEY)
            self.wallet_address = self.admin_account.address
            self.private_key = settings.ADMIN_PRIVATE_KEY
        except Exception as e:
            raise ValueError(f"Error al cargar la cuenta admin: {e}")
        
        self.load_contracts()
    
    def load_contracts(self):
        """Cargar contratos usando ABI completo desde artifacts de Hardhat"""
        try:
            # ✅ Ruta CORREGIDA: artifacts están en GanadoChain/artifacts/ (no en hardhat/artifacts/)
            base_path = Path(__file__).resolve().parent.parent.parent / "artifacts" / "contracts"
            
            print(f"📁 Buscando artifacts en: {base_path}")
            
            if not base_path.exists():
                raise ValueError(f"No se encontró la carpeta de artifacts: {base_path}")
            
            # Debug: mostrar contratos disponibles
            contracts = list(base_path.glob("*"))
            print("📋 Contratos encontrados:")
            for contract in contracts:
                print(f"  - {contract.name}")
            
            # Cargar ABI de GanadoTokenUpgradeable
            token_abi_path = base_path / "GanadoTokenUpgradeable.sol" / "GanadoTokenUpgradeable.json"
            print(f"📄 Buscando token ABI en: {token_abi_path}")
            
            if not token_abi_path.exists():
                # Buscar cualquier archivo de token
                token_files = list(base_path.glob("**/*GanadoToken*.json"))
                if token_files:
                    token_abi_path = token_files[0]
                    print(f"📄 Usando token ABI alternativo: {token_abi_path}")
                else:
                    raise FileNotFoundError(f"No se encontró el artifact de GanadoToken: {token_abi_path}")
            
            with open(token_abi_path) as f:
                token_artifact = json.load(f)
                token_abi = token_artifact["abi"]
            
            self.token_contract = self.w3.eth.contract(
                address=settings.GANADO_TOKEN_ADDRESS,
                abi=token_abi
            )
            print("✅ Token contract cargado")
            
            # Cargar ABI de AnimalNFTUpgradeable
            nft_abi_path = base_path / "AnimalNFTUpgradeable.sol" / "AnimalNFTUpgradeable.json"
            print(f"📄 Buscando NFT ABI en: {nft_abi_path}")
            
            if not nft_abi_path.exists():
                nft_files = list(base_path.glob("**/*AnimalNFT*.json"))
                if nft_files:
                    nft_abi_path = nft_files[0]
                    print(f"📄 Usando NFT ABI alternativo: {nft_abi_path}")
                else:
                    raise FileNotFoundError(f"No se encontró el artifact de AnimalNFT: {nft_abi_path}")
            
            with open(nft_abi_path) as f:
                nft_artifact = json.load(f)
                nft_abi = nft_artifact["abi"]
                # Guardar el ABI completo para procesamiento de eventos
                self.nft_abi = nft_abi
            
            self.nft_contract = self.w3.eth.contract(
                address=settings.ANIMAL_NFT_ADDRESS,
                abi=nft_abi
            )
            print("✅ NFT contract cargado")
            
            # Cargar ABI de GanadoRegistryUpgradeable
            registry_abi_path = base_path / "GanadoRegistryUpgradeable.sol" / "GanadoRegistryUpgradeable.json"
            print(f"📄 Buscando Registry ABI en: {registry_abi_path}")
            
            if not registry_abi_path.exists():
                registry_files = list(base_path.glob("**/*Registry*.json"))
                if registry_files:
                    registry_abi_path = registry_files[0]
                    print(f"📄 Usando Registry ABI alternativo: {registry_abi_path}")
                else:
                    raise FileNotFoundError(f"No se encontró el artifact de Registry: {registry_abi_path}")
            
            with open(registry_abi_path) as f:
                registry_artifact = json.load(f)
                registry_abi = registry_artifact["abi"]
            
            self.registry_contract = self.w3.eth.contract(
                address=settings.REGISTRY_ADDRESS,
                abi=registry_abi
            )
            print("✅ Registry contract cargado")
            
            print("✅ Todos los contratos cargados exitosamente")
            
        except Exception as e:
            print(f"❌ Error al cargar contratos: {e}")
            raise ValueError(f"Error al cargar contratos: {e}")
    
    def get_role_hash(self, role_name):
        """Convertir nombre de rol to hash bytes32 correctamente"""
        return Web3.keccak(text=role_name)
    
    def assign_role(self, target_wallet, role_name):
        """Asignar rol on-chain"""
        try:
            role_hash = self.get_role_hash(role_name)
            
            # ✅ Usar nonce con transacciones pendientes
            nonce = self.w3.eth.get_transaction_count(self.wallet_address, 'pending')
            
            transaction = self.registry_contract.functions.grantRole(
                role_hash, Web3.to_checksum_address(target_wallet)
            ).build_transaction({
                'from': self.wallet_address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('100', 'gwei')
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            if hasattr(signed_txn, 'rawTransaction'):
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            return tx_hash.hex()
            
        except Exception as e:
            raise Exception(f"Error asignando rol: {e}")
    
    def has_role(self, wallet_address, role_name):
        """Verificar si wallet tiene rol"""
        try:
            role_hash = self.get_role_hash(role_name)
            return self.registry_contract.functions.hasRole(role_hash, Web3.to_checksum_address(wallet_address)).call()
        except Exception as e:
            raise Exception(f"Error verificando rol: {e}")
    
    def get_balance(self, wallet_address=None):
        """Obtener balance de MATIC"""
        if wallet_address is None:
            wallet_address = self.wallet_address
        return self.w3.eth.get_balance(Web3.to_checksum_address(wallet_address))
    
    def mint_animal_nft(self, owner_wallet, metadata_uri, operational_ipfs=""):
        """Mint un NFT para un animal - CON MANEJO MEJORADO DE NONCES"""
        try:
            print(f"🔧 Minting NFT para: {owner_wallet}")
            print(f"📁 Metadata URI: {metadata_uri}")
            print(f"⚙️ Operational IPFS: {operational_ipfs}")
            
            # ✅ Obtener nonce actual (incluyendo transacciones pendientes)
            nonce = self.w3.eth.get_transaction_count(self.wallet_address, 'pending')
            print(f"📝 Usando nonce: {nonce}")
            
            # Construir la transacción con mayor gas price
            transaction = self.nft_contract.functions.mintAnimal(
                Web3.to_checksum_address(owner_wallet),
                metadata_uri,
                operational_ipfs
            ).build_transaction({
                'from': self.wallet_address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': self.w3.to_wei('100', 'gwei')
            })
            
            # Firmar y enviar
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            if hasattr(signed_txn, 'rawTransaction'):
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            print(f"✅ Transacción enviada: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            print(f"❌ Error en mint_animal_nft: {e}")
            raise Exception(f"Error minting NFT: {e}")

    def get_nft_owner(self, token_id):
        """Obtener el owner de un NFT"""
        try:
            return self.nft_contract.functions.ownerOf(token_id).call()
        except Exception as e:
            raise Exception(f"Error obteniendo owner NFT: {e}")

    def register_animal_on_chain(self, animal_id, metadata):
        """Registrar animal en el registry de blockchain"""
        try:
            # ✅ Usar nonce con transacciones pendientes
            nonce = self.w3.eth.get_transaction_count(self.wallet_address, 'pending')
            
            transaction = self.registry_contract.functions.registerAnimal(
                animal_id, metadata
            ).build_transaction({
                'from': self.wallet_address,
                'nonce': nonce,
                'gas': 250000,
                'gasPrice': self.w3.to_wei('100', 'gwei')
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            if hasattr(signed_txn, 'rawTransaction'):
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                
            return tx_hash.hex()
            
        except Exception as e:
            raise Exception(f"Error registrando animal: {e}")

    # Funciones adicionales para el token ERC20
    def mint_tokens(self, to_address, amount):
    #Mint tokens ERC20"""
        try:
            # Convertir amount a entero si es string
            if isinstance(amount, str):
                amount = int(amount)
                
            # ✅ Usar nonce con transacciones pendientes
            nonce = self.w3.eth.get_transaction_count(self.wallet_address, 'pending')
            
            transaction = self.token_contract.functions.mint(
                Web3.to_checksum_address(to_address), amount
            ).build_transaction({
                'from': self.wallet_address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('100', 'gwei')
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            if hasattr(signed_txn, 'rawTransaction'):
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                
            return tx_hash.hex()
            
        except Exception as e:
            raise Exception(f"Error minting tokens: {e}")

    def get_token_balance(self, wallet_address):
        """Obtener balance de tokens ERC20"""
        try:
            return self.token_contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
        except Exception as e:
            raise Exception(f"Error obteniendo balance de tokens: {e}")

    # ================== MÉTODOS NUEVOS PARA COMPATIBILIDAD CON TESTS ==================

    def mint_and_associate_animal(self, animal, owner_wallet=None, operational_ipfs=""):
        """Mint NFT y asociar con animal (para compatibilidad con tests)"""
        try:
            if not isinstance(animal, Animal):
                animal = Animal.objects.get(id=animal)
            
            metadata_uri = f"ipfs://{animal.ipfs_hash}" if animal.ipfs_hash else ""
            if not metadata_uri:
                raise Exception("El animal no tiene IPFS hash para generar metadata")
            
            tx_hash = self.mint_animal_nft(
                owner_wallet or animal.owner.wallet_address,
                metadata_uri,
                operational_ipfs
            )
            
            return {
                'success': True,
                'tx_hash': tx_hash,
                'animal_id': animal.id,
                'ear_tag': animal.ear_tag
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_animal_history(self, animal_id):
        """Obtener historial de animal (para compatibilidad)"""
        try:
            animal = Animal.objects.get(id=animal_id)
            if animal.token_id:
                return self.get_transaction_history(animal_id)
            return []
        except Exception as e:
            return []

    # ================== FUNCIONES DE ASOCIACIÓN CON MODELOS ==================

    def _get_token_id_from_receipt(self, receipt):
        """Extraer token_id de los logs de la transacción usando el evento AnimalMinted"""
        try:
            print(f"🔍 Procesando receipt con {len(receipt['logs'])} logs")
            
            # Obtener el ABI del evento AnimalMinted
            event_abi = None
            for item in self.nft_abi:
                if item['type'] == 'event' and item['name'] == 'AnimalMinted':
                    event_abi = item
                    break
            
            if not event_abi:
                raise Exception("No se encontró el evento AnimalMinted en el ABI")
            
            # Crear el topic del evento
            event_topic = Web3.keccak(text="AnimalMinted(uint256,address,string)").hex()
            
            for log in receipt['logs']:
                if len(log['topics']) > 0 and log['topics'][0].hex() == event_topic:
                    try:
                        # Decodificar el log usando web3.py
                        event_data = get_event_data(self.w3.codec, event_abi, log)
                        token_id = event_data['args']['tokenId']
                        print(f"✅ Token ID extraído: {token_id}")
                        return token_id
                    except Exception as e:
                        print(f"⚠️ Error decodificando log: {e}")
                        continue
            
            # Fallback: intentar con el método del contrato
            print("⚠️ No se encontró evento AnimalMinted, usando fallback...")
            try:
                total_supply = self.nft_contract.functions.totalSupply().call()
                print(f"📦 Total supply: {total_supply}")
                return total_supply
            except:
                raise Exception("No se pudo extraer token_id del receipt")
                
        except Exception as e:
            print(f"❌ Error en _get_token_id_from_receipt: {e}")
            raise Exception(f"Error extrayendo token_id: {e}")

    def _get_last_token_id(self):
        """Obtener el último token ID mintado"""
        try:
            # Intentar obtener el total supply
            total_supply = self.nft_contract.functions.totalSupply().call()
            return total_supply
        except:
            return None

    def get_animal_by_token_id(self, token_id):
        """Buscar animal por token_id"""
        try:
            return Animal.objects.get(token_id=token_id)
        except Animal.DoesNotExist:
            return None
        except Exception as e:
            raise Exception(f"Error buscando animal: {e}")

    def get_animal_nft_info(self, animal):
        """Obtener información del NFT de un animal"""
        if not animal.token_id:
            return None
        
        try:
            owner = self.get_nft_owner(animal.token_id)
            token_uri = self.nft_contract.functions.tokenURI(animal.token_id).call()
            
            return {
                'token_id': animal.token_id,
                'owner': owner,
                'token_uri': token_uri,
                'tx_hash': animal.mint_transaction_hash,
                'is_owner_correct': owner.lower() == animal.nft_owner_wallet.lower()
            }
        except Exception as e:
            raise Exception(f"Error obteniendo info NFT: {e}")

    def verify_animal_nft(self, animal):
        """Verificar que la información del NFT coincide con la base de datos"""
        if not animal.token_id:
            return {'verified': False, 'error': 'Animal no tiene NFT'}
        
        try:
            nft_info = self.get_animal_nft_info(animal)
            if not nft_info:
                return {'verified': False, 'error': 'No se pudo obtener info del NFT'}
            
            # Verificar que el owner coincide
            owner_matches = nft_info['is_owner_correct']
            
            # Verificar que el token URI contiene el IPFS hash correcto
            ipfs_in_uri = animal.ipfs_hash in nft_info['token_uri'] if animal.ipfs_hash else False
            
            return {
                'verified': owner_matches and ipfs_in_uri,
                'owner_matches': owner_matches,
                'ipfs_in_uri': ipfs_in_uri,
                'blockchain_owner': nft_info['owner'],
                'db_owner': animal.nft_owner_wallet,
                'token_uri': nft_info['token_uri']
            }
            
        except Exception as e:
            return {'verified': False, 'error': str(e)}

    # ================== FUNCIONES DE SALUD Y IoT ==================

    def update_animal_health(self, animal_id, health_status, source="VETERINARIAN", 
                        veterinarian_wallet="", iot_device_id="", notes="", 
                        temperature=None, heart_rate=None):
        """Actualizar estado de salud en blockchain desde múltiples fuentes"""
        try:
            animal = Animal.objects.get(id=animal_id)
            if not animal.token_id:
                raise Exception("Animal no tiene NFT")
            
            # Preparar metadata para IPFS
            metadata = {
                'animal_id': animal.id,
                'ear_tag': animal.ear_tag,
                'health_status': health_status,
                'source': source,
                'notes': notes,
                'timestamp': int(time.time())
            }
            
            # Agregar datos biométricos si están disponibles
            if temperature is not None:
                metadata['temperature'] = float(temperature)
            if heart_rate is not None:
                metadata['heart_rate'] = heart_rate
            
            # Placeholder para IPFS - en producción usar cliente IPFS real
            ipfs_hash = f"QmHealthHash{int(time.time())}"
            
            # Actualizar en blockchain
            transaction = self.nft_contract.functions.updateOperational(
                animal.token_id,
                f"ipfs://{ipfs_hash}"
            ).build_transaction({
                'from': self.wallet_address,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address, 'pending'),
                'gas': 300000,
                'gasPrice': self.w3.to_wei('100', 'gwei')
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            # Buscar veterinario si se proporcionó wallet
            veterinarian = None
            if veterinarian_wallet:
                try:
                    veterinarian = User.objects.get(wallet_address__iexact=veterinarian_wallet)
                except User.DoesNotExist:
                    print(f"⚠️ Veterinario con wallet {veterinarian_wallet} no encontrado")
            
            # Manejar dispositivo IoT - CORRECCIÓN AQUÍ
            device_id_for_record = ""
            if source == 'IOT_SENSOR' and iot_device_id:
                try:
                    iot_device = IoTDevice.objects.get(device_id=iot_device_id)
                    device_id_for_record = iot_device_id
                except IoTDevice.DoesNotExist:
                    print(f"⚠️ Dispositivo IoT {iot_device_id} no encontrado")
                    device_id_for_record = iot_device_id
            
            # Guardar en base de datos - CORRECCIÓN AQUÍ
            health_record = AnimalHealthRecord.objects.create(
                animal=animal,
                health_status=health_status,
                source=source,
                veterinarian=veterinarian,
                iot_device_id=device_id_for_record,  # ← CAMPO CORRECTO
                notes=notes,
                temperature=temperature,
                heart_rate=heart_rate,
                ipfs_hash=ipfs_hash,
                transaction_hash=tx_hash_hex
            )
            
            # Actualizar el estado de salud del animal
            animal.health_status = health_status
            animal.save()
            
            print(f"✅ Registro de salud creado: {health_record.id}")
            return tx_hash_hex
            
        except Exception as e:
            print(f"❌ Error actualizando salud: {e}")
            raise Exception(f"Error updating health status: {e}")
    
    def update_health_from_iot(self, animal_id, health_status, device_id, 
                             temperature=None, heart_rate=None, notes=""):
        """Método específico para actualizaciones desde IoT"""
        try:
            # Lógica específica para IoT
            notes = f"Datos automáticos desde IoT - Device: {device_id}"
            if temperature:
                notes += f" - Temp: {temperature}°C"
            if heart_rate:
                notes += f" - HR: {heart_rate}bpm"
            
            tx_hash = self.update_animal_health(
                animal_id=animal_id,
                health_status=health_status,
                source='IOT_SENSOR',
                iot_device_id=device_id,
                notes=notes,
                temperature=temperature,
                heart_rate=heart_rate
            )
            
            return {'success': True, 'tx_hash': tx_hash}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_transaction_history(self, animal_id):
        """Obtener historial de transacciones de un animal"""
        try:
            animal = Animal.objects.get(id=animal_id)
            if not animal.token_id:
                return []
            
            # Filtrar eventos Transfer por token_id
            transfer_events = self.nft_contract.events.Transfer().get_logs(
                argument_filters={'tokenId': animal.token_id}
            )
            
            history = []
            for event in transfer_events:
                history.append({
                    'type': 'TRANSFER',
                    'from': event['args']['from'],
                    'to': event['args']['to'],
                    'block_number': event['blockNumber'],
                    'transaction_hash': event['transactionHash'].hex(),
                    'timestamp': self.w3.eth.get_block(event['blockNumber'])['timestamp']
                })
            
            return history
        except Exception as e:
            print(f"Error getting transaction history: {e}")
            return []

    # ================== UTILIDADES ==================

    def is_valid_wallet(self, wallet_address):
        """Verificar si una dirección de wallet es válida"""
        return self.w3.is_address(wallet_address)

    def to_checksum_address(self, wallet_address):
        """Convertir a checksum address"""
        return self.w3.to_checksum_address(wallet_address)

    def wait_for_transaction(self, tx_hash, timeout=120):
        """Esperar por la confirmación de una transacción"""
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
    
    # En blockchain/services.py, agrega este método:
    def update_batch_status(self, batch, new_status, notes=None):
        """
        Actualiza el estado de un lote en la blockchain
        """
        try:
            logger.info(f"Updating batch status on blockchain: {batch.name} -> {new_status}")
            
            # Verificar que el batch tenga blockchain_id
            if not batch.blockchain_id:
                logger.warning(f"Batch {batch.name} has no blockchain ID")
                return {
                    'success': False,
                    'error': 'Batch has no blockchain ID'
                }
            
            # Preparar datos para el hash
            batch_data = {
                'batch_id': batch.blockchain_id,
                'name': batch.name,
                'new_status': new_status,
                'timestamp': int(time.time()),
                'notes': notes or '',
                'animal_count': batch.animals.count(),
                'minted_animals_count': batch.animals.filter(token_id__isnull=False).count()
            }
            
            # Convertir a JSON y calcular hash
            batch_json = json.dumps(batch_data, sort_keys=True)
            batch_hash = Web3.keccak(text=batch_json).hex()
            
            # Llamar al contrato
            transaction = self.registry_contract.functions.updateBatchStatus(
                batch.blockchain_id,
                new_status,
                batch_hash
            ).build_transaction({
                'from': self.wallet_address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            })
            
            # Firmar y enviar transacción
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                logger.info(f"Batch status updated successfully. TX: {tx_hash.hex()}")
                
                # Actualizar el batch
                batch.blockchain_tx = tx_hash.hex()
                batch.save()
                
                # Crear evento blockchain - CORREGIDO: usar metadata en lugar de status y details
                from .models import BlockchainEvent
                BlockchainEvent.objects.create(
                    event_type='BATCH_STATUS_UPDATE',
                    batch=batch,
                    transaction_hash=tx_hash.hex(),
                    block_number=tx_receipt.blockNumber,  # ← AÑADIR block_number
                    metadata={  # ← USAR metadata PARA TODA LA INFORMACIÓN ADICIONAL
                        'status': 'CONFIRMED',
                        'old_status': batch.status,
                        'new_status': new_status,
                        'notes': notes,
                        'batch_data': batch_data
                    }
                )
                
                return {
                    'success': True,
                    'tx_hash': tx_hash.hex(),
                    'block_number': tx_receipt.blockNumber,
                    'batch_hash': batch_hash
                }
            else:
                logger.error(f"Batch status update failed. TX: {tx_hash.hex()}")
                return {
                    'success': False,
                    'error': 'Transaction failed',
                    'tx_hash': tx_hash.hex()
                }
                
        except Exception as e:
            logger.error(f"Error updating batch status: {str(e)}")
            return {
                'success': False,
                'error': f'Error updating batch status: {str(e)}'
            }