# users/management/commands/grant_dao_roles.py
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from web3 import Web3
from django.contrib.auth import get_user_model
from users.models import UserActivityLog

class Command(BaseCommand):
    help = 'Concede los roles on-chain en el contrato a los usuarios del DAO'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener el modelo User de forma dinámica
        self.User = get_user_model()
        # Configurar paths base - RUTA CORREGIDA
        self.base_dir = Path(settings.BASE_DIR)
        # GanadoChain está al mismo nivel que backend, no dentro
        self.ganado_chain_dir = self.base_dir.parent.parent / 'GanadoChain'
        self.artifacts_dir = self.ganado_chain_dir / 'artifacts' / 'contracts'

    def find_abi_file(self, contract_name, verbosity=1):
        """Busca el archivo ABI en la estructura de directorios de Hardhat"""
        possible_paths = [
            self.artifacts_dir / f"{contract_name}.sol" / f"{contract_name}.json",
            self.artifacts_dir / f"{contract_name}.sol" / f"{contract_name}.dbg.json",
            self.artifacts_dir / contract_name / f"{contract_name}.json",
            self.artifacts_dir / f"{contract_name}.json"
        ]
        
        for path in possible_paths:
            if path.exists():
                if verbosity >= 2:
                    self.stdout.write(f"📁 ABI encontrado en: {path}")
                return path
        
        return None

    def load_contract_abi(self, contract_type, verbosity=1):
        """Carga la ABI basado en el tipo de contrato"""
        contract_map = {
            'registry': 'GanadoRegistryUpgradeable',
            'token': 'GanadoTokenUpgradeable', 
            'nft': 'AnimalNFTUpgradeable'
        }
        
        contract_name = contract_map.get(contract_type)
        if not contract_name:
            raise ValueError(f"Tipo de contrato desconocido: {contract_type}")
        
        abi_path = self.find_abi_file(contract_name, verbosity)
        if not abi_path:
            raise FileNotFoundError(f"No se encontró ABI para {contract_name} en {self.artifacts_dir}")
        
        try:
            with open(abi_path, 'r') as f:
                contract_data = json.load(f)
                if verbosity >= 2:
                    self.stdout.write(f"✅ ABI cargado exitosamente: {contract_name}")
                return contract_data['abi']
        except Exception as e:
            raise Exception(f"Error leyendo ABI de {abi_path}: {e}")

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        
        try:
            # 1. OBTENER CONFIGURACIÓN DE .ENV
            self.stdout.write("🔧 Leyendo configuración de .env...")
            
            admin_wallet_address = os.environ.get('ADMIN_WALLET_ADDRESS', '').lower()
            admin_private_key = os.environ.get('ADMIN_PRIVATE_KEY', '')
            rpc_url = os.environ.get('BLOCKCHAIN_RPC_URL', 'https://rpc-amoy.polygon.technology')
            registry_address = os.environ.get('REGISTRY_ADDRESS', '')
            
            # Validar configuraciones esenciales
            if not admin_wallet_address:
                raise ValueError("ADMIN_WALLET_ADDRESS no configurada en .env")
            if not admin_private_key:
                raise ValueError("ADMIN_PRIVATE_KEY no configurada en .env")
            if not registry_address:
                raise ValueError("REGISTRY_ADDRESS no configurada en .env")

            # 2. CONFIGURAR WEB3
            self.stdout.write(f"🌐 Conectando a {rpc_url}...")
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not w3.is_connected():
                raise ConnectionError("No se pudo conectar al proveedor de Blockchain")
            
            self.stdout.write(self.style.SUCCESS(f"✅ Conectado a la red"))
            self.stdout.write(f"📦 Bloque más reciente: {w3.eth.block_number}")

            # 3. CARGAR CONTRATO REGISTRY
            self.stdout.write("📁 Cargando ABI del contrato Registry...")
            registry_abi = self.load_contract_abi('registry', verbosity)
            registry_contract = w3.eth.contract(
                address=registry_address,
                abi=registry_abi
            )
            self.stdout.write(self.style.SUCCESS("✅ Contrato Registry cargado"))

            # 4. CONFIGURAR CUENTA ADMINISTRADORA
            self.stdout.write("👤 Configurando cuenta administradora...")
            admin_account = w3.eth.account.from_key(admin_private_key)
            
            if admin_account.address.lower() != admin_wallet_address:
                raise ValueError("La private key no coincide con ADMIN_WALLET_ADDRESS")

            admin_balance = w3.eth.get_balance(admin_account.address)
            self.stdout.write(f"   Address: {admin_account.address}")
            self.stdout.write(f"   Balance: {w3.from_wei(admin_balance, 'ether')} MATIC")
            
            if admin_balance < w3.to_wei('0.001', 'ether'):
                self.stdout.write(self.style.WARNING("⚠️  Balance bajo para transacciones"))

            # 5. VERIFICAR PERMISOS DE ADMIN
            self.stdout.write("🔐 Verificando permisos...")
            default_admin_role = registry_contract.functions.DEFAULT_ADMIN_ROLE().call()
            has_admin_role = registry_contract.functions.hasRole(
                default_admin_role, 
                admin_account.address
            ).call()
            
            if not has_admin_role:
                raise PermissionError("La cuenta no tiene DEFAULT_ADMIN_ROLE")
            
            self.stdout.write(self.style.SUCCESS("✅ Cuenta tiene DEFAULT_ADMIN_ROLE"))

            # 6. OBTENER USUARIOS DE LA BASE DE DATOS
            self.stdout.write("👥 Buscando usuarios para conceder roles...")
            
            users_to_grant = self.User.objects.filter(
                is_blockchain_active=True,
                is_verified=False,
                blockchain_roles__isnull=False
            ).exclude(wallet_address='')

            total_users = users_to_grant.count()
            self.stdout.write(f"🔍 Encontrados {total_users} usuarios para procesar")

            if verbosity >= 2 and total_users > 0:
                self.stdout.write("📋 Usuarios encontrados:")
                for user in users_to_grant:
                    self.stdout.write(f"   • {user.username} ({user.wallet_short}): {user.blockchain_roles}")

            if total_users == 0:
                self.stdout.write(self.style.WARNING("⚠️  No hay usuarios con roles para conceder"))
                return

            # 7. PROCESAR USUARIOS Y CONCEDER ROLES
            successful_grants = 0
            failed_grants = 0

            for i, user in enumerate(users_to_grant, 1):
                self.stdout.write(f"\n--- [{i}/{total_users}] {user.username} ({user.wallet_short}) ---")
                if verbosity >= 2:
                    self.stdout.write(f"🎯 Roles: {', '.join(user.blockchain_roles)}")

                # Procesar cada rol del usuario
                for role_name in user.blockchain_roles:
                    try:
                        # Convertir nombre de rol a hash bytes32
                        role_hash = Web3.keccak(text=role_name)
                        
                        # Convertir wallet address a checksum
                        checksum_address = Web3.to_checksum_address(user.wallet_address)
                        if verbosity >= 2:
                            self.stdout.write(f"   🔄 Address convertida a checksum: {checksum_address}")
                        
                        # Verificar si ya tiene el rol
                        already_has_role = registry_contract.functions.hasRole(
                            role_hash,
                            checksum_address
                        ).call()
                        
                        if already_has_role:
                            if verbosity >= 2:
                                self.stdout.write(f"✅ {role_name}: Ya concedido")
                            continue

                        # Construir transacción
                        nonce = w3.eth.get_transaction_count(admin_account.address)
                        transaction = registry_contract.functions.grantRole(
                            role_hash,
                            checksum_address
                        ).build_transaction({
                            'from': admin_account.address,
                            'nonce': nonce,
                            'gas': 200000,
                            'gasPrice': w3.eth.gas_price,
                            'chainId': 80002,
                        })

                        # FIRMAR Y ENVIAR TRANSACCIÓN (COMPATIBLE WEB3 6.x y 7.x)
                        signed_txn = w3.eth.account.sign_transaction(transaction, admin_private_key)

                        try:
                            # Web3.py <= 6.x (SignedTransaction object)
                            raw_tx = signed_txn.rawTransaction
                        except AttributeError:
                            # Web3.py >= 7.x (dict con raw_transaction)
                            raw_tx = signed_txn["raw_transaction"]

                        tx_hash = w3.eth.send_raw_transaction(raw_tx)
                        tx_hash_hex = tx_hash.hex()
                        
                        self.stdout.write(f"🔄 {role_name}: Transacción enviada")
                        if verbosity >= 2:
                            self.stdout.write(f"   📋 Hash: {tx_hash_hex}")
                            self.stdout.write(f"   🔗 Explorar: https://amoy.polygonscan.com/tx/{tx_hash_hex}")

                        # Esperar confirmación
                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
                        
                        if receipt.status == 1:
                            self.stdout.write(self.style.SUCCESS(f"✅ {role_name}: Concedido exitosamente!"))
                            if verbosity >= 2:
                                self.stdout.write(f"   📦 Bloque: {receipt.blockNumber}")
                                self.stdout.write(f"   ⛽ Gas usado: {receipt.gasUsed}")
                            
                            if not user.is_verified:
                                user.is_verified = True
                                user.save()
                            
                            UserActivityLog.objects.create(
                                user=user,
                                action='ROLE_ASSIGN',
                                metadata={
                                    'role': role_name,
                                    'tx_hash': tx_hash_hex,
                                    'block_number': receipt.blockNumber,
                                    'gas_used': receipt.gasUsed
                                },
                                blockchain_tx_hash=tx_hash_hex
                            )
                            successful_grants += 1
                        else:
                            self.stdout.write(self.style.ERROR(f"❌ {role_name}: Transacción fallida"))
                            failed_grants += 1

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Error con {role_name}: {str(e)}"))
                        failed_grants += 1
                        continue

            # 8. RESUMEN FINAL
            self.stdout.write("\n" + "="*60)
            self.stdout.write(self.style.SUCCESS("🎉 PROCESO COMPLETADO"))
            self.stdout.write("="*60)
            self.stdout.write(f"✅ Concesiones exitosas: {successful_grants}")
            
            if failed_grants > 0:
                self.stdout.write(self.style.ERROR(f"❌ Concesiones fallidas: {failed_grants}"))
            
            self.stdout.write(f"📊 Total de transacciones: {successful_grants + failed_grants}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error crítico: {str(e)}"))
            import traceback
            if verbosity >= 2:
                self.stderr.write(traceback.format_exc())
            return
