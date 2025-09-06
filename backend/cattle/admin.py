from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from .models import Animal, AnimalHealthRecord, Batch
from .blockchain_models import BlockchainEventState
from .audit_models import CattleAuditTrail
from iot.models import IoTDevice
from django.contrib.auth import get_user_model
from django.db.models import Count, Q  # ✅ IMPORTAR AQUÍ

User = get_user_model()

class AnimalHealthRecordInline(admin.TabularInline):
    model = AnimalHealthRecord
    extra = 0
    readonly_fields = ['created_at', 'blockchain_linked_display', 'polyscan_link']
    fields = ['health_status', 'source', 'temperature', 'heart_rate', 'movement_activity', 'created_at', 'blockchain_linked_display', 'polyscan_link']
    can_delete = False
    max_num = 5
    
    def blockchain_linked_display(self, obj):
        if obj.blockchain_hash:
            return format_html('<span style="color: green;">✅ Sí</span>')
        return format_html('<span style="color: red;">❌ No</span>')
    blockchain_linked_display.short_description = 'En Blockchain'
    
    def has_add_permission(self, request, obj=None):
        return True

class IoTDeviceInline(admin.TabularInline):
    model = IoTDevice
    extra = 0
    readonly_fields = ['last_reading', 'battery_level_display', 'is_active_display']
    fields = ['device_id', 'device_type', 'status', 'battery_level', 'last_reading', 'is_active_display']
    can_delete = True
    max_num = 3
    
    def battery_level_display(self, obj):
        if obj.battery_level is not None:
            color = 'green' if obj.battery_level > 50 else 'orange' if obj.battery_level > 20 else 'red'
            return format_html('<span style="color: {};">{}%</span>', color, obj.battery_level)
        return "N/A"
    battery_level_display.short_description = 'Batería'
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Activo</span>')
        return format_html('<span style="color: red;">❌ Inactivo</span>')
    is_active_display.short_description = 'Estado'

class CattleAuditTrailInline(admin.TabularInline):
    model = CattleAuditTrail
    extra = 0
    readonly_fields = ['object_type', 'action_type', 'user', 'timestamp', 'changes_display']
    fields = ['object_type', 'action_type', 'user', 'timestamp', 'changes_display']
    can_delete = False
    max_num = 10
    
    def changes_display(self, obj):
        if obj.changes:
            return format_html('<pre>{}</pre>', str(obj.changes))
        return "Sin cambios"
    changes_display.short_description = 'Cambios'
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = [
        'ear_tag', 
        'breed', 
        'owner', 
        'health_status_display',
        'current_batch_link',
        'token_id',
        'is_minted_display',
        'mint_transaction_short',
        'created_at'
    ]
    
    list_filter = [
        'health_status',
        'breed',
        'owner',
        'current_batch',
        'created_at'
    ]
    
    search_fields = [
        'ear_tag',
        'breed',
        'owner__username',
        'owner__email',
        'token_id',
        'mint_transaction_hash',
        'ipfs_hash',
        'nft_owner_wallet',
        'current_batch__name'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'is_minted_display',
        'metadata_uri_display',
        'mint_transaction_link',
        'polyscan_link',
        'age_display',
        'audit_trail_link'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'ear_tag', 
                'breed', 
                'birth_date', 
                'age_display',
                'weight',
                'health_status',
                'location',
                'owner',
                'current_batch'
            )
        }),
        ('Información Blockchain', {
            'fields': (
                'ipfs_hash',
                'token_id',
                'nft_owner_wallet',
                'mint_transaction_hash',
                'is_minted_display',
                'metadata_uri_display',
                'mint_transaction_link',
                'polyscan_link'
            )
        }),
        ('Auditoría', {
            'fields': (
                'audit_trail_link',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AnimalHealthRecordInline, IoTDeviceInline]
    
    def health_status_display(self, obj):
        status_colors = {
            'HEALTHY': 'green',
            'SICK': 'red',
            'RECOVERING': 'orange',
            'UNDER_OBSERVATION': 'blue',
            'QUARANTINED': 'purple'
        }
        color = status_colors.get(obj.health_status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_health_status_display())
    health_status_display.short_description = 'Estado Salud'
    
    def current_batch_link(self, obj):
        if obj.current_batch:
            url = reverse('admin:cattle_batch_change', args=[obj.current_batch.id])
            return format_html('<a href="{}">{}</a>', url, obj.current_batch.name)
        return "—"
    current_batch_link.short_description = 'Lote Actual'
    
    def is_minted_display(self, obj):
        if obj.is_minted:
            return format_html('<span style="color: green;">✅ Sí (Token #{})</span>', obj.token_id)
        return format_html('<span style="color: red;">❌ No</span>')
    is_minted_display.short_description = 'NFT Minted'
    
    def metadata_uri_display(self, obj):
        if obj.metadata_uri:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.metadata_uri, obj.metadata_uri)
        return "No disponible"
    metadata_uri_display.short_description = 'Metadata URI'
    
    def mint_transaction_short(self, obj):
        if obj.mint_transaction_hash:
            short_hash = obj.mint_transaction_hash[:10] + '...' + obj.mint_transaction_hash[-8:]
            return format_html('<code>{}</code>', short_hash)
        return "—"
    mint_transaction_short.short_description = 'Tx Hash'
    
    def mint_transaction_link(self, obj):
        if obj.polyscan_url:
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', obj.polyscan_url)
        return "—"
    mint_transaction_link.short_description = 'Enlace Transacción'
    
    def polyscan_link(self, obj):
        return self.mint_transaction_link(obj)
    polyscan_link.short_description = 'Explorador'
    
    def age_display(self, obj):
        from datetime import date
        if obj.birth_date:
            today = date.today()
            age = today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
            return f"{age} años"
        return "N/A"
    age_display.short_description = 'Edad'
    
    def audit_trail_link(self, obj):
        url = reverse('admin:cattle_cattleaudittrail_changelist') + f'?object_id={obj.id}&object_type=animal'
        return format_html('<a href="{}">📋 Ver Registros de Auditoría</a>', url)
    audit_trail_link.short_description = 'Auditoría'

@admin.register(AnimalHealthRecord)
class AnimalHealthRecordAdmin(admin.ModelAdmin):
    list_display = [
        'animal_link',
        'health_status_display',
        'source_display',
        'temperature_display',
        'heart_rate_display',
        'movement_display',
        'blockchain_linked_display',
        'created_at'
    ]
    
    list_filter = [
        'health_status',
        'source',
        'created_at',
        'iot_device_id'
    ]
    
    search_fields = [
        'animal__ear_tag',
        'animal__breed',
        'veterinarian__username',
        'veterinarian__email',
        'iot_device_id',
        'transaction_hash',
        'blockchain_hash'
    ]
    
    readonly_fields = [
        'created_at',
        'blockchain_linked_display',
        'polyscan_link',
        'animal_link',
        'audit_trail_link'
    ]
    
    fieldsets = (
        ('Información del Registro', {
            'fields': (
                'animal_link',
                'health_status',
                'source',
                'veterinarian',
                'iot_device_id',
                'notes'
            )
        }),
        ('Datos de Salud', {
            'fields': (
                'temperature',
                'heart_rate',
                'movement_activity',
            )
        }),
        ('Blockchain', {
            'fields': (
                'ipfs_hash',
                'transaction_hash',
                'blockchain_hash',
                'blockchain_linked_display',
                'polyscan_link'
            )
        }),
        ('Auditoría', {
            'fields': (
                'audit_trail_link',
                'created_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def animal_link(self, obj):
        if obj.animal:
            url = reverse('admin:cattle_animal_change', args=[obj.animal.id])
            return format_html('<a href="{}">{}</a>', url, obj.animal.ear_tag)
        return "-"
    animal_link.short_description = 'Animal'
    
    def health_status_display(self, obj):
        status_colors = {
            'HEALTHY': 'green',
            'SICK': 'red',
            'RECOVERING': 'orange',
            'UNDER_OBSERVATION': 'blue',
            'QUARANTINED': 'purple'
        }
        color = status_colors.get(obj.health_status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_health_status_display())
    health_status_display.short_description = 'Estado Salud'
    
    def source_display(self, obj):
        return obj.get_source_display()
    source_display.short_description = 'Fuente'
    
    def temperature_display(self, obj):
        if obj.temperature:
            color = 'green' if 37.5 <= obj.temperature <= 39.5 else 'red'
            return format_html('<span style="color: {};">{}°C</span>', color, obj.temperature)
        return "—"
    temperature_display.short_description = 'Temperatura'
    
    def heart_rate_display(self, obj):
        if obj.heart_rate:
            color = 'green' if 40 <= obj.heart_rate <= 70 else 'red'
            return format_html('<span style="color: {};">{} bpm</span>', color, obj.heart_rate)
        return "—"
    heart_rate_display.short_description = 'Ritmo Cardíaco'
    
    def movement_display(self, obj):
        if obj.movement_activity:
            return f"{obj.movement_activity} units"
        return "—"
    movement_display.short_description = 'Movimiento'
    
    def blockchain_linked_display(self, obj):
        if obj.blockchain_hash:
            return format_html('<span style="color: green;">✅ Sí</span>')
        return format_html('<span style="color: red;">❌ No</span>')
    blockchain_linked_display.short_description = 'En Blockchain'
    
    def polyscan_link(self, obj):
        if obj.polyscan_url:
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', obj.polyscan_url)
        return "—"
    polyscan_link.short_description = 'Transacción'
    
    def audit_trail_link(self, obj):
        url = reverse('admin:cattle_cattleaudittrail_changelist') + f'?object_id={obj.id}&object_type=health_record'
        return format_html('<a href="{}">📋 Ver Registros de Auditoría</a>', url)
    audit_trail_link.short_description = 'Auditoría'

class AnimalInline(admin.TabularInline):
    model = Batch.animals.through
    extra = 1
    verbose_name = 'Animal'
    verbose_name_plural = 'Animales en el Lote'
    readonly_fields = ['animal_minted_status', 'animal_health_status']
    
    def animal_minted_status(self, obj):
        if obj.animal.is_minted:
            return format_html('<span style="color: green;">✅ Sí</span>')
        return format_html('<span style="color: red;">❌ No</span>')
    animal_minted_status.short_description = 'NFT Minted'
    
    def animal_health_status(self, obj):
        status_colors = {
            'HEALTHY': 'green',
            'SICK': 'red',
            'RECOVERING': 'orange',
            'UNDER_OBSERVATION': 'blue',
            'QUARANTINED': 'purple'
        }
        color = status_colors.get(obj.animal.health_status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.animal.get_health_status_display())
    animal_health_status.short_description = 'Estado Salud'

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'origin',
        'destination',
        'status_display',
        'minted_animals_count_display',
        'get_total_animals_count',  # ✅ Cambiado a método
        'created_by',
        'created_at',
        'on_blockchain'  # ✅ Nuevo campo agregado
    ]
    
    list_filter = [
        'status',
        'created_by',
        'created_at',
        'on_blockchain'  # ✅ Nuevo filtro
    ]
    
    search_fields = [
        'name',
        'origin',
        'destination',
        'ipfs_hash',
        'blockchain_tx',
        'created_by__username'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'minted_animals_count_display',
        'get_total_animals_count_display',  # ✅ Cambiado a método
        'polyscan_link',
        'audit_trail_link',
        'on_blockchain'  # ✅ Solo lectura (se actualiza automáticamente)
    ]
    
    fieldsets = (
        ('Información del Lote', {
            'fields': (
                'name',
                'origin',
                'destination',
                'status',
                'created_by',
                'on_blockchain'  # ✅ Nuevo campo
            )
        }),
        ('Animales', {
            'fields': (
                'minted_animals_count_display',
                'get_total_animals_count_display',  # ✅ Cambiado
            )
        }),
        ('Blockchain', {
            'fields': (
                'ipfs_hash',
                'blockchain_tx',
                'polyscan_link'
            )
        }),
        ('Auditoría', {
            'fields': (
                'audit_trail_link',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AnimalInline]
    
    def status_display(self, obj):
        status_colors = {
            'CREATED': 'blue',
            'IN_TRANSIT': 'orange',
            'DELIVERED': 'green',
            'CANCELLED': 'red',
            'PROCESSING': 'purple',
            'QUALITY_CHECK': 'teal'
        }
        color = status_colors.get(obj.status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status_display.short_description = 'Estado'
    
    def minted_animals_count_display(self, obj):
        return f"{obj.minted_animals_count} / {obj.total_animals_count}"
    minted_animals_count_display.short_description = 'Animales con NFT'
    
    # ✅ NUEVOS MÉTODOS PARA REEMPLAZAR LA PROPERTY
    def get_total_animals_count(self, obj):
        return obj.total_animals_count
    get_total_animals_count.short_description = 'Total Animales'
    
    def get_total_animals_count_display(self, obj):
        return obj.total_animals_count
    get_total_animals_count_display.short_description = 'Total Animales'
    
    def polyscan_link(self, obj):
        if obj.polyscan_url:
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', obj.polyscan_url)
        return "—"
    polyscan_link.short_description = 'Transacción'
    
    def audit_trail_link(self, obj):
        url = reverse('admin:cattle_cattleaudittrail_changelist') + f'?object_id={obj.id}&object_type=batch'
        return format_html('<a href="{}">📋 Ver Registros de Auditoría</a>', url)
    audit_trail_link.short_description = 'Auditoría'

    def save_model(self, request, obj, form, change):
        if not change:  # Solo al crear
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    # ✅ OPCIÓN ALTERNATIVA: Usar annotations para mejor performance
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            animals_count=Count('animals'),
            minted_count=Count('animals', filter=Q(animals__token_id__isnull=False))
        )
    
    def animals_count(self, obj):
        return obj.animals_count
    animals_count.short_description = 'Total Animales'
    animals_count.admin_order_field = 'animals_count'
    
    def minted_count(self, obj):
        return obj.minted_count
    minted_count.short_description = 'Animales con NFT'
    minted_count.admin_order_field = 'minted_count'

@admin.register(CattleAuditTrail)
class CattleAuditTrailAdmin(admin.ModelAdmin):
    list_display = [
        'object_type',
        'object_id_display',
        'action_type_display',
        'user',
        'timestamp',
        'blockchain_linked_display'
    ]
    
    list_filter = [
        'object_type',
        'action_type',
        'timestamp',
        'user'
    ]
    
    search_fields = [
        'object_type',
        'object_id',
        'user__username',
        'user__email',
        'blockchain_tx_hash'
    ]
    
    readonly_fields = [
        'object_type',
        'object_id',
        'action_type',
        'user',
        'previous_state_display',
        'new_state_display',
        'changes_display',
        'ip_address',
        'blockchain_tx_hash',
        'timestamp',
        'polyscan_link'
    ]
    
    fieldsets = (
        ('Información de Auditoría', {
            'fields': (
                'object_type',
                'object_id',
                'action_type',
                'user',
                'timestamp'
            )
        }),
        ('Detalles del Cambio', {
            'fields': (
                'previous_state_display',
                'new_state_display',
                'changes_display',
            )
        }),
        ('Información Técnica', {
            'fields': (
                'ip_address',
                'blockchain_tx_hash',
                'polyscan_link'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def object_id_display(self, obj):
        # Crear enlace al objeto auditado según su tipo
        if obj.object_type == 'animal':
            url = reverse('admin:cattle_animal_change', args=[obj.object_id])
            return format_html('<a href="{}">Animal #{}</a>', url, obj.object_id)
        elif obj.object_type == 'batch':
            url = reverse('admin:cattle_batch_change', args=[obj.object_id])
            return format_html('<a href="{}">Lote #{}</a>', url, obj.object_id)
        elif obj.object_type == 'health_record':
            url = reverse('admin:cattle_animalhealthrecord_change', args=[obj.object_id])
            return format_html('<a href="{}">Registro Salud #{}</a>', url, obj.object_id)
        return obj.object_id
    object_id_display.short_description = 'Objeto'
    
    def action_type_display(self, obj):
        action_colors = {
            'CREATE': 'green',
            'UPDATE': 'blue',
            'DELETE': 'red',
            'TRANSFER': 'orange',
            'STATUS_CHANGE': 'purple',
            'HEALTH_UPDATE': 'teal'
        }
        color = action_colors.get(obj.action_type, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_action_type_display())
    action_type_display.short_description = 'Acción'
    
    def previous_state_display(self, obj):
        if obj.previous_state:
            return format_html('<pre>{}</pre>', str(obj.previous_state))
        return "Estado inicial"
    previous_state_display.short_description = 'Estado Anterior'
    
    def new_state_display(self, obj):
        if obj.new_state:
            return format_html('<pre>{}</pre>', str(obj.new_state))
        return "Sin cambios"
    new_state_display.short_description = 'Nuevo Estado'
    
    def changes_display(self, obj):
        if obj.changes:
            return format_html('<pre>{}</pre>', str(obj.changes))
        return "Sin cambios específicos"
    changes_display.short_description = 'Cambios Detallados'
    
    def blockchain_linked_display(self, obj):
        if obj.blockchain_tx_hash:
            return format_html('<span style="color: green;">✅ Sí</span>')
        return format_html('<span style="color: red;">❌ No</span>')
    blockchain_linked_display.short_description = 'En Blockchain'
    
    def polyscan_link(self, obj):
        if obj.blockchain_tx_hash:
            url = f"https://amoy.polygonscan.com/tx/{obj.blockchain_tx_hash}"
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', url)
        return "—"
    polyscan_link.short_description = 'Transacción Blockchain'

@admin.register(BlockchainEventState)
class BlockchainEventStateAdmin(admin.ModelAdmin):
    list_display = [
        'event_link',
        'state_display',
        'confirmation_blocks',
        'block_confirmed',
        'created_at'
    ]
    
    list_filter = [
        'state',
        'created_at'
    ]
    
    search_fields = [
        'event__transaction_hash',
        'event__animal__ear_tag',
        'event__batch__name'
    ]
    
    readonly_fields = [
        'event_link',
        'state',
        'confirmation_blocks',
        'block_confirmed',
        'created_at',
        'updated_at',
        'is_confirmed_display'
    ]
    
    fieldsets = (
        ('Información del Estado', {
            'fields': (
                'event_link',
                'state',
                'confirmation_blocks',
                'block_confirmed',
                'is_confirmed_display'
            )
        }),
        ('Auditoría', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def event_link(self, obj):
        if obj.event:
            url = reverse('admin:blockchain_blockchainevent_change', args=[obj.event.id])
            return format_html('<a href="{}">Evento #{}</a>', url, obj.event.id)
        return "—"
    event_link.short_description = 'Evento Blockchain'
    
    def state_display(self, obj):
        state_colors = {
            'PENDING': 'orange',
            'CONFIRMED': 'green',
            'FAILED': 'red',
            'REVERTED': 'purple'
        }
        color = state_colors.get(obj.state, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_state_display())
    state_display.short_description = 'Estado'
    
    def is_confirmed_display(self, obj):
        if obj.is_confirmed:
            return format_html('<span style="color: green;">✅ Confirmado</span>')
        return format_html('<span style="color: orange;">⏳ Pendiente</span>')
    is_confirmed_display.short_description = 'Confirmado'