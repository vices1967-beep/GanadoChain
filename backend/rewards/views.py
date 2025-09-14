from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Avg, Count
from django.contrib.auth import get_user_model

# Importaciones corregidas desde las ubicaciones correctas
from users.models import User
from users.reputation_models import RewardDistribution, StakingPool, ReputationScore
from users.serializers import (
    RewardDistributionSerializer, 
    StakingPoolSerializer,
    ClaimRewardsSerializer,
    StakeTokensSerializer,
    RewardStatsSerializer,
    StakingStatsSerializer
)

import logging

logger = logging.getLogger(__name__)

class RewardDistributionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RewardDistributionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = RewardDistribution.objects.all()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        action_type = self.request.query_params.get('action_type')
        is_claimed = self.request.query_params.get('is_claimed')
        
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        if is_claimed == 'true':
            queryset = queryset.filter(is_claimed=True)
        elif is_claimed == 'false':
            queryset = queryset.filter(is_claimed=False)
            
        return queryset.order_by('-distribution_date')

class StakingPoolViewSet(viewsets.ModelViewSet):
    serializer_class = StakingPoolSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = StakingPool.objects.all()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RewardClaimView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, reward_id):
        reward = get_object_or_404(RewardDistribution, id=reward_id, user=request.user)
        
        if reward.is_claimed:
            return Response({
                'error': 'Recompensa ya reclamada'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Aquí iría la lógica de blockchain para claim
        try:
            # Simulación de transacción blockchain
            # En producción, aquí se conectaría con el contrato inteligente
            reward.is_claimed = True
            reward.save()
            
            return Response({
                'success': True,
                'message': 'Recompensa reclamada exitosamente',
                'amount': float(reward.tokens_awarded)
            })
            
        except Exception as e:
            logger.error(f"Error reclamando recompensa {reward_id}: {str(e)}")
            return Response({
                'error': f'Error reclamando recompensa: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class BulkRewardClaimView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ClaimRewardsSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        reward_ids = serializer.validated_data['reward_ids']
        wallet_address = serializer.validated_data['wallet_address']
        
        rewards = RewardDistribution.objects.filter(
            id__in=reward_ids, 
            user=request.user,
            is_claimed=False
        )
        
        if len(rewards) != len(reward_ids):
            return Response({
                'error': 'Algunas recompensas no son válidas o ya fueron reclamadas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            total_amount = sum(float(reward.tokens_awarded) for reward in rewards)
            
            # Aquí iría la lógica de blockchain para bulk claim
            # En producción, se conectaría con el contrato inteligente
            
            rewards.update(is_claimed=True)
            
            return Response({
                'success': True,
                'message': f'{len(rewards)} recompensas reclamadas exitosamente',
                'total_amount': total_amount,
                'wallet_address': wallet_address
            })
            
        except Exception as e:
            logger.error(f"Error reclamando recompensas en bulk: {str(e)}")
            return Response({
                'error': f'Error reclamando recompensas: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class StakeTokensView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = StakeTokensSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        amount = serializer.validated_data['amount']
        duration_days = serializer.validated_data['duration_days']
        wallet_address = serializer.validated_data['wallet_address']
        
        # Verificar si el usuario ya tiene un staking pool activo
        existing_pool = StakingPool.objects.filter(user=request.user).first()
        if existing_pool:
            return Response({
                'error': 'Ya tienes un pool de staking activo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Aquí iría la lógica de blockchain para staking
            # En producción, se conectaría con el contrato inteligente
            
            # APY basado en la duración (ejemplo)
            apy_map = {
                30: 5.0,   # 30 días: 5% APY
                90: 8.0,   # 90 días: 8% APY
                180: 12.0, # 180 días: 12% APY
                365: 15.0  # 365 días: 15% APY
            }
            
            apy = apy_map.get(duration_days, 5.0)
            
            staking_pool = StakingPool.objects.create(
                user=request.user,
                tokens_staked=amount,
                staking_start=timezone.now(),
                staking_duration=duration_days,
                apy=apy,
                rewards_earned=0,
                blockchain_staking_id=None  # Se asignaría después de la transacción blockchain
            )
            
            return Response({
                'success': True,
                'message': 'Tokens stakeados exitosamente',
                'staking_pool_id': staking_pool.id,
                'amount': float(amount),
                'duration_days': duration_days,
                'apy': float(apy),
                'wallet_address': wallet_address
            })
            
        except Exception as e:
            logger.error(f"Error haciendo staking de tokens: {str(e)}")
            return Response({
                'error': f'Error haciendo staking: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class UnstakeTokensView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, staking_pool_id):
        staking_pool = get_object_or_404(StakingPool, id=staking_pool_id, user=request.user)
        
        # Verificar si el staking ha terminado
        from datetime import timedelta
        end_date = staking_pool.staking_start + timedelta(days=staking_pool.staking_duration)
        
        if timezone.now() < end_date:
            return Response({
                'error': 'El período de staking aún no ha terminado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Aquí iría la lógica de blockchain para unstaking
            # En producción, se conectaría con el contrato inteligente
            
            # Calcular recompensas finales
            total_rewards = float(staking_pool.tokens_staked) * float(staking_pool.apy) / 100 * staking_pool.staking_duration / 365
            
            staking_pool.rewards_earned = total_rewards
            staking_pool.save()
            
            return Response({
                'success': True,
                'message': 'Tokens unstakeados exitosamente',
                'staked_amount': float(staking_pool.tokens_staked),
                'rewards_earned': total_rewards,
                'total_amount': float(staking_pool.tokens_staked) + total_rewards
            })
            
        except Exception as e:
            logger.error(f"Error unstakeando tokens: {str(e)}")
            return Response({
                'error': f'Error unstakeando tokens: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class ReputationLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Obtener el top 100 de usuarios por reputación total
        User = get_user_model()
        leaderboard = User.objects.annotate(
            total_reputation=Sum('reputationscore__score')
        ).exclude(total_reputation=None).order_by('-total_reputation')[:100].values(
            'id', 'username', 'email', 'total_reputation'
        )
        
        return Response({'leaderboard': list(leaderboard)})

class UserRewardsStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        user = request.user if not user_id else get_object_or_404(User, id=user_id)
        
        if user != request.user and not request.user.is_staff:
            return Response({'error': 'Permiso denegado'}, status=status.HTTP_403_FORBIDDEN)
        
        rewards = RewardDistribution.objects.filter(user=user)
        staking_pools = StakingPool.objects.filter(user=user)
        
        stats = {
            'total_rewards': rewards.count(),
            'total_tokens_earned': float(rewards.aggregate(
                total=Sum('tokens_awarded'))['total'] or 0),
            'unclaimed_rewards': rewards.filter(is_claimed=False).count(),
            'unclaimed_tokens': float(rewards.filter(is_claimed=False).aggregate(
                total=Sum('tokens_awarded'))['total'] or 0),
            'rewards_by_type': rewards.values('action_type').annotate(
                count=Count('id'),
                total_tokens=Sum('tokens_awarded')
            ),
            'staking_info': {
                'active_pools': staking_pools.count(),
                'total_staked': float(staking_pools.aggregate(
                    total=Sum('tokens_staked'))['total'] or 0),
                'total_rewards_earned': float(staking_pools.aggregate(
                    total=Sum('rewards_earned'))['total'] or 0)
            }
        }
        
        return Response(stats)

class GlobalRewardsStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Permiso denegado'}, status=status.HTTP_403_FORBIDDEN)
        
        stats = {
            'total_rewards_distributed': RewardDistribution.objects.count(),
            'total_tokens_distributed': float(RewardDistribution.objects.aggregate(
                total=Sum('tokens_awarded'))['total'] or 0),
            'total_unclaimed_tokens': float(RewardDistribution.objects.filter(
                is_claimed=False).aggregate(total=Sum('tokens_awarded'))['total'] or 0),
            'rewards_by_type': RewardDistribution.objects.values('action_type').annotate(
                count=Count('id'),
                total_tokens=Sum('tokens_awarded')
            ),
            'staking_stats': {
                'total_pools': StakingPool.objects.count(),
                'total_staked': float(StakingPool.objects.aggregate(
                    total=Sum('tokens_staked'))['total'] or 0),
                'avg_apy': float(StakingPool.objects.aggregate(
                    avg_apy=Avg('apy'))['avg_apy'] or 0),
                'total_rewards_paid': float(StakingPool.objects.aggregate(
                    total=Sum('rewards_earned'))['total'] or 0)
            }
        }
        
        return Response(stats)

class ActionTypeRewardsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        action_types = RewardDistribution.objects.values('action_type').annotate(
            total_rewards=Count('id'),
            total_tokens=Sum('tokens_awarded'),
            avg_reward=Avg('tokens_awarded')
        ).order_by('-total_tokens')
        
        # Mapear nombres de acción más descriptivos
        action_names = {
            'ANIMAL_REGISTRATION': 'Registro de Animal',
            'HEALTH_UPDATE': 'Actualización de Salud',
            'LOCATION_UPDATE': 'Actualización de Ubicación',
            'BATCH_CREATION': 'Creación de Lote',
            'CERTIFICATION': 'Certificación',
            'DATA_QUALITY': 'Calidad de Datos',
            'COMMUNITY_CONTRIBUTION': 'Contribución Comunitaria',
            'IOT_DATA_SUBMISSION': 'Envío de Datos IoT'
        }
        
        result = []
        for action in action_types:
            result.append({
                'action_type': action['action_type'],
                'action_display': action_names.get(action['action_type'], action['action_type']),
                'total_rewards': action['total_rewards'],
                'total_tokens': float(action['total_tokens'] or 0),
                'avg_reward': float(action['avg_reward'] or 0)
            })
        
        return Response({'action_types': result})