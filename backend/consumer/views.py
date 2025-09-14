from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q
import qrcode
import io
import json

# Importaciones corregidas desde las ubicaciones correctas
from cattle.models import Animal, AnimalHealthRecord
from cattle.blockchain_models import AnimalCertification 
from cattle.serializers import (
    PublicAnimalHistorySerializer, 
    PublicAnimalSerializer,
    PublicHealthRecordSerializer,
    
)
from blockchain.models import BlockchainEvent
from blockchain.serializers import PublicBlockchainEventSerializer, PublicCertificationSerializer
import logging

logger = logging.getLogger(__name__)

class QRVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        qr_data = request.query_params.get('qr', '')
        token_id = request.query_params.get('token_id', '')
        
        if not qr_data and not token_id:
            return Response({'error': 'QR code or token ID required'}, status=400)
        
        try:
            if qr_data:
                # Decodificar QR code
                if qr_data.startswith('GANADOCHAIN_ANIMAL_'):
                    animal_id = int(qr_data.split('_')[-1])
                    animal = Animal.objects.get(id=animal_id, is_minted=True)
                else:
                    return Response({'verified': False, 'error': 'Invalid QR format'})
            else:
                # Buscar por token ID
                animal = Animal.objects.get(token_id=token_id, is_minted=True)
            
            # Verificar que el animal esté mintado y sea válido
            if not animal.is_minted:
                return Response({'verified': False, 'error': 'Animal not minted on blockchain'})
            
            # Obtener información pública del animal
            animal_data = PublicAnimalSerializer(animal).data
            
            # Obtener certificaciones válidas
            certifications = AnimalCertification.objects.filter(
                animal=animal, 
                revoked=False,
                expiration_date__gte=timezone.now()
            )
            
            # Obtener último registro de salud
            last_health_record = AnimalHealthRecord.objects.filter(
                animal=animal
            ).order_by('-created_at').first()
            
            # Obtener eventos blockchain relevantes
            blockchain_events = BlockchainEvent.objects.filter(
                animal=animal,
                event_type__in=['MINT', 'TRANSFER', 'HEALTH_UPDATE']
            ).order_by('-created_at')[:10]
            
            return Response({
                'verified': True,
                'animal': animal_data,
                'certifications': PublicCertificationSerializer(certifications, many=True).data,
                'last_health_record': PublicHealthRecordSerializer(last_health_record).data if last_health_record else None,
                'blockchain_events': PublicBlockchainEventSerializer(blockchain_events, many=True).data,
                'verification_date': timezone.now(),
                'verification_id': f"VC_{animal.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            })
            
        except Animal.DoesNotExist:
            return Response({'verified': False, 'error': 'Animal not found'})
        except Exception as e:
            logger.error(f"Error en verificación QR: {str(e)}")
            return Response({'verified': False, 'error': 'Verification error'})

class PublicAnimalHistoryView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, animal_id):
        animal = get_object_or_404(Animal, id=animal_id, is_minted=True)
        
        # Obtener historial completo público
        health_records = AnimalHealthRecord.objects.filter(
            animal=animal
        ).order_by('-created_at')[:50]  # Limitar a 50 registros
        
        certifications = AnimalCertification.objects.filter(
            animal=animal,
            revoked=False
        ).order_by('-certification_date')
        
        blockchain_events = BlockchainEvent.objects.filter(
            animal=animal
        ).order_by('-created_at')[:20]
        
        response_data = {
            'animal': PublicAnimalSerializer(animal).data,
            'health_history': PublicHealthRecordSerializer(health_records, many=True).data,
            'certifications': PublicCertificationSerializer(certifications, many=True).data,
            'blockchain_history': PublicBlockchainEventSerializer(blockchain_events, many=True).data,
            'summary': {
                'total_health_records': health_records.count(),
                'total_certifications': certifications.count(),
                'total_blockchain_events': blockchain_events.count(),
                'first_record_date': health_records.last().created_at if health_records.exists() else None,
                'last_update': animal.updated_at
            }
        }
        
        return Response(response_data)

class GenerateQRView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, animal_id):
        animal = get_object_or_404(Animal, id=animal_id)
        
        # Generar QR con más información
        qr_data = json.dumps({
            'type': 'GANADOCHAIN_ANIMAL',
            'animal_id': animal.id,
            'ear_tag': animal.ear_tag,
            'token_id': animal.token_id,
            'breed': animal.breed,
            'verification_url': f"{request.build_absolute_uri('/')}api/consumer/verify/?qr=GANADOCHAIN_ANIMAL_{animal.id}"
        })
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a respuesta HTTP
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="ganadochain_qr_{animal.ear_tag}.png"'
        return response

class AnimalSearchView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        search_term = request.query_params.get('q', '')
        breed = request.query_params.get('breed', '')
        health_status = request.query_params.get('health_status', '')
        
        queryset = Animal.objects.filter(is_minted=True, is_public=True)
        
        if search_term:
            queryset = queryset.filter(
                Q(ear_tag__icontains=search_term) |
                Q(breed__icontains=search_term) |
                Q(token_id__icontains=search_term)
            )
        
        if breed:
            queryset = queryset.filter(breed__iexact=breed)
        
        if health_status:
            queryset = queryset.filter(health_status=health_status)
        
        # Limitar resultados y ordenar
        animals = queryset.order_by('-created_at')[:20]
        
        return Response({
            'results': PublicAnimalSerializer(animals, many=True).data,
            'count': animals.count(),
            'search_term': search_term
        })

class CertificationVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, certification_id):
        certification = get_object_or_404(AnimalCertification, id=certification_id)
        
        # Verificar que la certificación sea válida
        is_valid = (
            not certification.revoked and 
            certification.expiration_date >= timezone.now() and
            certification.animal.is_minted
        )
        
        response_data = {
            'certification': PublicCertificationSerializer(certification).data,
            'is_valid': is_valid,
            'verification_date': timezone.now(),
            'animal': PublicAnimalSerializer(certification.animal).data,
            'issuing_authority': certification.standard.issuing_authority if certification.standard else None
        }
        
        return Response(response_data)

class BlockchainProofView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, animal_id):
        animal = get_object_or_404(Animal, id=animal_id, is_minted=True)
        
        # Obtener eventos blockchain como prueba
        events = BlockchainEvent.objects.filter(
            animal=animal
        ).order_by('created_at')
        
        # Crear proof chain
        proof_chain = []
        for event in events:
            proof_chain.append({
                'event_type': event.event_type,
                'transaction_hash': event.transaction_hash,
                'block_number': event.block_number,
                'timestamp': event.created_at,
                'metadata': event.metadata
            })
        
        return Response({
            'animal_id': animal.id,
            'ear_tag': animal.ear_tag,
            'token_id': animal.token_id,
            'proof_chain': proof_chain,
            'total_events': len(proof_chain),
            'first_event': proof_chain[0] if proof_chain else None,
            'last_event': proof_chain[-1] if proof_chain else None,
            'verification_hash': self.generate_verification_hash(proof_chain)
        })
    
    def generate_verification_hash(self, proof_chain):
        import hashlib
        chain_data = ''.join([str(event['transaction_hash']) for event in proof_chain])
        return hashlib.sha256(chain_data.encode()).hexdigest()

class PublicAPIDocsView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        docs = {
            'endpoints': {
                'qr_verification': {
                    'url': '/api/consumer/verify/',
                    'method': 'GET',
                    'params': {'qr': 'QR code data or token_id'},
                    'description': 'Verify animal using QR code or token ID'
                },
                'animal_history': {
                    'url': '/api/consumer/animal/<animal_id>/history/',
                    'method': 'GET',
                    'description': 'Get public history of an animal'
                },
                'generate_qr': {
                    'url': '/api/consumer/animal/<animal_id>/qr/',
                    'method': 'GET',
                    'description': 'Generate QR code for an animal'
                },
                'animal_search': {
                    'url': '/api/consumer/search/',
                    'method': 'GET',
                    'params': {'q': 'search term', 'breed': 'filter by breed', 'health_status': 'filter by health status'},
                    'description': 'Search for public animals'
                },
                'certification_verify': {
                    'url': '/api/consumer/certification/<certification_id>/verify/',
                    'method': 'GET',
                    'description': 'Verify a certification'
                },
                'blockchain_proof': {
                    'url': '/api/consumer/animal/<animal_id>/proof/',
                    'method': 'GET',
                    'description': 'Get blockchain proof chain for an animal'
                }
            },
            'response_formats': ['JSON'],
            'authentication': 'None required for public endpoints',
            'rate_limiting': '100 requests per hour per IP',
            'version': '1.0.0'
        }
        
        return Response(docs)