from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RewardDistributionViewSet, 
    StakingPoolViewSet, 
    RewardClaimView,
    BulkRewardClaimView,
    StakeTokensView,
    UnstakeTokensView,
    ReputationLeaderboardView, 
    UserRewardsStatsView,
    GlobalRewardsStatsView,
    ActionTypeRewardsView
)

router = DefaultRouter()
router.register(r'rewards', RewardDistributionViewSet, basename='reward')  # Add basename here
router.register(r'staking', StakingPoolViewSet, basename='staking-pool')   # Add basename here too

urlpatterns = [
    path('', include(router.urls)),
    
    # Rutas de recompensas
    path('claim/<int:reward_id>/', RewardClaimView.as_view(), name='reward-claim'),
    path('claim/bulk/', BulkRewardClaimView.as_view(), name='bulk-reward-claim'),
    
    # Rutas de staking
    path('staking/action/stake/', StakeTokensView.as_view(), name='stake-tokens'),
    path('staking/action/unstake/<int:staking_pool_id>/', UnstakeTokensView.as_view(), name='unstake-tokens'),
    
    # Rutas de estadísticas y leaderboards
    path('leaderboard/', ReputationLeaderboardView.as_view(), name='reputation-leaderboard'),
    path('stats/', UserRewardsStatsView.as_view(), name='user-rewards-stats'),
    path('stats/<int:user_id>/', UserRewardsStatsView.as_view(), name='specific-user-rewards-stats'),
    path('stats/global/', GlobalRewardsStatsView.as_view(), name='global-rewards-stats'),
    path('stats/action-types/', ActionTypeRewardsView.as_view(), name='action-type-rewards'),
]