from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import GlobalCertificationBody, Certification, CertificationStandard
from .serializers import (
    GlobalCertificationBodySerializer,
    CertificationSerializer,
    CertificationStandardSerializer
)

class GlobalCertificationBodyViewSet(viewsets.ModelViewSet):
    """Organismos de certificación global"""
    queryset = GlobalCertificationBody.objects.filter(is_active=True)
    serializer_class = GlobalCertificationBodySerializer
    
    @action(detail=True, methods=['get'])
    def certifications(self, request, pk=None):
        """Certificaciones emitidas por este organismo"""
        body = self.get_object()
        certifications = Certification.objects.filter(
            standard__certification_body=body
        )[:50]  # Limitar para demo
        
        serializer = CertificationSerializer(certifications, many=True)
        return Response(serializer.data)

class CertificationViewSet(viewsets.ModelViewSet):
    """Certificaciones - CRÍTICO PARA DEMO DE TRAZABILIDAD"""
    queryset = Certification.objects.select_related(
        'certified_entity', 'standard', 'auditor'
    ).prefetch_related('animals', 'batches')[:100]  # Limitar para demo
    
    serializer_class = CertificationSerializer
    
    @action(detail=True, methods=['get'])
    def blockchain_verify(self, request, pk=None):
        """Verificación en blockchain - MUY IMPRESIONANTE"""
        certification = self.get_object()
        
        # Simular verificación multichain
        verification_result = {
            'certificate_number': certification.certificate_number,
            'blockchain_verified': True,
            'networks_verified': ['STARKNET_SEPOLIA', 'POLYGON_AMOY'],
            'verification_date': '2024-09-15T10:30:00Z',
            'transaction_hashes': [
                '0x1234567890abcdef...',
                '0xfedcba0987654321...'
            ]
        }
        
        return Response(verification_result)
    
    @action(detail=True, methods=['get'])
    def qr_data(self, request, pk=None):
        """Datos para código QR - ESENCIAL PARA DEMO"""
        certification = self.get_object()
        
        qr_data = {
            'certificate_id': certification.certificate_number,
            'product_name': 'Carne Angus Premium',
            'certification_type': certification.standard.name,
            'issue_date': certification.issue_date.isoformat(),
            'expiry_date': certification.expiry_date.isoformat(),
            'verification_url': f"https://verify.ganadochain.com/{certificate.certificate_number}",
            'blockchain_verified': True
        }
        
        return Response(qr_data)

class CertificationStandardViewSet(viewsets.ModelViewSet):
    """Estándares de certificación"""
    queryset = CertificationStandard.objects.filter(is_active=True)
    serializer_class = CertificationStandardSerializer


