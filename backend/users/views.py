from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, UserUpdateSerializer,
    UserListSerializer, ChangePasswordSerializer, WalletConnectSerializer,
    BlockchainRoleSerializer, UserActivityLogSerializer, UserPreferenceSerializer,
    APITokenSerializer, APITokenCreateSerializer, UserStatsSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    UserSearchSerializer, UserRoleUpdateSerializer, VerifyWalletSerializer,
    UserExportSerializer, UserDetailSerializer, NotificationSerializer,
    UserRoleSerializer, ReputationScoreSerializer, NotificationCreateSerializer
)
from .models import UserActivityLog, UserPreference, APIToken
from .notification_models import Notification
from .reputation_models import UserRole, ReputationScore
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Para usuarios no admin, solo pueden ver su propio perfil
        if not self.request.user.is_staff:
            queryset = queryset.filter(id=self.request.user.id)
        
        # Filtros
        role = self.request.query_params.get('role', None)
        is_verified = self.request.query_params.get('is_verified', None)
        company = self.request.query_params.get('company', None)
        search = self.request.query_params.get('search', None)
        
        if role:
            queryset = queryset.filter(role=role)
        if is_verified == 'true':
            queryset = queryset.filter(is_verified=True)
        elif is_verified == 'false':
            queryset = queryset.filter(is_verified=False)
        if company:
            queryset = queryset.filter(company__icontains=company)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(wallet_address__icontains=search) |
                Q(company__icontains=search)
            )
            
        return queryset.order_by('-date_joined')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserProfileSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Solo el propio usuario o admin puede modificar/eliminar
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener el perfil del usuario actual"""
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Actualizar perfil del usuario actual"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Cambiar contraseña del usuario actual"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": ["Contraseña actual incorrecta."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Registrar actividad
            UserActivityLog.objects.create(
                user=user,
                action='PASSWORD_CHANGE',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({"message": "Contraseña cambiada exitosamente."})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def connect_wallet(self, request, pk=None):
        """Conectar wallet a usuario"""
        user = self.get_object()
        
        # Verificar permisos
        if user != request.user and not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para realizar esta acción."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = WalletConnectSerializer(data=request.data)
        if serializer.is_valid():
            # TODO: Implementar verificación de firma con web3
            # Por ahora solo actualizamos la wallet address
            wallet_address = serializer.validated_data['wallet_address']
            
            # Verificar que la wallet no esté en uso
            if User.objects.filter(wallet_address=wallet_address).exclude(id=user.id).exists():
                return Response(
                    {"wallet_address": ["Esta dirección wallet ya está en uso."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.wallet_address = wallet_address
            user.save()
            
            # Registrar actividad
            UserActivityLog.objects.create(
                user=user,
                action='BLOCKCHAIN_INTERACTION',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'action': 'wallet_connect', 'wallet_address': wallet_address}
            )
            
            return Response({"message": "Wallet conectada exitosamente."})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def verify_wallet(self, request, pk=None):
        """Verificar wallet mediante firma"""
        user = self.get_object()
        
        if user != request.user and not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para realizar esta acción."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = VerifyWalletSerializer(data=request.data)
        if serializer.is_valid():
            # TODO: Implementar verificación de firma real con web3
            # Por ahora simulamos la verificación
            wallet_address = serializer.validated_data['wallet_address']
            
            if user.wallet_address != wallet_address:
                return Response(
                    {"error": "La dirección wallet no coincide con la del usuario."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Simular verificación exitosa
            user.is_verified = True
            user.verification_date = timezone.now()
            user.save()
            
            # Registrar actividad
            UserActivityLog.objects.create(
                user=user,
                action='BLOCKCHAIN_INTERACTION',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'action': 'wallet_verification', 'wallet_address': wallet_address}
            )
            
            return Response({"message": "Wallet verificada exitosamente."})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de usuarios"""
        if not request.user.is_staff:
            return Response(
                {"error": "Solo los administradores pueden ver las estadísticas."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'users_by_role': dict(User.objects.values_list('role').annotate(count=Count('id'))),
            'new_users_today': User.objects.filter(date_joined__date=timezone.now().date()).count(),
            'new_users_this_week': User.objects.filter(date_joined__gte=timezone.now() - timezone.timedelta(days=7)).count(),
            'users_with_blockchain_roles': User.objects.annotate(roles_count=Count('blockchain_roles')).filter(roles_count__gt=0).count()
        }
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Búsqueda de usuarios"""
        if not request.user.is_staff:
            return Response(
                {"error": "Solo los administradores pueden buscar usuarios."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSearchSerializer(data=request.query_params)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            search_in = serializer.validated_data['search_in']
            
            q_objects = Q()
            if 'username' in search_in:
                q_objects |= Q(username__icontains=query)
            if 'email' in search_in:
                q_objects |= Q(email__icontains=query)
            if 'wallet' in search_in:
                q_objects |= Q(wallet_address__icontains=query)
            if 'name' in search_in:
                q_objects |= Q(first_name__icontains=query) | Q(last_name__icontains=query)
            if 'company' in search_in:
                q_objects |= Q(company__icontains=query)
            
            users = User.objects.filter(q_objects)[:50]  # Limitar resultados
            serializer = UserListSerializer(users, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def notifications(self, request, pk=None):
        """Obtener notificaciones del usuario"""
        user = self.get_object()
        
        if user != request.user and not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para ver estas notificaciones."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """Obtener roles detallados del usuario"""
        user = self.get_object()
        
        if user != request.user and not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para ver estos roles."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        roles = UserRole.objects.filter(user=user, is_active=True)
        serializer = UserRoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reputation(self, request, pk=None):
        """Obtener reputación del usuario"""
        user = self.get_object()
        
        if user != request.user and not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para ver esta reputación."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reputation_scores = ReputationScore.objects.filter(user=user)
        serializer = ReputationScoreSerializer(reputation_scores, many=True)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        
        # Registrar actividad
        UserActivityLog.objects.create(
            user=user,
            action='PROFILE_UPDATE',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            metadata={'action': 'registration'}
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = None  # TokenObtainPairView ya tiene su propio serializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Obtener usuario desde el username
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                
                # Registrar actividad de login
                UserActivityLog.objects.create(
                    user=user,
                    action='LOGIN',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
            except User.DoesNotExist:
                pass
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        return get_object_or_404(UserPreference, user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class APITokenViewSet(viewsets.ModelViewSet):
    serializer_class = APITokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return APIToken.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return APITokenCreateSerializer
        return APITokenSerializer
    
    def perform_create(self, serializer):
        import secrets
        token = secrets.token_hex(32)
        serializer.save(user=self.request.user, token=token)
        
        # Registrar actividad
        UserActivityLog.objects.create(
            user=self.request.user,
            action='BLOCKCHAIN_INTERACTION',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            metadata={'action': 'api_token_create', 'token_name': serializer.validated_data['name']}
        )
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerar token API"""
        api_token = self.get_object()
        
        import secrets
        api_token.token = secrets.token_hex(32)
        api_token.save()
        
        serializer = self.get_serializer(api_token)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivityLog.objects.filter(user=self.request.user).order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Actividad reciente"""
        limit = int(request.query_params.get('limit', 10))
        logs = self.get_queryset()[:limit]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Notificaciones no leídas"""
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marcar notificación como leída"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marcar todas las notificaciones como leídas"""
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"message": "Todas las notificaciones marcadas como leídas."})

class UserRoleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return UserRole.objects.all()
        return UserRole.objects.filter(user=self.request.user)

class ReputationScoreViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReputationScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ReputationScore.objects.all()
        return ReputationScore.objects.filter(user=self.request.user)

class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            # TODO: Implementar lógica real de reset de password
            # Por ahora solo simulamos el envío de email
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                # Simular envío de email
                return Response({
                    "message": "Si el email existe, se ha enviado un enlace de reset."
                })
            except User.DoesNotExist:
                # Por seguridad, no revelamos si el email existe
                return Response({
                    "message": "Si el email existe, se ha enviado un enlace de reset."
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            # TODO: Implementar verificación real del token
            # Por ahora simulamos el reset
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            # Simular verificación de token
            # En una implementación real, verificaríamos el token
            return Response({
                "message": "Contraseña restablecida exitosamente."
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    """Vista para obtener el perfil del usuario (legacy)"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Añade esto al final de users/views.py

class WalletConnectView(APIView):
    """Vista para conectar wallet de blockchain"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            wallet_address = request.data.get('wallet_address')
            
            if not wallet_address:
                return Response(
                    {'error': 'Wallet address is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar formato de dirección de wallet (básico)
            if not wallet_address.startswith('0x') or len(wallet_address) != 42:
                return Response(
                    {'error': 'Invalid wallet address format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Asociar wallet al usuario
            request.user.wallet_address = wallet_address
            request.user.save()
            
            return Response({
                'success': True,
                'message': 'Wallet connected successfully',
                'wallet_address': wallet_address,
                'user': request.user.username
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error connecting wallet: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )