from django.db import transaction
from .adapter import BlockchainAdapterFactory
from cattle.models import Animal
from cattle.multichain_models import AnimalMultichain, AnimalNFTMirror
from django.conf import settings
from django.utils import timezone
from core.multichain.models import BlockchainNetwork
import requests




class MultichainNFTService:
    """Servicio para operaciones NFT multichain"""
    
    def __init__(self):
        self.adapters = {}
    
    def register_animal_on_blockchain(self, animal_multichain, primary_network_id=None):
        """Registrar animal en blockchain primaria"""
        try:
            with transaction.atomic():
                # Obtener red primaria
                if primary_network_id:
                    primary_network = BlockchainNetwork.objects.get(id=primary_network_id)
                else:
                    primary_network = animal_multichain.primary_network
                
                if not primary_network:
                    raise ValueError("Primary network not specified")
                
                # Crear metadata del NFT
                metadata_uri = self._create_animal_metadata(animal_multichain.animal)
                
                # Mint NFT en red primaria
                adapter = BlockchainAdapterFactory.get_adapter(primary_network)
                result = adapter.mint_nft(
                    metadata_uri=metadata_uri,
                    to_address=animal_multichain.animal.owner.wallet_address
                )
                
                if result['success']:
                    # Actualizar modelo con datos del NFT
                    animal_multichain.primary_network = primary_network
                    animal_multichain.primary_token_id = result['token_id']
                    animal_multichain.save()
                    
                    # Crear evento blockchain
                    self._create_blockchain_event(
                        animal_multichain.animal,
                        'NFT_MINTED',
                        primary_network,
                        result['transaction_hash'],
                        f"NFT minted on {primary_network.name}"
                    )
                    
                    return {
                        'success': True,
                        'transaction_hash': result['transaction_hash'],
                        'token_id': result['token_id'],
                        'network': primary_network.name
                    }
                else:
                    return {
                        'success': False,
                        'error': result['error']
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_mirror_on_network(self, animal_multichain, target_network_id):
        """Crear espejo del NFT en otra blockchain"""
        try:
            with transaction.atomic():
                target_network = BlockchainNetwork.objects.get(id=target_network_id)
                
                # Verificar que no exista ya un espejo en esta red
                existing_mirror = AnimalNFTMirror.objects.filter(
                    animal_multichain=animal_multichain,
                    network=target_network
                ).first()
                
                if existing_mirror:
                    return {
                        'success': False,
                        'error': f"Mirror already exists on {target_network.name}"
                    }
                
                # Obtener metadata del NFT original
                metadata_uri = self._get_existing_metadata(animal_multichain)
                
                # Mint espejo en red destino
                adapter = BlockchainAdapterFactory.get_adapter(target_network)
                result = adapter.mint_nft(
                    metadata_uri=metadata_uri,
                    to_address=animal_multichain.animal.owner.wallet_address
                )
                
                if result['success']:
                    # Crear registro del espejo
                    mirror = AnimalNFTMirror.objects.create(
                        animal_multichain=animal_multichain,
                        network=target_network,
                        token_id=result['token_id'],
                        mirror_transaction_hash=result['transaction_hash'],
                        is_active=True
                    )
                    
                    # Marcar como cross-chain
                    animal_multichain.is_cross_chain = True
                    animal_multichain.last_cross_chain_sync = timezone.now()
                    animal_multichain.save()
                    
                    # Crear evento blockchain
                    self._create_blockchain_event(
                        animal_multichain.animal,
                        'NFT_MIRRORED',
                        target_network,
                        result['transaction_hash'],
                        f"NFT mirrored to {target_network.name}"
                    )
                    
                    return {
                        'success': True,
                        'mirror_id': mirror.id,
                        'transaction_hash': result['transaction_hash'],
                        'token_id': result['token_id'],
                        'network': target_network.name
                    }
                else:
                    return {
                        'success': False,
                        'error': result['error']
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_animal_metadata(self, animal):
        """Crear metadata IPFS para el animal"""
        metadata = {
            "name": f"GanadoChain NFT - {animal.ear_tag}",
            "description": f"Digital twin of {animal.breed} cattle with ear tag {animal.ear_tag}",
            "image": self._get_animal_image_url(animal),
            "attributes": [
                {
                    "trait_type": "Breed",
                    "value": animal.breed
                },
                {
                    "trait_type": "Birth Date", 
                    "value": animal.birth_date.isoformat() if animal.birth_date else ""
                },
                {
                    "trait_type": "Health Status",
                    "value": animal.health_status
                },
                {
                    "trait_type": "Current Weight",
                    "value": float(animal.current_weight) if animal.current_weight else 0
                },
                {
                    "trait_type": "Owner",
                    "value": animal.owner.username
                }
            ],
            "external_url": f"https://ganadochain.com/animals/{animal.id}",
            "background_color": "ffffff"
        }
        
        # Subir a IPFS y retornar URI
        return self._upload_to_ipfs(metadata)
    
    def _upload_to_ipfs(self, metadata):
        """Subir metadata a IPFS"""
        # Implementar upload a IPFS (Pinata, Infura, etc.)
        try:
            # Ejemplo con Pinata
            headers = {
                'pinata_api_key': settings.PINATA_API_KEY,
                'pinata_secret_api_key': settings.PINATA_SECRET_API_KEY,
            }
            
            response = requests.post(
                'https://api.pinata.cloud/pinning/pinJSONToIPFS',
                headers=headers,
                json=metadata
            )
            
            if response.status_code == 200:
                ipfs_hash = response.json()['IpfsHash']
                return f"ipfs://{ipfs_hash}"
            else:
                # Fallback to storing hash in database
                return f"https://ganadochain.com/api/metadata/{hash(metadata)}/"
                
        except Exception:
            # Fallback local
            return f"https://ganadochain.com/api/metadata/{hash(metadata)}/"
    
    def _get_animal_image_url(self, animal):
        """Obtener URL de imagen del animal"""
        if animal.photos.exists():
            return animal.photos.first().image.url
        else:
            # Imagen por defecto basada en raza
            return f"https://ganadochain.com/static/images/breeds/{animal.breed.lower()}.jpg"
    
    def _get_existing_metadata(self, animal_multichain):
        """Obtener metadata existente del NFT original"""
        # En una implementación real, esto obtendría la metadata del NFT existente
        return self._create_animal_metadata(animal_multichain.animal)
    
    def _create_blockchain_event(self, animal, event_type, network, tx_hash, description):
        """Crear registro de evento blockchain"""
        from cattle.models import BlockchainEventState
        
        BlockchainEventState.objects.create(
            animal=animal,
            event_type=event_type,
            blockchain_network=network.name,
            transaction_hash=tx_hash,
            description=description,
            status='CONFIRMED'
        )