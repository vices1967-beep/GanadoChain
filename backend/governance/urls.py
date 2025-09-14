from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GovernanceProposalViewSet, 
    VoteViewSet, 
    ProposalStatsView,
    UserVotingStatsView,
    ActiveProposalsView,
    ProposalTimelineView
)

router = DefaultRouter()
router.register(r'proposals', GovernanceProposalViewSet, basename='governanceproposal')
router.register(r'votes', VoteViewSet, basename='vote')

urlpatterns = [
    # -------------------------------------------------------------------------
    # RUTAS DEL ROUTER (API REST)
    # -------------------------------------------------------------------------
    path('', include(router.urls)),
    
    # -------------------------------------------------------------------------
    # ESTADÍSTICAS DE PROPUESTAS
    # -------------------------------------------------------------------------
    path(
        'stats/', 
        ProposalStatsView.as_view(), 
        name='proposal-stats',
        kwargs={'description': 'Estadísticas generales de propuestas y votación'}
    ),
    path(
        'stats/<int:proposal_id>/', 
        ProposalStatsView.as_view(), 
        name='proposal-detail-stats',
        kwargs={'description': 'Estadísticas detalladas de una propuesta específica'}
    ),
    
    # -------------------------------------------------------------------------
    # ESTADÍSTICAS DE USUARIOS
    # -------------------------------------------------------------------------
    path(
        'user-stats/', 
        UserVotingStatsView.as_view(), 
        name='user-voting-stats',
        kwargs={'description': 'Estadísticas de votación del usuario actual'}
    ),
    path(
        'user-stats/<int:user_id>/', 
        UserVotingStatsView.as_view(), 
        name='specific-user-voting-stats',
        kwargs={'description': 'Estadísticas de votación de un usuario específico (solo admin)'}
    ),
    
    # -------------------------------------------------------------------------
    # PROPUESTAS ACTIVAS
    # -------------------------------------------------------------------------
    path(
        'active/', 
        ActiveProposalsView.as_view(), 
        name='active-proposals',
        kwargs={'description': 'Lista de propuestas activas para votación'}
    ),
    
    # -------------------------------------------------------------------------
    # TIMELINE DE ACTIVIDAD
    # -------------------------------------------------------------------------
    path(
        'timeline/', 
        ProposalTimelineView.as_view(), 
        name='proposal-timeline',
        kwargs={'description': 'Timeline de actividad de propuestas y votos'}
    ),
    
    # -------------------------------------------------------------------------
    # ENDPOINTS ESPECÍFICOS PARA ACCIONES PERSONALIZADAS
    # -------------------------------------------------------------------------
    path(
        'proposals/<int:pk>/voting-status/', 
        GovernanceProposalViewSet.as_view({'get': 'voting_status'}), 
        name='proposal-voting-status',
        kwargs={'description': 'Obtener el estado de votación de una propuesta'}
    ),
    path(
        'proposals/<int:pk>/vote/', 
        GovernanceProposalViewSet.as_view({'post': 'vote'}), 
        name='proposal-vote',
        kwargs={'description': 'Votar en una propuesta específica'}
    ),
    path(
        'proposals/<int:pk>/update-status/', 
        GovernanceProposalViewSet.as_view({'post': 'update_status'}), 
        name='proposal-update-status',
        kwargs={'description': 'Actualizar el estado de una propuesta (solo admin)'}
    ),
    path(
        'my-votes/', 
        VoteViewSet.as_view({'get': 'my_votes'}), 
        name='my-votes',
        kwargs={'description': 'Obtener todos los votos del usuario actual'}
    ),
]

# Para incluir en el urls.py principal
app_name = 'governance'

# Documentación de parámetros de query disponibles
GOVERNANCE_QUERY_PARAMS = {
    'proposals': {
        'status': 'Filtrar por estado (PENDING, ACTIVE, APPROVED, REJECTED, EXECUTED)',
        'type': 'Filtrar por tipo (PARAMETER_CHANGE, UPGRADE, GRANT, POLICY)',
        'proposed_by': 'Filtrar por ID del proponente',
        'voting_status': 'Filtrar por estado de votación (active, upcoming, completed)'
    },
    'votes': {
        'proposal_id': 'Filtrar por ID de propuesta',
        'voter_id': 'Filtrar por ID de votante',
        'vote_value': 'Filtrar por valor de voto (true/false)'
    },
    'timeline': {
        'days': 'Número de días para el timeline (default: 30)'
    }
}

# Ejemplos de uso para documentación
GOVERNANCE_API_EXAMPLES = {
    'proposals': {
        'all': '/governance/proposals/',
        'filtered': '/governance/proposals/?status=ACTIVE&type=PARAMETER_CHANGE',
        'active_voting': '/governance/proposals/?voting_status=active',
        'voting_status': '/governance/proposals/123/voting-status/',
        'vote': '/governance/proposals/123/vote/'
    },
    'votes': {
        'all': '/governance/votes/',
        'my_votes': '/governance/my-votes/',
        'filtered': '/governance/votes/?proposal_id=123&vote_value=true'
    },
    'stats': {
        'general': '/governance/stats/',
        'proposal_detail': '/governance/stats/456/',
        'user_stats': '/governance/user-stats/',
        'specific_user': '/governance/user-stats/789/'
    },
    'active': {
        'proposals': '/governance/active/'
    },
    'timeline': {
        'activity': '/governance/timeline/?days=60'
    }
}