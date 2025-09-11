# blockchain/management/commands/audit_wallet_activity.py
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from web3 import Web3
from django.contrib.auth import get_user_model
from collections import defaultdict
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Analiza TODAS las transacciones de la wallet admin del proyecto'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_dir = Path(settings.BASE_DIR)
        self.ganado_chain_dir = self.base_dir.parent.parent / 'GanadoChain'
        self.artifacts_dir = self.ganado_chain_dir / 'artifacts' / 'contracts'
        self.contract_abis = {}
        self.known_contracts = {}

    def load_contract_abis(self):
        """Cargar todos los ABIs de contratos del proyecto"""
        contract_files = {
            'registry': 'GanadoRegistryUpgradeable',
            'token': 'GanadoTokenUpgradeable', 
            'nft': 'AnimalNFTUpgradeable'
        }
        
        for contract_type, contract_name in contract_files.items():
            try:
                abi_path = self.artifacts_dir / f"{contract_name}.sol" / f"{contract_name}.json"
                with open(abi_path, 'r') as f:
                    abi_data = json.load(f)
                    self.contract_abis[contract_type] = abi_data['abi']
                    
                    # Guardar address del contrato si está en el ABI (para contracts deployados)
                    if 'address' in abi_data:
                        self.known_contracts[abi_data['address'].lower()] = contract_type
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"⚠️  ABI no encontrado para {contract_name}"))

        # Añadir contratos desde variables de entorno
        env_contracts = {
            os.environ.get('REGISTRY_ADDRESS', '').lower(): 'registry',
            os.environ.get('GANADO_TOKEN_ADDRESS', '').lower(): 'token',
            os.environ.get('ANIMAL_NFT_ADDRESS', '').lower(): 'nft'
        }
        self.known_contracts.update({k: v for k, v in env_contracts.items() if k})

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
            '--wallet',
            type=str,
            default=None,
            help='Wallet address a analizar (por defecto: ADMIN_WALLET_ADDRESS)'
        )
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Análisis rápido sin detalles de cada transacción'
        )

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        from_block = options['from_block']
        to_block = options['to_block']
        wallet_address = options['wallet'] or os.environ.get('ADMIN_WALLET_ADDRESS', '')
        quick_mode = options['quick']

        if not wallet_address:
            self.stderr.write(self.style.ERROR("❌ No se especificó wallet address"))
            return

        try:
            # 1. CONFIGURACIÓN
            rpc_url = os.environ.get('BLOCKCHAIN_RPC_URL', 'https://rpc-amoy.polygon.technology')
            
            # 2. CONECTAR
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not w3.is_connected():
                raise ConnectionError("No se pudo conectar a blockchain")

            # Convertir 'latest' a bloque actual
            if to_block == 'latest':
                to_block = w3.eth.block_number
            else:
                to_block = int(to_block)

            self.load_contract_abis()

            # 3. OBTENER TODAS LAS TRANSACCIONES DE LA WALLET
            self.stdout.write(f"\n🔍 Analizando transacciones de: {wallet_address}")
            self.stdout.write(f"📊 Rango de bloques: {from_block} → {to_block}")

            # Obtener transacciones como remitente (outgoing)
            outgoing_txs = self.get_wallet_transactions(w3, wallet_address, from_block, to_block, 'from')
            
            # Obtener transacciones como destinatario (incoming) 
            incoming_txs = self.get_wallet_transactions(w3, wallet_address, from_block, to_block, 'to')

            # 4. ANALIZAR TRANSACCIONES
            self.analyze_transactions(w3, outgoing_txs, incoming_txs, wallet_address, verbosity, quick_mode)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error crítico: {e}"))
            import traceback
            if verbosity >= 2:
                self.stderr.write(traceback.format_exc())

    def get_wallet_transactions(self, w3, wallet_address, from_block, to_block, direction):
        """Obtener transacciones de la wallet"""
        try:
            logs = w3.eth.get_logs({
                'fromBlock': from_block,
                'toBlock': to_block,
                direction: wallet_address
            })
            return logs
        except Exception as e:
            self.stdout.write(f"❌ Error obteniendo transacciones {direction}: {e}")
            return []

    def analyze_transactions(self, w3, outgoing_txs, incoming_txs, wallet_address, verbosity, quick_mode):
        """Analizar todas las transacciones de la wallet"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 ANÁLISIS COMPLETO DE TRANSACCIONES")
        self.stdout.write("="*60)

        total_outgoing = len(outgoing_txs)
        total_incoming = len(incoming_txs)
        
        self.stdout.write(f"📤 Transacciones salientes: {total_outgoing}")
        self.stdout.write(f"📥 Transacciones entrantes: {total_incoming}")
        self.stdout.write(f"📈 Total de transacciones: {total_outgoing + total_incoming}")

        # 1. ANALIZAR TRANSACCIONES SALIENTES (LAS MÁS IMPORTANTES)
        if outgoing_txs:
            self.stdout.write("\n🎯 TRANSACCIONES SALIENTES (ACCIONES REALIZADAS):")
            self.analyze_outgoing_transactions(w3, outgoing_txs, wallet_address, verbosity, quick_mode)

        # 2. ANALIZAR TRANSACCIONES ENTRANTES
        if incoming_txs:
            self.stdout.write("\n💸 TRANSACCIONES ENTRANTES (FONDOS RECIBIDOS):")
            self.analyze_incoming_transactions(w3, incoming_txs, verbosity, quick_mode)

        # 3. RESUMEN Y ESTADÍSTICAS
        self.generate_summary(w3, outgoing_txs, incoming_txs, wallet_address)

    def analyze_outgoing_transactions(self, w3, transactions, wallet_address, verbosity, quick_mode):
        """Analizar transacciones salientes en detalle"""
        categorized_txs = defaultdict(list)
        total_gas_used = 0
        total_value_sent = Decimal('0')

        for log in transactions:
            try:
                tx_hash = log['transactionHash'].hex()
                tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
                tx = w3.eth.get_transaction(tx_hash)
                
                # Obtener información básica
                block_number = tx_receipt['blockNumber']
                gas_used = tx_receipt['gasUsed']
                gas_price = tx['gasPrice']
                gas_cost = w3.from_wei(gas_used * gas_price, 'ether')
                value = w3.from_wei(tx['value'], 'ether')
                
                total_gas_used += gas_used
                total_value_sent += Decimal(str(value))

                # Categorizar la transacción
                category = self.categorize_transaction(w3, tx, tx_receipt)
                categorized_txs[category].append({
                    'hash': tx_hash,
                    'block': block_number,
                    'to': tx['to'],
                    'value': value,
                    'gas_used': gas_used,
                    'gas_cost': gas_cost,
                    'function': self.decode_function(w3, tx),
                    'status': '✅ Éxito' if tx_receipt['status'] == 1 else '❌ Fallo'
                })

                if verbosity >= 2 and not quick_mode:
                    self.stdout.write(f"\n   🔍 Tx: {tx_hash}")
                    self.stdout.write(f"     Block: {block_number}")
                    self.stdout.write(f"     To: {tx['to']}")
                    self.stdout.write(f"     Value: {value} MATIC")
                    self.stdout.write(f"     Gas: {gas_used} (Costo: {gas_cost} MATIC)")
                    self.stdout.write(f"     Función: {self.decode_function(w3, tx)}")
                    self.stdout.write(f"     Estado: {'✅ Éxito' if tx_receipt['status'] == 1 else '❌ Fallo'}")

            except Exception as e:
                self.stdout.write(f"❌ Error analizando tx {log['transactionHash'].hex()}: {e}")

        # Mostrar resumen por categoría
        self.stdout.write(f"\n📋 RESUMEN POR CATEGORÍA:")
        for category, txs in categorized_txs.items():
            self.stdout.write(f"   • {category}: {len(txs)} transacciones")

        self.stdout.write(f"\n💸 TOTAL ENVIADO: {total_value_sent} MATIC")
        self.stdout.write(f"⛽ TOTAL GAS USADO: {total_gas_used} gas")

    def analyze_incoming_transactions(self, w3, transactions, verbosity, quick_mode):
        """Analizar transacciones entrantes"""
        total_received = Decimal('0')
        
        for log in transactions:
            try:
                tx_hash = log['transactionHash'].hex()
                tx = w3.eth.get_transaction(tx_hash)
                value = w3.from_wei(tx['value'], 'ether')
                total_received += Decimal(str(value))

                if verbosity >= 2 and not quick_mode:
                    self.stdout.write(f"\n   💰 Tx: {tx_hash}")
                    self.stdout.write(f"     From: {tx['from']}")
                    self.stdout.write(f"     Value: {value} MATIC")
                    self.stdout.write(f"     Block: {tx['blockNumber']}")

            except Exception as e:
                self.stdout.write(f"❌ Error analizando tx entrante {log['transactionHash'].hex()}: {e}")

        self.stdout.write(f"\n💰 TOTAL RECIBIDO: {total_received} MATIC")

    def categorize_transaction(self, w3, tx, tx_receipt):
        """Categorizar la transacción"""
        to_address = tx['to']
        
        if not to_address:
            return "🚀 Deployment de contrato"
        
        to_address_lower = to_address.lower()
        
        # Verificar si es a un contrato conocido del proyecto
        if to_address_lower in self.known_contracts:
            contract_type = self.known_contracts[to_address_lower]
            return f"📦 Interacción con {contract_type.upper()}"
        
        # Verificar si es una transferencia simple
        if tx['input'] == '0x' or tx['input'] == '0x0':
            return "🔄 Transferencia simple de MATIC"
        
        # Intentar decodificar la función
        try:
            function_info = self.decode_function(w3, tx)
            if 'grantRole' in function_info:
                return "🎯 Concesión de rol"
            elif 'mint' in function_info.lower():
                return "🪙 Minting de tokens/NFTs"
            elif 'transfer' in function_info.lower():
                return "🔄 Transferencia de tokens"
        except:
            pass
        
        return "⚡ Otra interacción con contrato"

    def decode_function(self, w3, tx):
        """Intentar decodificar la función llamada"""
        if not tx['input'] or tx['input'] == '0x' or tx['input'] == '0x0':
            return "Transferencia simple"
        
        to_address = tx['to']
        if not to_address:
            return "Contract deployment"
        
        # Buscar en contratos conocidos
        for contract_address, contract_type in self.known_contracts.items():
            if to_address.lower() == contract_address:
                try:
                    contract = w3.eth.contract(address=to_address, abi=self.contract_abis[contract_type])
                    decoded = contract.decode_function_input(tx['input'])
                    return f"{decoded[0].fn_name}"
                except:
                    return f"Interacción con {contract_type} (no decodificada)"
        
        return "Interacción con contrato externo"

    def generate_summary(self, w3, outgoing_txs, incoming_txs, wallet_address):
        """Generar resumen final"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📈 RESUMEN FINAL")
        self.stdout.write("="*60)
        
        # Balance actual
        try:
            balance = w3.from_wei(w3.eth.get_balance(wallet_address), 'ether')
            self.stdout.write(f"💰 Balance actual: {balance} MATIC")
        except:
            pass
        
        # Estadísticas de gas
        total_gas = 0
        for tx in outgoing_txs:
            try:
                receipt = w3.eth.get_transaction_receipt(tx['transactionHash'].hex())
                total_gas += receipt['gasUsed']
            except:
                pass
                
        self.stdout.write(f"⛽ Gas total usado: {total_gas}")
        
        # Contratos interactuados
        interacted_contracts = set()
        for tx in outgoing_txs:
            try:
                tx_data = w3.eth.get_transaction(tx['transactionHash'].hex())
                if tx_data['to']:
                    interacted_contracts.add(tx_data['to'])
            except:
                pass
        
        self.stdout.write(f"📞 Contratos interactuados: {len(interacted_contracts)}")
        
        # Transacciones exitosas vs fallidas
        success_count = 0
        for tx in outgoing_txs:
            try:
                receipt = w3.eth.get_transaction_receipt(tx['transactionHash'].hex())
                if receipt['status'] == 1:
                    success_count += 1
            except:
                pass
        
        self.stdout.write(f"✅ Transacciones exitosas: {success_count}/{len(outgoing_txs)}")