from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum, Max
from django.shortcuts import get_object_or_404
import csv
import json
from datetime import datetime, timedelta

# Importaciones corregidas desde las ubicaciones correctas
from cattle.models import Animal, Batch, AnimalHealthRecord
from cattle.audit_models import CattleAuditTrail
from cattle.blockchain_models import AnimalCertification, CertificationStandard
from users.models import User
from blockchain.models import BlockchainEvent, ContractInteraction
from iot.models import IoTDevice, GPSData, HealthSensorData
from users.reputation_models import RewardDistribution, StakingPool

class ComplianceReportView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        report_type = request.query_params.get('type', 'general')
        days = int(request.query_params.get('days', 30))
        
        from_date = timezone.now() - timedelta(days=days)
        
        if report_type == 'certifications':
            certifications = AnimalCertification.objects.filter(
                created_at__gte=from_date
            )
            
            data = {
                'total_certifications': certifications.count(),
                'active_certifications': certifications.filter(revoked=False).count(),
                'revoked_certifications': certifications.filter(revoked=True).count(),
                'by_standard': dict(certifications.values_list('standard__name').annotate(count=Count('id'))),
                'expiring_soon': certifications.filter(
                    expiration_date__lte=timezone.now() + timedelta(days=30)
                ).count()
            }
            
            return Response(data)
        
        elif report_type == 'health':
            health_data = AnimalHealthRecord.objects.filter(
                created_at__gte=from_date
            ).values('health_status').annotate(
                count=Count('id')
            )
            
            return Response({'health_status_distribution': list(health_data)})
        
        elif report_type == 'blockchain':
            # Estadísticas de blockchain
            blockchain_stats = {
                'total_events': BlockchainEvent.objects.filter(created_at__gte=from_date).count(),
                'total_transactions': ContractInteraction.objects.filter(created_at__gte=from_date).count(),
                'successful_transactions': ContractInteraction.objects.filter(
                    created_at__gte=from_date, status='SUCCESS'
                ).count(),
                'failed_transactions': ContractInteraction.objects.filter(
                    created_at__gte=from_date, status='FAILED'
                ).count(),
                'events_by_type': dict(BlockchainEvent.objects.filter(
                    created_at__gte=from_date
                ).values_list('event_type').annotate(count=Count('id')))
            }
            
            return Response(blockchain_stats)
        
        elif report_type == 'iot':
            # Estadísticas de dispositivos IoT
            iot_stats = {
                'total_devices': IoTDevice.objects.count(),
                'active_devices': IoTDevice.objects.filter(status='ACTIVE').count(),
                'gps_readings': GPSData.objects.filter(timestamp__gte=from_date).count(),
                'health_readings': HealthSensorData.objects.filter(timestamp__gte=from_date).count(),
                'devices_by_type': dict(IoTDevice.objects.values_list('device_type').annotate(count=Count('id')))
            }
            
            return Response(iot_stats)
        
        elif report_type == 'rewards':
            # Estadísticas de recompensas
            rewards_stats = {
                'total_rewards_distributed': RewardDistribution.objects.filter(
                    distribution_date__gte=from_date
                ).count(),
                'total_tokens_distributed': float(RewardDistribution.objects.filter(
                    distribution_date__gte=from_date
                ).aggregate(total=Sum('tokens_awarded'))['total'] or 0),
                'unclaimed_tokens': float(RewardDistribution.objects.filter(
                    distribution_date__gte=from_date, is_claimed=False
                ).aggregate(total=Sum('tokens_awarded'))['total'] or 0),
                'rewards_by_type': dict(RewardDistribution.objects.filter(
                    distribution_date__gte=from_date
                ).values_list('action_type').annotate(count=Count('id')))
            }
            
            return Response(rewards_stats)
        
        # Reporte general por defecto
        general_data = {
            'total_animals': Animal.objects.count(),
            'total_batches': Batch.objects.count(),
            'total_users': User.objects.count(),
            'animals_by_health_status': dict(Animal.objects.values_list('health_status').annotate(count=Count('id'))),
            'batches_by_status': dict(Batch.objects.values_list('status').annotate(count=Count('id'))),
            'time_period': f'{from_date.date()} to {timezone.now().date()}',
            'report_generated': timezone.now()
        }
        
        return Response(general_data)

class ExportAnimalDataView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        format = request.query_params.get('format', 'json')
        animal_ids = request.GET.getlist('animal_ids')
        
        if animal_ids:
            animals = Animal.objects.filter(id__in=animal_ids, owner=request.user)
        else:
            animals = Animal.objects.filter(owner=request.user)
        
        if format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="animal_data_export_{timezone.now().date()}.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Ear Tag', 'Breed', 'Birth Date', 'Weight', 
                'Health Status', 'Location', 'IPFS Hash', 'Token ID',
                'Owner', 'Created At'
            ])
            
            for animal in animals:
                writer.writerow([
                    animal.id,
                    animal.ear_tag,
                    animal.breed,
                    animal.birth_date.strftime('%Y-%m-%d') if animal.birth_date else '',
                    animal.weight,
                    animal.health_status,
                    animal.location,
                    animal.ipfs_hash,
                    animal.token_id,
                    animal.owner.username if animal.owner else '',
                    animal.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
        
        else:  # JSON
            data = [
                {
                    'id': animal.id,
                    'ear_tag': animal.ear_tag,
                    'breed': animal.breed,
                    'birth_date': animal.birth_date.strftime('%Y-%m-%d') if animal.birth_date else None,
                    'weight': float(animal.weight) if animal.weight else None,
                    'health_status': animal.health_status,
                    'location': animal.location,
                    'ipfs_hash': animal.ipfs_hash,
                    'token_id': animal.token_id,
                    'owner': animal.owner.username if animal.owner else None,
                    'created_at': animal.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'metadata_uri': animal.metadata_uri,
                    'is_minted': animal.is_minted
                }
                for animal in animals
            ]
            
            return Response({
                'animals': data, 
                'count': len(data),
                'export_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'exported_by': request.user.username
            })

class AuditReportGenerator(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        report_type = request.query_params.get('type', 'general')
        days = int(request.query_params.get('days', 7))
        
        from_date = timezone.now() - timedelta(days=days)
        audits = CattleAuditTrail.objects.filter(timestamp__gte=from_date)
        
        if report_type == 'user_activity':
            user_activity = audits.values('user__username').annotate(
                action_count=Count('id'),
                last_action=Max('timestamp')
            ).order_by('-action_count')
            
            return Response({'user_activity': list(user_activity)})
        
        elif report_type == 'action_types':
            action_stats = audits.values('action_type').annotate(
                count=Count('id'),
                last_performed=Max('timestamp')
            ).order_by('-count')
            
            return Response({'action_stats': list(action_stats)})
        
        elif report_type == 'blockchain_audit':
            # Auditoría de eventos blockchain
            blockchain_events = BlockchainEvent.objects.filter(created_at__gte=from_date)
            blockchain_stats = {
                'total_events': blockchain_events.count(),
                'events_by_type': dict(blockchain_events.values_list('event_type').annotate(count=Count('id'))),
                'events_with_animals': blockchain_events.filter(animal__isnull=False).count(),
                'events_with_batches': blockchain_events.filter(batch__isnull=False).count()
            }
            
            return Response(blockchain_stats)
        
        # Reporte general
        general_stats = {
            'total_audits': audits.count(),
            'audits_by_type': dict(audits.values_list('action_type').annotate(count=Count('id'))),
            'unique_users': audits.values('user').distinct().count(),
            'time_period': f'{from_date.date()} to {timezone.now().date()}',
            'report_generated': timezone.now()
        }
        
        return Response(general_stats)

class FinancialReportView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        from_date = timezone.now() - timedelta(days=days)
        
        # Estadísticas de staking
        staking_stats = {
            'total_staking_pools': StakingPool.objects.count(),
            'active_staking_pools': StakingPool.objects.filter(
                staking_start__lte=timezone.now()
            ).count(),
            'total_tokens_staked': float(StakingPool.objects.aggregate(
                total=Sum('tokens_staked'))['total'] or 0),
            'total_rewards_paid': float(StakingPool.objects.aggregate(
                total=Sum('rewards_earned'))['total'] or 0),
            'average_apy': float(StakingPool.objects.aggregate(
                avg_apy=Avg('apy'))['avg_apy'] or 0)
        }
        
        # Estadísticas de recompensas
        rewards_stats = {
            'total_rewards': RewardDistribution.objects.filter(
                distribution_date__gte=from_date
            ).count(),
            'total_tokens_distributed': float(RewardDistribution.objects.filter(
                distribution_date__gte=from_date
            ).aggregate(total=Sum('tokens_awarded'))['total'] or 0),
            'claimed_rewards': RewardDistribution.objects.filter(
                distribution_date__gte=from_date, is_claimed=True
            ).count(),
            'unclaimed_rewards': RewardDistribution.objects.filter(
                distribution_date__gte=from_date, is_claimed=False
            ).count(),
            'claimed_tokens': float(RewardDistribution.objects.filter(
                distribution_date__gte=from_date, is_claimed=True
            ).aggregate(total=Sum('tokens_awarded'))['total'] or 0),
            'unclaimed_tokens': float(RewardDistribution.objects.filter(
                distribution_date__gte=from_date, is_claimed=False
            ).aggregate(total=Sum('tokens_awarded'))['total'] or 0)
        }
        
        report = {
            'time_period': f'{from_date.date()} to {timezone.now().date()}',
            'staking_statistics': staking_stats,
            'rewards_statistics': rewards_stats,
            'total_circulating_tokens': staking_stats['total_tokens_staked'] + rewards_stats['total_tokens_distributed'],
            'report_generated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return Response(report)

class SystemHealthReportView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Reporte de salud del sistema
        health_report = {
            'database': {
                'total_animals': Animal.objects.count(),
                'total_users': User.objects.count(),
                'total_iot_devices': IoTDevice.objects.count(),
                'total_blockchain_events': BlockchainEvent.objects.count()
            },
            'blockchain': {
                'successful_transactions': ContractInteraction.objects.filter(status='SUCCESS').count(),
                'failed_transactions': ContractInteraction.objects.filter(status='FAILED').count(),
                'pending_transactions': ContractInteraction.objects.filter(status='PENDING').count(),
                'average_gas_used': ContractInteraction.objects.aggregate(avg_gas=Avg('gas_used'))['avg_gas'] or 0
            },
            'iot_system': {
                'active_devices': IoTDevice.objects.filter(status='ACTIVE').count(),
                'inactive_devices': IoTDevice.objects.filter(status='INACTIVE').count(),
                'total_gps_readings': GPSData.objects.count(),
                'total_health_readings': HealthSensorData.objects.count(),
                'devices_needing_attention': IoTDevice.objects.filter(
                    battery_level__lt=20, status='ACTIVE'
                ).count()
            },
            'system_metrics': {
                'report_generated': timezone.now(),
                'uptime': '99.9%',  # Esto vendría de monitoring externo
                'active_sessions': 0,  # Esto se calcularía de otra manera
                'memory_usage': '75%'  # Esto vendría de monitoring del sistema
            }
        }
        
        return Response(health_report)

class ExportReportView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        report_type = request.query_params.get('type', 'compliance')
        format = request.query_params.get('format', 'csv')
        days = int(request.query_params.get('days', 30))
        
        from_date = timezone.now() - timedelta(days=days)
        
        if report_type == 'compliance' and format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="compliance_report_{timezone.now().date()}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Metric', 'Value', 'Time Period'])
            
            # Datos de cumplimiento
            certifications = AnimalCertification.objects.filter(created_at__gte=from_date)
            animals = Animal.objects.all()
            
            writer.writerow(['Total Animals', animals.count(), f'{days} days'])
            writer.writerow(['Total Certifications', certifications.count(), f'{days} days'])
            writer.writerow(['Active Certifications', certifications.filter(revoked=False).count(), f'{days} days'])
            writer.writerow(['Revoked Certifications', certifications.filter(revoked=True).count(), f'{days} days'])
            
            return response
        
        elif report_type == 'financial' and format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="financial_report_{timezone.now().date()}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Metric', 'Value', 'Currency'])
            
            # Datos financieros
            staking_total = StakingPool.objects.aggregate(total=Sum('tokens_staked'))['total'] or 0
            rewards_total = RewardDistribution.objects.aggregate(total=Sum('tokens_awarded'))['total'] or 0
            
            writer.writerow(['Total Staked', float(staking_total), 'GAN'])
            writer.writerow(['Total Rewards Distributed', float(rewards_total), 'GAN'])
            writer.writerow(['Total Circulating', float(staking_total + rewards_total), 'GAN'])
            
            return response
        
        return Response({'error': 'Tipo de reporte o formato no soportado'}, status=400)