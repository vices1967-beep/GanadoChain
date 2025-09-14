from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Sum, Avg
from django.contrib.auth import get_user_model

# Importaciones corregidas desde las ubicaciones correctas
from blockchain.models import GovernanceProposal, Vote
from blockchain.serializers import (
    GovernanceProposalSerializer, 
    VoteSerializer,
    CreateProposalSerializer,
    CreateVoteSerializer,
    ProposalParameterSerializer
)
from users.models import User
import logging

logger = logging.getLogger(__name__)

class GovernanceProposalViewSet(viewsets.ModelViewSet):
    serializer_class = GovernanceProposalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateProposalSerializer
        return GovernanceProposalSerializer
    
    def get_queryset(self):
        queryset = GovernanceProposal.objects.all()
        
        status_filter = self.request.query_params.get('status')
        proposal_type = self.request.query_params.get('type')
        proposed_by = self.request.query_params.get('proposed_by')
        voting_status = self.request.query_params.get('voting_status')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if proposal_type:
            queryset = queryset.filter(proposal_type=proposal_type)
        if proposed_by:
            queryset = queryset.filter(proposed_by_id=proposed_by)
        
        # Filtrar por estado de votación
        if voting_status:
            now = timezone.now()
            if voting_status == 'active':
                queryset = queryset.filter(voting_start__lte=now, voting_end__gte=now)
            elif voting_status == 'upcoming':
                queryset = queryset.filter(voting_start__gt=now)
            elif voting_status == 'completed':
                queryset = queryset.filter(voting_end__lt=now)
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(proposed_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def voting_status(self, request, pk=None):
        proposal = self.get_object()
        now = timezone.now()
        
        status_info = {
            'proposal_id': proposal.id,
            'current_time': now,
            'voting_start': proposal.voting_start,
            'voting_end': proposal.voting_end,
            'status': proposal.status,
            'voting_period': 'upcoming'
        }
        
        if now >= proposal.voting_start and now <= proposal.voting_end:
            status_info['voting_period'] = 'active'
            status_info['time_remaining'] = proposal.voting_end - now
        elif now > proposal.voting_end:
            status_info['voting_period'] = 'completed'
        
        return Response(status_info)
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        proposal = self.get_object()
        
        serializer = CreateVoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        vote_value = serializer.validated_data['vote_value']
        
        # Validaciones de la propuesta
        if proposal.status != 'ACTIVE':
            return Response({
                'error': 'La propuesta no está activa para votación'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        now = timezone.now()
        if now < proposal.voting_start or now > proposal.voting_end:
            return Response({
                'error': 'Fuera del período de votación'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya votó
        existing_vote = Vote.objects.filter(proposal=proposal, voter=request.user).first()
        if existing_vote:
            return Response({
                'error': 'Ya has votado en esta propuesta'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Aquí iría la lógica de blockchain para obtener el voting power
            # En producción, se conectaría con el contrato inteligente
            voting_power = 1.0  # Esto vendría de blockchain
            
            # Crear voto
            vote = Vote.objects.create(
                proposal=proposal,
                voter=request.user,
                vote_value=vote_value,
                voting_power=voting_power,
                blockchain_vote_hash=f"0x{hash(str(timezone.now()) + str(proposal.id))[:64]}"
            )
            
            return Response({
                'success': True, 
                'message': 'Voto registrado exitosamente',
                'vote_id': vote.id,
                'vote_value': vote_value,
                'voting_power': voting_power
            })
            
        except Exception as e:
            logger.error(f"Error registrando voto: {str(e)}")
            return Response({
                'error': f'Error registrando voto: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        proposal = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['PENDING', 'ACTIVE', 'APPROVED', 'REJECTED', 'EXECUTED']:
            return Response({
                'error': 'Estado inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        proposal.status = new_status
        proposal.save()
        
        return Response({
            'success': True,
            'message': f'Estado actualizado a {new_status}',
            'proposal_id': proposal.id,
            'new_status': new_status
        })

class VoteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Vote.objects.all()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(voter=self.request.user)
        
        proposal_id = self.request.query_params.get('proposal_id')
        voter_id = self.request.query_params.get('voter_id')
        vote_value = self.request.query_params.get('vote_value')
        
        if proposal_id:
            queryset = queryset.filter(proposal_id=proposal_id)
        if voter_id:
            queryset = queryset.filter(voter_id=voter_id)
        if vote_value:
            queryset = queryset.filter(vote_value=vote_value)
            
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def my_votes(self, request):
        votes = Vote.objects.filter(voter=request.user).order_by('-created_at')
        serializer = self.get_serializer(votes, many=True)
        return Response(serializer.data)

class ProposalStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, proposal_id=None):
        if proposal_id:
            proposal = get_object_or_404(GovernanceProposal, id=proposal_id)
            
            votes = Vote.objects.filter(proposal=proposal)
            total_votes = votes.count()
            
            stats = {
                'proposal_id': proposal.id,
                'proposal_title': proposal.title,
                'total_votes': total_votes,
                'yes_votes': votes.filter(vote_value=True).count(),
                'no_votes': votes.filter(vote_value=False).count(),
                'yes_percentage': (votes.filter(vote_value=True).count() / total_votes * 100) if total_votes > 0 else 0,
                'no_percentage': (votes.filter(vote_value=False).count() / total_votes * 100) if total_votes > 0 else 0,
                'voting_power_total': float(votes.aggregate(total=Sum('voting_power'))['total'] or 0),
                'voting_power_yes': float(votes.filter(vote_value=True).aggregate(total=Sum('voting_power'))['total'] or 0),
                'voting_power_no': float(votes.filter(vote_value=False).aggregate(total=Sum('voting_power'))['total'] or 0),
                'unique_voters': votes.values('voter').distinct().count(),
                'quorum_met': self.check_quorum(proposal, votes)
            }
            
            return Response(stats)
        
        else:
            # Stats generales
            total_proposals = GovernanceProposal.objects.count()
            
            stats = {
                'total_proposals': total_proposals,
                'proposals_by_status': dict(GovernanceProposal.objects.values_list('status').annotate(count=Count('id'))),
                'proposals_by_type': dict(GovernanceProposal.objects.values_list('proposal_type').annotate(count=Count('id'))),
                'active_proposals': GovernanceProposal.objects.filter(status='ACTIVE').count(),
                'completed_proposals': GovernanceProposal.objects.filter(
                    Q(status='APPROVED') | Q(status='REJECTED') | Q(status='EXECUTED')
                ).count(),
                'total_votes': Vote.objects.count(),
                'unique_voters': Vote.objects.values('voter').distinct().count(),
                'participation_rate': (Vote.objects.values('voter').distinct().count() / User.objects.count() * 100) if User.objects.count() > 0 else 0
            }
            
            return Response(stats)
    
    def check_quorum(self, proposal, votes):
        # Lógica para verificar si se alcanzó el quórum
        # Esto debería venir de blockchain o configuración
        total_voting_power = float(votes.aggregate(total=Sum('voting_power'))['total'] or 0)
        return total_voting_power >= 1000  # Ejemplo de quórum

class UserVotingStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        user = request.user if not user_id else get_object_or_404(User, id=user_id)
        
        if user != request.user and not request.user.is_staff:
            return Response({'error': 'Permiso denegado'}, status=status.HTTP_403_FORBIDDEN)
        
        user_votes = Vote.objects.filter(voter=user)
        user_proposals = GovernanceProposal.objects.filter(proposed_by=user)
        
        stats = {
            'user_id': user.id,
            'username': user.username,
            'total_votes': user_votes.count(),
            'total_proposals': user_proposals.count(),
            'votes_by_decision': {
                'yes': user_votes.filter(vote_value=True).count(),
                'no': user_votes.filter(vote_value=False).count()
            },
            'proposals_by_status': dict(user_proposals.values_list('status').annotate(count=Count('id'))),
            'voting_power_total': float(user_votes.aggregate(total=Sum('voting_power'))['total'] or 0),
            'participation_rate': (user_votes.count() / GovernanceProposal.objects.filter(status='ACTIVE').count() * 100) if GovernanceProposal.objects.filter(status='ACTIVE').count() > 0 else 0,
            'last_vote': user_votes.order_by('-created_at').first().created_at if user_votes.exists() else None,
            'voting_consistency': self.calculate_consistency(user_votes)
        }
        
        return Response(stats)
    
    def calculate_consistency(self, votes):
        if votes.count() == 0:
            return 0
        yes_votes = votes.filter(vote_value=True).count()
        return (yes_votes / votes.count() * 100) if votes.count() > 0 else 0

class ActiveProposalsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        now = timezone.now()
        active_proposals = GovernanceProposal.objects.filter(
            voting_start__lte=now, 
            voting_end__gte=now,
            status='ACTIVE'
        ).order_by('voting_end')
        
        serializer = GovernanceProposalSerializer(active_proposals, many=True)
        return Response({
            'active_proposals': serializer.data,
            'count': active_proposals.count(),
            'current_time': now
        })

class ProposalTimelineView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        from_date = timezone.now() - timezone.timedelta(days=days)
        
        timeline = GovernanceProposal.objects.filter(
            created_at__gte=from_date
        ).values('created_at__date').annotate(
            proposals_count=Count('id'),
            votes_count=Count('vote')
        ).order_by('created_at__date')
        
        return Response({
            'timeline': list(timeline),
            'time_period': f'{from_date.date()} to {timezone.now().date()}',
            'total_proposals': GovernanceProposal.objects.filter(created_at__gte=from_date).count(),
            'total_votes': Vote.objects.filter(created_at__gte=from_date).count()
        })