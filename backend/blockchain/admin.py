# blockchain/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    BlockchainEvent, ContractInteraction, 
    NetworkState, SmartContract
)

@admin.register(BlockchainEvent)
class BlockchainEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_type_display', 'short_hash', 'block_number', 
        'animal_display', 'from_address_short', 'to_address_short',
        'created_at', 'polyscan_link'
    ]
    list_filter = [
        'event_type', 'created_at', 'block_number'
    ]
    search_fields = [
        'transaction_hash', 'animal__ear_tag', 
        'from_address', 'to_address'
    ]
    readonly_fields = [
        'transaction_hash', 'block_number', 'created_at',
        'polyscan_link', 'short_hash'
    ]
    fieldsets = (
        ('Información de Transacción', {
            'fields': (
                'event_type', 'transaction_hash', 'block_number',
                'polyscan_link'
            )
        }),
        ('Entidades Involucradas', {
            'fields': (
                'animal', 'batch', 'from_address', 'to_address'
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Información Temporal', {
            'fields': ('created_at',),
            'classes': ('wide',)
        })
    )

    def event_type_display(self, obj):
        return obj.get_event_type_display()
    event_type_display.short_description = 'Tipo de Evento'
    event_type_display.admin_order_field = 'event_type'

    def short_hash(self, obj):
        return obj.short_hash
    short_hash.short_description = 'Hash'

    def animal_display(self, obj):
        if obj.animal:
            return f"{obj.animal.ear_tag} ({obj.animal.breed})"
        return "N/A"
    animal_display.short_description = 'Animal'

    def from_address_short(self, obj):
        if obj.from_address:
            return f"{obj.from_address[:8]}...{obj.from_address[-6:]}"
        return "N/A"
    from_address_short.short_description = 'From'

    def to_address_short(self, obj):
        if obj.to_address:
            return f"{obj.to_address[:8]}...{obj.to_address[-6:]}"
        return "N/A"
    to_address_short.short_description = 'To'

    def polyscan_link(self, obj):
        if obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 Ver en PolyScan</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Blockchain'

@admin.register(ContractInteraction)
class ContractInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'contract_type', 'action_type', 'short_hash',
        'caller_short', 'status_display', 'gas_used',
        'created_at'
    ]
    list_filter = [
        'contract_type', 'action_type', 'status', 'created_at'
    ]
    search_fields = [
        'transaction_hash', 'caller_address', 'target_address'
    ]
    readonly_fields = [
        'transaction_hash', 'block_number', 'created_at',
        'updated_at', 'polyscan_link', 'gas_cost_eth'
    ]
    fieldsets = (
        ('Información de Contrato', {
            'fields': (
                'contract_type', 'action_type', 'status'
            )
        }),
        ('Transacción', {
            'fields': (
                'transaction_hash', 'block_number', 'polyscan_link'
            )
        }),
        ('Addresses', {
            'fields': ('caller_address', 'target_address')
        }),
        ('Parámetros y Gas', {
            'fields': (
                'parameters', 'gas_used', 'gas_price', 'gas_cost_eth'
            ),
            'classes': ('wide',)
        }),
        ('Error Handling', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('wide',)
        })
    )

    def status_display(self, obj):
        status_colors = {
            'SUCCESS': 'green',
            'FAILED': 'red',
            'PENDING': 'orange'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Estado'

    def caller_short(self, obj):
        if obj.caller_address:
            return f"{obj.caller_address[:8]}...{obj.caller_address[-6:]}"
        return "N/A"
    caller_short.short_description = 'Caller'

    def short_hash(self, obj):
        return obj.short_hash
    short_hash.short_description = 'Tx Hash'

    def gas_cost_eth(self, obj):
        if obj.gas_used and obj.gas_price:
            cost = (obj.gas_used * obj.gas_price) / 10**18
            return f"{cost:.8f} ETH"
        return "N/A"
    gas_cost_eth.short_description = 'Costo de Gas'

    def polyscan_link(self, obj):
        if obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 PolyScan</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Explorer'

@admin.register(NetworkState)
class NetworkStateAdmin(admin.ModelAdmin):
    list_display = [
        'chain_id', 'last_block_number', 'average_gas_price',
        'active_nodes', 'last_sync_time', 'sync_status'
    ]
    readonly_fields = [
        'last_sync_time', 'created_at'
    ]
    fieldsets = (
        ('Estado de Red', {
            'fields': (
                'chain_id', 'last_block_number', 'average_gas_price'
            )
        }),
        ('Métricas de Red', {
            'fields': ('active_nodes', 'sync_enabled')
        }),
        ('Timestamps', {
            'fields': ('last_sync_time', 'created_at')
        })
    )

    def sync_status(self, obj):
        color = 'green' if obj.sync_enabled else 'red'
        status = 'Sincronizando' if obj.sync_enabled else 'Detenido'
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, status
        )
    sync_status.short_description = 'Estado Sync'

@admin.register(SmartContract)
class SmartContractAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'contract_type_display', 'short_address',
        'version', 'is_active_display', 'deployment_block'
    ]
    list_filter = [
        'contract_type', 'is_active', 'version'
    ]
    search_fields = [
        'name', 'address', 'deployment_tx_hash'
    ]
    readonly_fields = [
        'deployment_block', 'created_at', 'updated_at',
        'polyscan_link', 'deployment_polyscan_link'
    ]
    fieldsets = (
        ('Información del Contrato', {
            'fields': (
                'name', 'contract_type', 'version', 'is_active'
            )
        }),
        ('Addresses', {
            'fields': ('address', 'deployer_address')
        }),
        ('Blockchain Info', {
            'fields': (
                'deployment_block', 'deployment_tx_hash',
                'polyscan_link', 'deployment_polyscan_link'
            )
        }),
        ('ABI', {
            'fields': ('abi',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )

    def contract_type_display(self, obj):
        type_colors = {
            'NFT': 'blue',
            'TOKEN': 'green',
            'REGISTRY': 'purple',
            'IOT': 'orange'
        }
        color = type_colors.get(obj.contract_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_contract_type_display()
        )
    contract_type_display.short_description = 'Tipo'

    def short_address(self, obj):
        return obj.short_address
    short_address.short_description = 'Address'

    def is_active_display(self, obj):
        color = 'green' if obj.is_active else 'red'
        status = 'Activo' if obj.is_active else 'Inactivo'
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, status
        )
    is_active_display.short_description = 'Estado'

    def polyscan_link(self, obj):
        if obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 Ver Contrato</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Contrato'

    def deployment_polyscan_link(self, obj):
        if obj.deployment_polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 Ver Deployment</a>',
                obj.deployment_polyscan_url
            )
        return "N/A"
    deployment_polyscan_link.short_description = 'Deployment'

# Configuración del Admin Site
admin.site.site_header = "GanadoChain Administration"
admin.site.site_title = "GanadoChain Admin Portal"
admin.site.index_title = "Bienvenido al Portal de Administración de GanadoChain"

# Personalizar el orden de las apps
def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    
    # Reordenar las apps
    app_ordering = {
        'cattle': 1,      # Primero: Módulo de Animales
        'blockchain': 2,  # Segundo: Blockchain
        'iot': 3,         # Tercero: IoT
        'auth': 4,        # Autenticación
        'authtoken': 5,   # Tokens
    }
    
    app_list = sorted(
        app_dict.values(), 
        key=lambda x: app_ordering.get(x['app_label'], 10)
    )
    
    return app_list

# Aplicar la personalización
admin.AdminSite.get_app_list = get_app_list