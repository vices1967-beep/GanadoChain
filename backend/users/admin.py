from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, UserActivityLog, UserPreference, APIToken
from .reputation_models import UserRole, ReputationScore, RewardDistribution, StakingPool
from .notification_models import Notification
import json

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'role_display', 'wallet_short', 'is_verified_display',
        'blockchain_roles_count', 'profile_completion_display',
        'is_staff', 'date_joined'
    ]
    
    list_filter = [
        'role', 'is_verified', 'is_staff', 'is_superuser', 
        'is_blockchain_active', 'date_joined'
    ]
    
    search_fields = [
        'username', 'email', 'first_name', 'last_name', 
        'wallet_address', 'company', 'phone_number'
    ]
    
    readonly_fields = [
        'date_joined', 'last_login', 'wallet_short', 
        'profile_completion_display', 'blockchain_roles_list',
        'verification_date', 'last_blockchain_sync',
        'is_active_display', 'is_blockchain_active_display',
        'reputation_scores_link', 'user_roles_link',
        'notifications_link', 'rewards_link', 'staking_pool_link'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'username', 'password', 'email', 
                'first_name', 'last_name'
            )
        }),
        ('Información GanadoChain', {
            'fields': (
                'role', 'wallet_address', 'wallet_short',
                'blockchain_roles', 'blockchain_roles_list',
                'is_verified', 'verification_date',
                'is_blockchain_active', 'is_blockchain_active_display',
                'last_blockchain_sync'
            )
        }),
        ('Sistemas Integrados', {
            'fields': (
                'reputation_scores_link',
                'user_roles_link',
                'notifications_link',
                'rewards_link',
                'staking_pool_link'
            ),
            'classes': ('collapse',)
        }),
        ('Perfil Extendido', {
            'fields': (
                'profile_image', 'phone_number', 'company',
                'location', 'bio', 'website',
                'twitter_handle', 'discord_handle',
                'profile_completion_display'
            )
        }),
        ('Permisos and Estado', {
            'fields': (
                'is_active', 'is_active_display', 'is_staff',
                'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Fechas Importantes', {
            'fields': (
                'date_joined', 'last_login'
            ),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'role', 'wallet_address'
            ),
        }),
        ('Información Adicional', {
            'classes': ('collapse',),
            'fields': (
                'phone_number', 'company', 'location'
            ),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')
    
    def role_display(self, obj):
        role_colors = {
            'PRODUCER': 'green',
            'VET': 'blue',
            'FRIGORIFICO': 'orange',
            'AUDITOR': 'purple',
            'IOT': 'red',
            'ADMIN': 'darkred',
            'DAO': 'teal',
            'CONSUMER': 'gray',
            'VIEWER': 'lightgray'
        }
        color = role_colors.get(obj.role, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_role_display()
        )
    role_display.short_description = 'Rol'
    
    def wallet_short(self, obj):
        if obj.wallet_address:
            return f"{obj.wallet_address[:8]}...{obj.wallet_address[-6:]}"
        return "—"
    wallet_short.short_description = 'Wallet'
    
    def is_verified_display(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✅ Verificado</span>')
        return format_html('<span style="color: red;">❌ No Verificado</span>')
    is_verified_display.short_description = 'Verificado'
    
    def blockchain_roles_count(self, obj):
        count = len(obj.blockchain_roles)
        if count > 0:
            return format_html('<span style="color: green;">{} roles</span>', count)
        return format_html('<span style="color: gray;">Sin roles</span>')
    blockchain_roles_count.short_description = 'Roles Blockchain'
    
    def blockchain_roles_list(self, obj):
        if obj.blockchain_roles:
            roles_html = ''.join(f'<li>{role}</li>' for role in obj.blockchain_roles)
            return format_html('<ul>{}</ul>', roles_html)
        return "—"
    blockchain_roles_list.short_description = 'Roles Asignados'
    
    def profile_completion_display(self, obj):
        completion = obj.profile_completion
        if completion > 80:
            color = 'green'
        elif completion > 50:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<div style="background-color: #f0f0f0; border-radius: 10px; height: 20px; width: 100px; position: relative;">'
            '<div style="background-color: {}; border-radius: 10px; height: 100%; width: {}%;"></div>'
            '<span style="position: absolute; top: 0; left: 0; right: 0; text-align: center; font-size: 12px; color: black;">{}%</span>'
            '</div>',
            color, completion, int(completion)
        )
    profile_completion_display.short_description = 'Completitud Perfil'
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Activo</span>')
        return format_html('<span style="color: red;">❌ Inactivo</span>')
    is_active_display.short_description = 'Estado'
    
    def is_blockchain_active_display(self, obj):
        if obj.is_blockchain_active:
            return format_html('<span style="color: green;">✅ Activo</span>')
        return format_html('<span style="color: red;">❌ Inactivo</span>')
    is_blockchain_active_display.short_description = 'Blockchain'
    
    def reputation_scores_link(self, obj):
        url = reverse('admin:users_reputationscore_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">⭐ Ver Puntuaciones de Reputación</a>', url)
    reputation_scores_link.short_description = 'Reputación'
    
    def user_roles_link(self, obj):
        url = reverse('admin:users_userrole_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">👑 Ver Roles Detallados</a>', url)
    user_roles_link.short_description = 'Roles Detallados'
    
    def notifications_link(self, obj):
        url = reverse('admin:users_notification_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">🔔 Ver Notificaciones</a>', url)
    notifications_link.short_description = 'Notificaciones'
    
    def rewards_link(self, obj):
        url = reverse('admin:users_rewarddistribution_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">💰 Ver Recompensas</a>', url)
    rewards_link.short_description = 'Recompensas'
    
    def staking_pool_link(self, obj):
        url = reverse('admin:users_stakingpool_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">🏦 Ver Staking</a>', url)
    staking_pool_link.short_description = 'Staking'

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'action_display', 'severity_display',
        'ip_address', 'short_tx_hash', 'timestamp'
    ]
    
    list_filter = [
        'action', 'timestamp', 'user__role'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'ip_address',
        'blockchain_tx_hash', 'message'
    ]
    
    readonly_fields = [
        'timestamp', 'user_link', 'action_display',
        'severity_display', 'short_tx_hash', 'metadata_prettified'
    ]
    
    fieldsets = (
        ('Información del Evento', {
            'fields': (
                'user_link', 'action', 'action_display',
                'ip_address', 'user_agent'
            )
        }),
        ('Detalles', {
            'fields': (
                'message', 'metadata_prettified',
                'blockchain_tx_hash', 'short_tx_hash'
            )
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "—"
    user_link.short_description = 'Usuario'
    
    def action_display(self, obj):
        action_colors = {
            'LOGIN': 'green',
            'LOGOUT': 'blue',
            'NFT_MINT': 'purple',
            'TOKEN_MINT': 'orange',
            'HEALTH_UPDATE': 'red',
            'ROLE_ASSIGN': 'teal',
            'PROFILE_UPDATE': 'darkblue',
            'PASSWORD_CHANGE': 'darkred',
            'BLOCKCHAIN_INTERACTION': 'darkgreen'
        }
        color = action_colors.get(obj.action, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_action_display()
        )
    action_display.short_description = 'Acción'
    
    def severity_display(self, obj):
        if obj.action in ['LOGIN', 'LOGOUT', 'PROFILE_UPDATE']:
            return format_html('<span style="color: green;">🟢 Normal</span>')
        elif obj.action in ['NFT_MINT', 'TOKEN_MINT', 'ROLE_ASSIGN']:
            return format_html('<span style="color: orange;">🟡 Importante</span>')
        elif obj.action in ['HEALTH_UPDATE', 'PASSWORD_CHANGE']:
            return format_html('<span style="color: red;">🔴 Crítico</span>')
        else:
            return format_html('<span style="color: blue;">🔵 Info</span>')
    severity_display.short_description = 'Severidad'
    
    def short_tx_hash(self, obj):
        if obj.blockchain_tx_hash:
            return f"{obj.blockchain_tx_hash[:8]}...{obj.blockchain_tx_hash[-6:]}"
        return "—"
    short_tx_hash.short_description = 'Tx Hash'
    
    def metadata_prettified(self, obj):
        return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>', 
                          json.dumps(obj.metadata, indent=2, ensure_ascii=False))
    metadata_prettified.short_description = 'Metadatos (Formateados)'

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'email_notifications_display',
        'push_notifications_display', 'language_display',
        'theme_display'
    ]
    
    list_filter = [
        'email_notifications', 'push_notifications',
        'language', 'theme'
    ]
    
    search_fields = [
        'user__username', 'user__email'
    ]
    
    readonly_fields = [
        'user_link', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user_link',)
        }),
        ('Preferencias de Notificación', {
            'fields': (
                'email_notifications', 'push_notifications'
            )
        }),
        ('Preferencias de Interfaz', {
            'fields': (
                'language', 'theme', 'animals_per_page',
                'enable_animations'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "—"
    user_link.short_description = 'Usuario'
    
    def email_notifications_display(self, obj):
        if obj.email_notifications:
            return format_html('<span style="color: green;">✅ Activadas</span>')
        return format_html('<span style="color: red;">❌ Desactivadas</span>')
    email_notifications_display.short_description = 'Email Notif.'
    
    def push_notifications_display(self, obj):
        if obj.push_notifications:
            return format_html('<span style="color: green;">✅ Activadas</span>')
        return format_html('<span style="color: red;">❌ Desactivadas</span>')
    push_notifications_display.short_description = 'Push Notif.'
    
    def language_display(self, obj):
        language_names = {'es': 'Español', 'en': 'English'}
        return language_names.get(obj.language, obj.language)
    language_display.short_description = 'Idioma'
    
    def theme_display(self, obj):
        theme_names = {'light': 'Claro', 'dark': 'Oscuro', 'auto': 'Automático'}
        return theme_names.get(obj.theme, obj.theme)
    theme_display.short_description = 'Tema'

@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user_link', 'token_type_display',
        'is_active_display', 'is_expired_display',
        'created_at'
    ]
    
    list_filter = [
        'token_type', 'is_active', 'created_at'
    ]
    
    search_fields = [
        'name', 'user__username', 'user__email', 'token'
    ]
    
    readonly_fields = [
        'token', 'created_at', 'user_link', 'token_type_display',
        'is_expired_display', 'last_used_formatted'
    ]
    
    fieldsets = (
        ('Información del Token', {
            'fields': (
                'user_link', 'name', 'token', 'token_type',
                'token_type_display'
            )
        }),
        ('Estado', {
            'fields': (
                'is_active', 'is_active_display', 'expires_at',
                'is_expired_display'
            )
        }),
        ('Uso', {
            'fields': ('last_used', 'last_used_formatted'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "—"
    user_link.short_description = 'Usuario'
    
    def token_type_display(self, obj):
        type_colors = {
            'READ': 'blue',
            'WRITE': 'green',
            'ADMIN': 'red',
            'IOT': 'orange'
        }
        color = type_colors.get(obj.token_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_token_type_display()
        )
    token_type_display.short_description = 'Tipo'
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Activo</span>')
        return format_html('<span style="color: red;">❌ Inactivo</span>')
    is_active_display.short_description = 'Estado'
    
    def is_expired_display(self, obj):
        from django.utils import timezone
        if obj.expires_at and obj.expires_at < timezone.now():
            return format_html('<span style="color: red;">❌ Expirado</span>')
        return format_html('<span style="color: green;">✅ Vigente</span>')
    is_expired_display.short_description = 'Expirado'
    
    def last_used_formatted(self, obj):
        if obj.last_used:
            return obj.last_used.strftime("%Y-%m-%d %H:%M:%S")
        return "Nunca"
    last_used_formatted.short_description = 'Último Uso'

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'role_type_display', 'scope_type_display',
        'scope_id_display', 'is_active_display', 'granted_by_link',
        'granted_at', 'expires_at_display'
    ]
    
    list_filter = [
        'role_type', 'scope_type', 'is_active', 'granted_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'scope_id',
        'granted_by__username', 'role_type'
    ]
    
    readonly_fields = [
        'granted_at', 'user_link', 'granted_by_link',
        'scope_id_display', 'expires_at_display'
    ]
    
    fieldsets = (
        ('Información del Rol', {
            'fields': (
                'user_link', 'role_type', 'scope_type',
                'scope_id', 'scope_id_display'
            )
        }),
        ('Gestión del Rol', {
            'fields': (
                'is_active', 'granted_by_link', 'granted_at',
                'expires_at', 'expires_at_display'
            )
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "—"
    user_link.short_description = 'Usuario'
    
    def role_type_display(self, obj):
        role_colors = {
            'PRODUCER_ROLE': 'green',
            'VET_ROLE': 'blue',
            'FRIGORIFICO_ROLE': 'orange',
            'AUDITOR_ROLE': 'purple',
            'IOT_ROLE': 'red',
            'DAO_ROLE': 'teal',
            'DEFAULT_ADMIN_ROLE': 'darkred'
        }
        color = role_colors.get(obj.role_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, dict(User.BLOCKCHAIN_ROLE_CHOICES).get(obj.role_type, obj.role_type)
        )
    role_type_display.short_description = 'Rol'
    
    def scope_type_display(self, obj):
        scope_names = {
            'GLOBAL': 'Global',
            'BATCH': 'Por Lote',
            'ANIMAL': 'Por Animal',
            'LOCATION': 'Por Ubicación'
        }
        return scope_names.get(obj.scope_type, obj.scope_type)
    scope_type_display.short_description = 'Alcance'
    
    def scope_id_display(self, obj):
        if obj.scope_id:
            # Crear enlace según el tipo de scope
            if obj.scope_type == 'BATCH' and obj.scope_id.isdigit():
                url = reverse('admin:cattle_batch_change', args=[obj.scope_id])
                return format_html('<a href="{}">Lote #{}</a>', url, obj.scope_id)
            elif obj.scope_type == 'ANIMAL' and obj.scope_id.isdigit():
                url = reverse('admin:cattle_animal_change', args=[obj.scope_id])
                return format_html('<a href="{}">Animal #{}</a>', url, obj.scope_id)
            return obj.scope_id
        return "Global"
    scope_id_display.short_description = 'ID del Alcance'
    
    def granted_by_link(self, obj):
        if obj.granted_by:
            url = reverse('admin:users_user_change', args=[obj.granted_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.granted_by.username)
        return "—"
    granted_by_link.short_description = 'Otorgado por'
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Activo</span>')
        return format_html('<span style="color: red;">❌ Inactivo</span>')
    is_active_display.short_description = 'Estado'
    
    def expires_at_display(self, obj):
        from django.utils import timezone
        if obj.expires_at:
            if obj.expires_at < timezone.now():
                return format_html('<span style="color: red;">❌ Expirado</span>')
            return obj.expires_at.strftime("%Y-%m-%d %H:%M")
        return "—"
    expires_at_display.short_description = 'Expira'

@admin.register(ReputationScore)
class ReputationScoreAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'reputation_type_display', 'score_display',
        'total_actions', 'positive_actions', 'last_calculated'
    ]
    
    list_filter = [
        'reputation_type', 'last_calculated'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'reputation_type'
    ]
    
    readonly_fields = [
        'last_calculated', 'user_link', 'score_display',
        'metrics_prettified'
    ]
    
    fieldsets = (
        ('Información de Reputación', {
            'fields': (
                'user_link', 'reputation_type'
            )
        }),
        ('Puntuación', {
            'fields': (
                'score', 'score_display', 'total_actions',
                'positive_actions'
            )
        }),
        ('Métricas Detalladas', {
            'fields': ('metrics_prettified',),
            'classes': ('collapse',)
        }),
        ('Actualización', {
            'fields': ('last_calculated',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "—"
    user_link.short_description = 'Usuario'
    
    def reputation_type_display(self, obj):
        type_colors = {
            'PRODUCER': 'green',
            'VET': 'blue',
            'FRIGORIFICO': 'orange',
            'AUDITOR': 'purple'
        }
        color = type_colors.get(obj.reputation_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_reputation_type_display()
        )
    reputation_type_display.short_description = 'Tipo de Reputación'
    
    def score_display(self, obj):
        if obj.score:
            if obj.score >= 4.0:
                color = 'green'
            elif obj.score >= 3.0:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}/5.0</span>',
                color, obj.score
            )
        return "—"
    score_display.short_description = 'Puntuación'
    
    def metrics_prettified(self, obj):
        return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>', 
                          json.dumps(obj.metrics, indent=2, ensure_ascii=False))
    metrics_prettified.short_description = 'Métricas (Formateadas)'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'notification_type_display', 'title_short',
        'priority_display', 'is_read_display', 'created_at'
    ]
    
    list_filter = [
        'notification_type', 'priority', 'is_read', 'created_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'title', 'message',
        'related_object_id'
    ]
    
    readonly_fields = [
        'created_at', 'user_link', 'notification_type_display',
        'priority_display', 'related_object_link'
    ]
    
    fieldsets = (
        ('Información de Notificación', {
            'fields': (
                'user_link', 'notification_type', 'priority',
                'priority_display', 'title', 'message'
            )
        }),
        ('Objeto Relacionado', {
            'fields': (
                'related_object_id', 'related_content_type',
                'related_object_link'
            ),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_read', 'is_read_display')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "—"
    user_link.short_description = 'Usuario'
    
    def notification_type_display(self, obj):
        type_colors = {
            'HEALTH_ALERT': 'red',
            'BLOCKCHAIN_TX': 'blue',
            'IOT_ALERT': 'orange',
            'BATCH_UPDATE': 'green',
            'ROLE_CHANGE': 'purple',
            'REPUTATION_UPDATE': 'teal'
        }
        color = type_colors.get(obj.notification_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_notification_type_display()
        )
    notification_type_display.short_description = 'Tipo'
    
    def title_short(self, obj):
        if len(obj.title) > 30:
            return obj.title[:27] + '...'
        return obj.title
    title_short.short_description = 'Título'
    
    def priority_display(self, obj):
        priority_colors = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'URGENT': 'darkred'
        }
        color = priority_colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_display.short_description = 'Prioridad'
    
    def is_read_display(self, obj):
        if obj.is_read:
            return format_html('<span style="color: green;">✅ Leída</span>')
        return format_html('<span style="color: red;">❌ No Leída</span>')
    is_read_display.short_description = 'Leída'
    
    def related_object_link(self, obj):
        if obj.related_object_id and obj.related_content_type:
            # Crear enlace según el tipo de contenido
            if obj.related_content_type == 'animal':
                url = reverse('admin:cattle_animal_change', args=[obj.related_object_id])
                return format_html('<a href="{}">Animal #{}</a>', url, obj.related_object_id)
            elif obj.related_content_type == 'batch':
                url = reverse('admin:cattle_batch_change', args=[obj.related_object_id])
                return format_html('<a href="{}">Lote #{}</a>', url, obj.related_object_id)
            elif obj.related_content_type == 'health_record':
                url = reverse('admin:cattle_animalhealthrecord_change', args=[obj.related_object_id])
                return format_html('<a href="{}">Registro Salud #{}</a>', url, obj.related_object_id)
        return "—"
    related_object_link.short_description = 'Objeto Relacionado'

@admin.register(RewardDistribution)
class RewardDistributionAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'action_type_display', 'action_id_display',
        'tokens_awarded_display', 'distribution_date', 
        'is_claimed_display', 'polyscan_link'
    ]
    
    list_filter = [
        'action_type', 'is_claimed', 'distribution_date'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'action_type',
        'transaction_hash', 'action_id'
    ]
    
    readonly_fields = [
        'distribution_date', 'user_link', 'action_type_display',
        'action_id_display', 'is_claimed_display', 'polyscan_link'
    ]
    
    fieldsets = (
        ('Información de Recompensa', {
            'fields': (
                'user_link', 'action_type', 'action_type_display',
                'action_id', 'action_id_display'
            )
        }),
        ('Detalles de la Recompensa', {
            'fields': (
                'tokens_awarded', 'tokens_awarded_display',
                'transaction_hash', 'polyscan_link'
            )
        }),
        ('Estado', {
            'fields': ('is_claimed', 'is_claimed_display')
        }),
        ('Timestamps', {
            'fields': ('distribution_date',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "—"
    user_link.short_description = 'Usuario'
    
    def action_type_display(self, obj):
        action_types = {
            'ANIMAL_REGISTRATION': 'Registro de Animal',
            'HEALTH_UPDATE': 'Actualización de Salud',
            'LOCATION_UPDATE': 'Actualización de Ubicación',
            'BATCH_CREATION': 'Creación de Lote',
            'CERTIFICATION': 'Certificación',
            'DATA_QUALITY': 'Calidad de Datos',
            'COMMUNITY_CONTRIBUTION': 'Contribución Comunitaria',
            'IOT_DATA_SUBMISSION': 'Envío de Datos IoT'
        }
        display_name = action_types.get(obj.action_type, obj.action_type)
        
        action_colors = {
            'ANIMAL_REGISTRATION': 'green',
            'HEALTH_UPDATE': 'red',
            'LOCATION_UPDATE': 'blue',
            'BATCH_CREATION': 'purple',
            'CERTIFICATION': 'orange',
            'DATA_QUALITY': 'teal',
            'COMMUNITY_CONTRIBUTION': 'pink',
            'IOT_DATA_SUBMISSION': 'brown'
        }
        color = action_colors.get(obj.action_type, 'gray')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, display_name
        )
    action_type_display.short_description = 'Tipo de Acción'
    
    def action_id_display(self, obj):
        if obj.action_id:
            # Crear enlace según el tipo de acción
            if obj.action_type == 'ANIMAL_REGISTRATION':
                url = reverse('admin:cattle_animal_change', args=[obj.action_id])
                return format_html('<a href="{}">Animal #{}</a>', url, obj.action_id)
            elif obj.action_type == 'BATCH_CREATION':
                url = reverse('admin:cattle_batch_change', args=[obj.action_id])
                return format_html('<a href="{}">Lote #{}</a>', url, obj.action_id)
            elif obj.action_type == 'HEALTH_UPDATE':
                url = reverse('admin:cattle_animalhealthrecord_change', args=[obj.action_id])
                return format_html('<a href="{}">Registro Salud #{}</a>', url, obj.action_id)
            elif obj.action_type == 'CERTIFICATION':
                url = reverse('admin:cattle_animalcertification_change', args=[obj.action_id])
                return format_html('<a href="{}">Certificación #{}</a>', url, obj.action_id)
            return str(obj.action_id)
        return "—"
    action_id_display.short_description = 'ID de Acción'
    
    def tokens_awarded_display(self, obj):
        return f"{obj.tokens_awarded} GAN"
    tokens_awarded_display.short_description = 'Tokens'
    
    def is_claimed_display(self, obj):
        if obj.is_claimed:
            return format_html('<span style="color: green;">✅ Reclamado</span>')
        return format_html('<span style="color: orange;">⏳ Pendiente</span>')
    is_claimed_display.short_description = 'Estado'
    
    def polyscan_link(self, obj):
        if obj.transaction_hash:
            return format_html(
                '<a href="https://polygonscan.com/tx/{}" target="_blank" style="background-color: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 PolyScan</a>',
                obj.transaction_hash
            )
        return "—"
    polyscan_link.short_description = 'Blockchain'

@admin.register(StakingPool)
class StakingPoolAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'tokens_staked_display', 'staking_status',
        'apy_display', 'rewards_earned_display', 'staking_start',
        'staking_end_display'
    ]
    
    list_filter = [
        'staking_start', 'staking_duration', 'apy'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'blockchain_staking_id'
    ]
    
    readonly_fields = [
        'staking_start', 'user_link', 'staking_status',
        'staking_end_display', 'rewards_earned_display',
        'estimated_total_rewards', 'polyscan_link'
    ]
    
    fieldsets = (
        ('Información del Staking', {
            'fields': (
                'user_link', 'tokens_staked', 'staking_duration',
                'apy', 'apy_display'
            )
        }),
        ('Estado del Staking', {
            'fields': (
                'staking_status', 'staking_start', 'staking_end_display',
                'rewards_earned', 'rewards_earned_display',
                'estimated_total_rewards'
            )
        }),
        ('Blockchain', {
            'fields': ('blockchain_staking_id', 'polyscan_link'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "—"
    user_link.short_description = 'Usuario'
    
    def tokens_staked_display(self, obj):
        return f"{obj.tokens_staked} GAN"
    tokens_staked_display.short_description = 'Tokens Staked'
    
    def staking_status(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = obj.staking_start + timedelta(days=obj.staking_duration)
        if timezone.now() < obj.staking_start:
            return format_html('<span style="color: orange;">⏳ Pendiente</span>')
        elif timezone.now() <= end_date:
            days_left = (end_date - timezone.now()).days
            return format_html('<span style="color: green;">✅ Activo ({} días)</span>', days_left)
        else:
            return format_html('<span style="color: blue;">✅ Completado</span>')
    staking_status.short_description = 'Estado'
    
    def apy_display(self, obj):
        return f"{obj.apy}%"
    apy_display.short_description = 'APY'
    
    def rewards_earned_display(self, obj):
        return f"{obj.rewards_earned} GAN"
    rewards_earned_display.short_description = 'Recompensas'
    
    def staking_end_display(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = obj.staking_start + timedelta(days=obj.staking_duration)
        return end_date.strftime("%Y-%m-%d %H:%M")
    staking_end_display.short_description = 'Fecha de Fin'
    
    def estimated_total_rewards(self, obj):
        if obj.tokens_staked and obj.apy:
            # Cálculo de recompensas totales estimadas
            annual_rewards = obj.tokens_staked * obj.apy / 100
            duration_years = obj.staking_duration / 365
            estimated = annual_rewards * duration_years
            return f"{estimated:.2f} GAN"
        return "—"
    estimated_total_rewards.short_description = 'Recompensas Totales Estimadas'
    
    def polyscan_link(self, obj):
        if obj.blockchain_staking_id:
            return format_html(
                '<a href="https://polygonscan.com/address/{}" target="_blank" style="background-color: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 Ver Staking</a>',
                obj.blockchain_staking_id
            )
        return "—"
    polyscan_link.short_description = 'Blockchain'

# Configuración adicional para el admin de Users
admin.site.site_header = "🐄 GanadoChain - User Administration"
admin.site.site_title = "GanadoChain User Admin"
admin.site.index_title = "Administración de Usuarios"

# Personalizar el orden de las apps
def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    
    # Reordenar las apps
    app_ordering = {
        'cattle': 1,      # Primero: Módulo de Animales
        'users': 2,       # Segundo: Usuarios
        'blockchain': 3,  # Tercero: Blockchain
        'iot': 4,         # Cuarto: IoT
        'auth': 5,        # Autenticación
        'authtoken': 6,   # Tokens
    }
    
    app_list = sorted(
        app_dict.values(), 
        key=lambda x: app_ordering.get(x['app_label'], 10)
    )
    
    return app_list

# Aplicar la personalización
admin.AdminSite.get_app_list = get_app_list