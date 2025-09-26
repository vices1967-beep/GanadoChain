from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import CertificationStandard, AnimalCertification
from .serializers import CertificationStandardSerializer, AnimalCertificationSerializer
import logging

logger = logging.getLogger(__name__)

class CertificationStandardViewSet(viewsets.ModelViewSet):
    queryset = CertificationStandard.objects.filter(is_active=True)
    serializer_class = CertificationStandardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            from rest_framework.permissions import IsAdminUser
            return [IsAdminUser()]
        return [IsAuthenticated()]

class AnimalCertificationViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalCertificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AnimalCertification.objects.all()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(animal__owner=self.request.user)
        
        animal_id = self.request.query_params.get('animal_id')
        standard_id = self.request.query_params.get('standard_id')
        revoked = self.request.query_params.get('revoked')
        
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if standard_id:
            queryset = queryset.filter(standard_id=standard_id)
        if revoked == 'true':
            queryset = queryset.filter(revoked=True)
        elif revoked == 'false':
            queryset = queryset.filter(revoked=False)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        certification = self.get_object()
        reason = request.data.get('reason', '')
        
        certification.revoked = True
        certification.revocation_reason = reason
        certification.save()
        
        return Response({
            'success': True,
            'message': 'Certificación revocada',
            'certification_id': certification.id
        })
