from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from .models import CattleAuditTrail
import csv
import json

class AuditTrailExportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        format = request.query_params.get('format', 'json')
        days = int(request.query_params.get('days', 30))
        
        from_date = timezone.now() - timezone.timedelta(days=days)
        audits = CattleAuditTrail.objects.filter(timestamp__gte=from_date)
        
        if not request.user.is_staff:
            audits = audits.filter(user=request.user)
        
        if format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="audit_trail_{timezone.now().date()}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Timestamp', 'User', 'Object Type', 'Object ID', 'Action', 'IP Address', 'Blockchain TX'])
            
            for audit in audits:
                writer.writerow([
                    audit.timestamp,
                    audit.user.username if audit.user else 'System',
                    audit.object_type,
                    audit.object_id,
                    audit.action_type,
                    audit.ip_address,
                    audit.blockchain_tx_hash or ''
                ])
            
            return response
        
        else:  # JSON
            data = [
                {
                    'timestamp': audit.timestamp,
                    'user': audit.user.username if audit.user else 'System',
                    'object_type': audit.object_type,
                    'object_id': audit.object_id,
                    'action': audit.action_type,
                    'ip_address': audit.ip_address,
                    'blockchain_tx': audit.blockchain_tx_hash
                }
                for audit in audits
            ]
            
            return Response({'audits': data, 'count': len(data)})
