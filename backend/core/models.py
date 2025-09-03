from django.db import models
from django.core.exceptions import ValidationError
import re
from web3 import Web3

# Validaciones mejoradas para reutilizar
def validate_ethereum_address(value):
    """Validación completa de dirección Ethereum"""
    if not re.match(r'^(0x)?[0-9a-fA-F]{40}$', value):
        raise ValidationError('Dirección Ethereum inválida')
    
    # Validación de checksum si tiene prefijo 0x
    if value.startswith('0x'):
        try:
            checksum_address = Web3.to_checksum_address(value)
            if value != checksum_address:
                raise ValidationError('Dirección Ethereum con checksum inválido')
        except:
            raise ValidationError('Dirección Ethereum inválida')

def validate_transaction_hash(value):
    """Validación de hash de transacción"""
    if not re.match(r'^(0x)?[0-9a-fA-F]{64}$', value):
        raise ValidationError('Hash de transacción inválido')

def validate_ipfs_hash(value):
    """Validación de hash IPFS"""
    if value and not re.match(r'^[Qm][1-9A-Za-z]{44}$', value):
        raise ValidationError('Hash IPFS inválido')