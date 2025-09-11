from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserActivityLog, UserPreference, APIToken
from .reputation_models import UserRole, ReputationScore
from .notification_models import Notification
from .notification_models import Notification  # Importación correcta
import re
from decimal import Decimal

User = get_user_model()

# users/serializers.py - Modificar EthereumAddressField
class EthereumAddressField(serializers.CharField):
    """Campo personalizado para validar direcciones Ethereum"""
    
    def __init__(self, **kwargs):
        kwargs['max_length'] = 42
        super().__init__(**kwargs)
    
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        
        if data:
            # Normalizar a minúsculas y asegurar prefijo 0x
            if not data.startswith('0x'):
                data = '0x' + data
            data = data.lower()
            
            # Validar formato Ethereum (0x + 40 caracteres hex)
            if not re.match(r'^0x[0-9a-f]{40}$', data):
                raise serializers.ValidationError('Dirección Ethereum inválida')
        
        return data
    
    # Eliminar el método validate ya que la validación se hace en to_internal_value

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    wallet_address = EthereumAddressField(required=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'password2', 
            'first_name', 'last_name', 'wallet_address', 'role',
            'phone_number', 'company', 'location'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'wallet_address': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        
        # Validar que el wallet address sea único
        wallet_address = attrs['wallet_address']
        if User.objects.filter(wallet_address__iexact=wallet_address).exists():
            raise serializers.ValidationError({"wallet_address": "Esta dirección wallet ya está registrada."})
        
        # Validar que el email sea único
        email = attrs.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"email": "Este correo electrónico ya está registrado."})
        
        # Validar que el username sea único
        username = attrs.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({"username": "Este nombre de usuario ya está en uso."})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Crear preferencias por defecto
        UserPreference.objects.create(user=user)
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    profile_completion = serializers.IntegerField(read_only=True)
    wallet_short = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    has_blockchain_roles = serializers.BooleanField(read_only=True)
    primary_blockchain_role = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'wallet_address', 'wallet_short', 'role', 'role_display',
            'is_verified', 'is_blockchain_active', 'verification_date',
            'profile_image', 'phone_number', 'company', 'location',
            'bio', 'website', 'twitter_handle', 'discord_handle',
            'blockchain_roles', 'has_blockchain_roles', 'primary_blockchain_role',
            'last_blockchain_sync', 'profile_completion',
            'date_joined', 'last_login'
        )
        read_only_fields = (
            'id', 'email', 'date_joined', 'last_login', 'is_verified',
            'verification_date', 'last_blockchain_sync', 'profile_completion',
            'wallet_short', 'role_display', 'has_blockchain_roles', 
            'primary_blockchain_role'
        )

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'profile_image',
            'phone_number', 'company', 'location', 'bio',
            'website', 'twitter_handle', 'discord_handle'
        )

class UserListSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    wallet_short = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'wallet_address', 'wallet_short', 'role', 'role_display',
            'is_verified', 'company', 'date_joined'
        )

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})
        return attrs

class WalletConnectSerializer(serializers.Serializer):
    wallet_address = EthereumAddressField(required=True)
    signature = serializers.CharField(required=True)
    message = serializers.CharField(required=True)

    def validate(self, attrs):
        # Aquí se implementaría la verificación de la firma
        wallet_address = attrs['wallet_address']
        signature = attrs['signature']
        message = attrs['message']
        
        # TODO: Implementar verificación de firma con web3
        # Por ahora solo validamos el formato
        if not signature.startswith('0x') or len(signature) != 132:
            raise serializers.ValidationError({"signature": "Formato de firma inválido."})
        
        return attrs

class BlockchainRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.BLOCKCHAIN_ROLE_CHOICES)
    action = serializers.ChoiceField(choices=[('add', 'add'), ('remove', 'remove')])

class UserActivityLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    short_tx_hash = serializers.CharField(read_only=True)
    
    class Meta:
        model = UserActivityLog
        fields = (
            'id', 'user', 'user_username', 'action', 'action_display',
            'ip_address', 'user_agent', 'metadata', 'timestamp',
            'blockchain_tx_hash', 'short_tx_hash'
        )
        read_only_fields = ('id', 'timestamp', 'short_tx_hash')

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = (
            'email_notifications', 'push_notifications', 'language',
            'theme', 'animals_per_page', 'enable_animations'
        )

class APITokenSerializer(serializers.ModelSerializer):
    token_type_display = serializers.CharField(source='get_token_type_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = APIToken
        fields = (
            'id', 'user', 'user_username', 'name', 'token', 'token_type',
            'token_type_display', 'is_active', 'expires_at', 'last_used',
            'is_expired', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'is_expired', 'user_username')
        extra_kwargs = {
            'token': {'write_only': True}
        }

class APITokenCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIToken
        fields = ('name', 'token_type', 'expires_at')
        read_only_fields = ('token',)

class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField(min_value=0)
    active_users = serializers.IntegerField(min_value=0)
    verified_users = serializers.IntegerField(min_value=0)
    users_by_role = serializers.DictField()
    new_users_today = serializers.IntegerField(min_value=0)
    new_users_this_week = serializers.IntegerField(min_value=0)
    users_with_blockchain_roles = serializers.IntegerField(min_value=0)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})
        return attrs

class UserSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, max_length=100)
    search_in = serializers.MultipleChoiceField(
        choices=[
            ('username', 'Username'),
            ('email', 'Email'),
            ('wallet', 'Wallet Address'),
            ('name', 'Nombre'),
            ('company', 'Empresa')
        ],
        required=False,
        default=['username', 'email', 'wallet', 'name']
    )

class UserRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    wallet_address = EthereumAddressField(required=True)

class VerifyWalletSerializer(serializers.Serializer):
    wallet_address = EthereumAddressField(required=True)
    signed_message = serializers.CharField(required=True)
    original_message = serializers.CharField(required=True)

class UserExportSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    blockchain_roles_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'wallet_address', 'role', 'role_display', 'is_verified',
            'company', 'location', 'date_joined', 'last_login',
            'blockchain_roles_count'
        )

# Nuevos serializers para los modelos adicionales

class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = (
            'id', 'user', 'user_username', 'notification_type', 'notification_type_display',
            'title', 'message', 'related_object_id', 'related_content_type',
            'is_read', 'priority', 'priority_display', 'created_at'
        )
        read_only_fields = ('created_at',)

class UserRoleSerializer(serializers.ModelSerializer):
    role_type_display = serializers.CharField(source='get_role_type_display', read_only=True)
    scope_type_display = serializers.CharField(source='get_scope_type_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    granted_by_username = serializers.CharField(source='granted_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = UserRole
        fields = (
            'id', 'user', 'user_username', 'role_type', 'role_type_display',
            'scope_type', 'scope_type_display', 'scope_id', 'granted_by',
            'granted_by_username', 'granted_at', 'expires_at', 'is_active'
        )
        read_only_fields = ('granted_at',)

class ReputationScoreSerializer(serializers.ModelSerializer):
    reputation_type_display = serializers.CharField(source='get_reputation_type_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ReputationScore
        fields = (
            'id', 'user', 'user_username', 'reputation_type', 'reputation_type_display',
            'score', 'total_actions', 'positive_actions', 'last_calculated', 'metrics'
        )
        read_only_fields = ('last_calculated',)

class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para usuario con información extendida"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    wallet_short = serializers.CharField(read_only=True)
    profile_completion = serializers.IntegerField(read_only=True)
    preferences = serializers.SerializerMethodField(read_only=True)
    activity_logs = serializers.SerializerMethodField(read_only=True)
    notifications = serializers.SerializerMethodField(read_only=True)
    detailed_roles = serializers.SerializerMethodField(read_only=True)
    reputation_scores = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'wallet_address', 'wallet_short', 'role', 'role_display',
            'is_verified', 'is_blockchain_active', 'profile_image',
            'phone_number', 'company', 'location', 'bio', 'website',
            'twitter_handle', 'discord_handle', 'blockchain_roles',
            'profile_completion', 'date_joined', 'last_login',
            'preferences', 'activity_logs', 'notifications',
            'detailed_roles', 'reputation_scores'
        )
        read_only_fields = ('date_joined', 'last_login', 'profile_completion')
    
    def get_preferences(self, obj):
        try:
            return UserPreferenceSerializer(obj.preferences).data
        except UserPreference.DoesNotExist:
            return None
    
    def get_activity_logs(self, obj):
        logs = obj.activity_logs.all()[:10]  # Solo últimos 10
        return UserActivityLogSerializer(logs, many=True).data
    
    def get_notifications(self, obj):
        notifications = obj.notification_set.all()[:10]  # Solo últimos 10
        return NotificationSerializer(notifications, many=True).data
    
    def get_detailed_roles(self, obj):
        roles = obj.detailed_roles.filter(is_active=True)
        return UserRoleSerializer(roles, many=True).data
    
    def get_reputation_scores(self, obj):
        scores = obj.reputationscore_set.all()
        return ReputationScoreSerializer(scores, many=True).data

class UserBulkUpdateSerializer(serializers.Serializer):
    """Serializer para actualización masiva de usuarios"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1
    )
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    is_active = serializers.BooleanField(required=False)
    is_blockchain_active = serializers.BooleanField(required=False)

class UserImportSerializer(serializers.Serializer):
    """Serializer para importación de usuarios"""
    file = serializers.FileField()
    overwrite_existing = serializers.BooleanField(default=False)

class UserRoleBulkAssignSerializer(serializers.Serializer):
    """Serializer para asignación masiva de roles"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1
    )
    role = serializers.ChoiceField(choices=User.BLOCKCHAIN_ROLE_CHOICES)
    action = serializers.ChoiceField(choices=[('add', 'add'), ('remove', 'remove')])

class ReputationUpdateSerializer(serializers.Serializer):
    """Serializer para actualización de reputación"""
    user_id = serializers.IntegerField(min_value=1)
    reputation_type = serializers.ChoiceField(choices=ReputationScore.REPUTATION_TYPES)
    score_delta = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2,
        min_value=Decimal('-100.00'),
        max_value=Decimal('100.00')
    )
    reason = serializers.CharField(max_length=500)

class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de notificaciones"""
    
    class Meta:
        model = Notification
        fields = (
            'user', 'notification_type', 'title', 'message',
            'related_object_id', 'related_content_type', 'priority'
        )

class NotificationBulkCreateSerializer(serializers.Serializer):
    """Serializer para creación masiva de notificaciones"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1
    )
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPES)
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    priority = serializers.ChoiceField(choices=Notification._meta.get_field('priority').choices, default='MEDIUM')