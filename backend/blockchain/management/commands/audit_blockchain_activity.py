# blockchain/management/commands/audit_blockchain_activity.py
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from web3 import Web3
from django.contrib.auth import get_user_model
from collections import defaultdict

User = get_user_model()

class Command(BaseCommand):
    help = 'Auditoría completa de todas las transacciones en los contratos'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_dir = Path(settings.BASE_DIR)
        self.ganado_chain_dir = self.base_dir.parent.parent / 'GanadoChain'
        self.artifacts_dir = self.ganado_chain_dir / 'artifacts' / 'contracts'
        self.contract_abis = {}

    def load_all_abis(self):
        """Cargar todos los ABIs de contratos disponibles"""
        contract_files = {
            'registry': 'GanadoRegistryUpgradeable',
            'token': 'GanadoTokenUpgradeable', 
            'nft': 'AnimalNFTUpgradeable'
        }
        
        for contract_type, contract_name in contract_files.items():
            try:
                abi_path = self.artifacts_dir / f"{contract_name}.sol" / f"{contract_name}.json"
                with open(abi_path, 'r') as f:
                    self.contract_abis[contract_type] = json.load(f)['abi']
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"⚠️  ABI no encontrado para {contract_name}"))

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-block',
            type=int,
            default=0,
            help='Bloque inicial para escanear'
        )
        parser.add_argument(
            '--to-block',
            type=str,
            default='latest',
            help='Bloque final para escanear (número o "latest")'
        )
        parser.add_argument(
            '--check-events',
            action='store_true',
            help='Revisar eventos de contratos'
        )
        parser.add_argument(
            '--check-transactions',
            action='store_true', 
            help='Revisar transacciones directas'
        )

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        from_block = options['from_block']
        to_block = options['to_block']

        try:
            # 1. CONFIGURACIÓN
            rpc_url = os.environ.get('BLOCKCHAIN_RPC_URL', 'https://rpc-amoy.polygon.technology')
            contract_addresses = {
                'registry': os.environ.get('REGISTRY_ADDRESS'),
                'token': os.environ.get('GANADO_TOKEN_ADDRESS'),
                'nft': os.environ.get('ANIMAL_NFT_ADDRESS')
            }

            # 2. CONECTAR Y CONVERTIR 'latest'
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not w3.is_connected():
                raise ConnectionError("No se pudo conectar a blockchain")

            # Convertir 'latest' a bloque actual
            if to_block == 'latest':
                to_block = w3.eth.block_number
            else:
                to_block = int(to_block)

            self.stdout.write(f"📊 Escaneando bloques: {from_block} → {to_block}")

            self.load_all_abis()

            # 3. INSTANCIAR CONTRATOS
            contracts = {}
            for contract_type, address in contract_addresses.items():
                if address and contract_type in self.contract_abis:
                    contracts[contract_type] = w3.eth.contract(
                        address=address, 
                        abi=self.contract_abis[contract_type]
                    )
                    self.stdout.write(f"✅ Contrato {contract_type} cargado: {address}")
                else:
                    self.stdout.write(f"⚠️  Contrato {contract_type} no configurado")

            # 4. AUDITORÍA DE EVENTOS
            if options['check_events']:
                self.audit_contract_events(contracts, from_block, to_block, verbosity)

            # 5. AUDITORÍA DE TRANSACCIONES
            if options['check_transactions']:
                self.audit_transactions(w3, contract_addresses, from_block, to_block, verbosity)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error crítico: {e}"))
            import traceback
            if verbosity >= 2:
                self.stderr.write(traceback.format_exc())

    def audit_contract_events(self, contracts, from_block, to_block, verbosity):
        """Auditar todos los eventos de los contratos"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("🔍 AUDITORÍA DE EVENTOS DE CONTRATOS")
        self.stdout.write("="*60)

        all_events = []

        for contract_type, contract in contracts.items():
            try:
                # Obtener todos los eventos disponibles del contrato
                events = contract.events
                
                # CORRECCIÓN: Iterar sobre las keys del diccionario _events
                for event_name in events._events.keys():
                    try:
                        event_class = getattr(events, event_name)
                        
                        self.stdout.write(f"\n📋 Buscando eventos {event_name} en {contract_type}...")
                        
                        logs = event_class.get_logs(
                            fromBlock=from_block,
                            toBlock=to_block
                        )
                        
                        self.stdout.write(f"   ✅ Encontrados: {len(logs)} eventos")
                        
                        for log in logs:
                            event_data = {
                                'contract': contract_type,
                                'event': event_name,
                                'tx_hash': log['transactionHash'].hex(),
                                'block': log['blockNumber'],
                                'args': dict(log['args'])
                            }
                            all_events.append(event_data)
                            
                            if verbosity >= 2:
                                self.stdout.write(f"   🔍 Tx: {log['transactionHash'].hex()} - Block: {log['blockNumber']}")
                                if 'args' in log and log['args']:
                                    for arg_name, arg_value in log['args'].items():
                                        self.stdout.write(f"     {arg_name}: {arg_value}")

                    except Exception as e:
                        self.stdout.write(f"   ❌ Error en evento {event_name}: {e}")
                        continue

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error en {contract_type}: {e}"))

        # 6. ANALIZAR EVENTOS
        self.analyze_unexpected_events(all_events, verbosity)

    def audit_transactions(self, w3, contract_addresses, from_block, to_block, verbosity):
        """Auditar transacciones directas a los contratos"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("🔍 AUDITORÍA DE TRANSACCIONES DIRECTAS")
        self.stdout.write("="*60)

        # Obtener todas las transacciones a los contratos
        for contract_type, address in contract_addresses.items():
            if not address:
                continue

            self.stdout.write(f"\n📋 Transacciones a {contract_type} ({address})")
            
            try:
                # Crear filtro para transacciones a este contrato
                logs = w3.eth.get_logs({
                    'fromBlock': from_block,
                    'toBlock': to_block,
                    'address': address
                })
                
                self.stdout.write(f"   ✅ Transacciones encontradas: {len(logs)}")
                
                # Analizar transacciones
                for i, log in enumerate(logs):
                    if verbosity >= 2 or (verbosity >= 1 and i < 5):  # Mostrar primeras 5 en verbosity 1
                        tx_hash = log['transactionHash'].hex()
                        tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
                        tx = w3.eth.get_transaction(tx_hash)
                        
                        self.stdout.write(f"   🔍 Tx: {tx_hash}")
                        self.stdout.write(f"     Block: {log['blockNumber']}")
                        self.stdout.write(f"     From: {tx['from']}")
                        self.stdout.write(f"     To: {tx['to']}")
                        self.stdout.write(f"     Value: {w3.from_wei(tx['value'], 'ether')} MATIC")
                        self.stdout.write(f"     Gas usado: {tx_receipt['gasUsed']}")
                        
                        # Intentar decodificar la data de la transacción
                        if tx['input'] and tx['input'] != '0x':
                            try:
                                # Buscar el contrato correcto para decodificar
                                for ct_type, addr in contract_addresses.items():
                                    if addr and addr.lower() == tx['to'].lower():
                                        contract = w3.eth.contract(address=addr, abi=self.contract_abis.get(ct_type, []))
                                        try:
                                            decoded = contract.decode_function_input(tx['input'])
                                            self.stdout.write(f"     Función: {decoded[0].fn_name}")
                                            for param, value in decoded[1].items():
                                                self.stdout.write(f"       {param}: {value}")
                                        except:
                                            self.stdout.write(f"     Data: {tx['input'][:100]}...")
                                        break
                            except:
                                self.stdout.write(f"     Data: {tx['input'][:100]}...")
                        
                        self.stdout.write("     ---")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error auditando {contract_type}: {e}"))

    def analyze_unexpected_events(self, events, verbosity):
        """Analizar eventos inesperados o no contemplados"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("🔍 ANÁLISIS DE EVENTOS")
        self.stdout.write("="*60)

        if not events:
            self.stdout.write("📭 No se encontraron eventos")
            return

        # Contar eventos por tipo y contrato
        event_counts = defaultdict(lambda: defaultdict(int))
        for event in events:
            event_counts[event['contract']][event['event']] += 1

        self.stdout.write("\n📊 RESUMEN DE EVENTOS POR CONTRATO:")
        for contract, events_in_contract in event_counts.items():
            self.stdout.write(f"\n   📍 {contract.upper()}:")
            for event_name, count in events_in_contract.items():
                self.stdout.write(f"     • {event_name}: {count} eventos")

        # Eventos esperados (que tu sistema ya maneja)
        expected_events = {
            'RoleGranted', 'RoleRevoked', 'Transfer', 'Approval',
            'Mint', 'Burn', 'HealthUpdated', 'BatchCreated'
        }

        # Buscar eventos inesperados
        unexpected_events = defaultdict(lambda: defaultdict(int))
        for event in events:
            if event['event'] not in expected_events:
                unexpected_events[event['contract']][event['event']] += 1

        if unexpected_events:
            self.stdout.write(self.style.WARNING("\n⚠️  EVENTOS NO CONTEMPLADOS:"))
            for contract, events_in_contract in unexpected_events.items():
                self.stdout.write(f"\n   📍 {contract.upper()}:")
                for event_name, count in events_in_contract.items():
                    self.stdout.write(f"     • {event_name}: {count} ocurrencias")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Todos los eventos están contemplados"))

        # Buscar usuarios desconocidos en eventos
        unknown_users = set()
        for event in events:
            if 'args' in event and event['args']:
                # Buscar addresses en los argumentos del evento
                for arg_name, arg_value in event['args'].items():
                    if isinstance(arg_value, str) and arg_value.startswith('0x') and len(arg_value) == 42:
                        user_address = arg_value.lower()
                        if not User.objects.filter(wallet_address=user_address).exists():
                            unknown_users.add(user_address)

        if unknown_users:
            self.stdout.write(self.style.WARNING("\n⚠️  USUARIOS DESCONOCIDOS EN BLOCKCHAIN:"))
            for address in list(unknown_users)[:10]:  # Mostrar solo primeros 10
                self.stdout.write(f"   • {address}")
            if len(unknown_users) > 10:
                self.stdout.write(f"   • ... y {len(unknown_users) - 10} más")

    def get_contract_creation_block(self, w3, contract_address):
        """Obtener bloque de creación del contrato"""
        try:
            # Obtener la transacción de creación del contrato
            tx_hash = w3.eth.get_transaction_receipt(contract_address).transactionHash
            tx = w3.eth.get_transaction(tx_hash)
            return tx.blockNumber
        except:
            return 0