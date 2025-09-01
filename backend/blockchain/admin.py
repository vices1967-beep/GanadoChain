from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    BlockchainEvent, ContractInteraction, 
    NetworkState, SmartContract, GasPriceHistory, TransactionPool
)
import json

@admin.register(BlockchainEvent)
class BlockchainEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_type_display', 'short_hash', 'block_number', 
        'animal_link', 'batch_link', 'from_address_short', 
        'to_address_short', 'created_at', 'polyscan_link'
    ]
    list_filter = [
        'event_type', 'created_at', 'block_number'
    ]
    search_fields = [
        'transaction_hash', 'animal__ear_tag', 'batch__name',
        'from_address', 'to_address'
    ]
    readonly_fields = [
        'transaction_hash', 'block_number', 'created_at',
        'polyscan_link', 'short_hash', 'animal_link', 'batch_link',
        'metadata_prettified'
    ]
    fieldsets = (
        ('Información de Transacción', {
            'fields': (
                'event_type', 'transaction_hash', 'short_hash', 'block_number',
                'polyscan_link'
            )
        }),
        ('Entidades Involucradas', {
            'fields': (
                'animal_link', 'batch_link', 'from_address', 'to_address'
            )
        }),
        ('Metadata', {
            'fields': ('metadata_prettified',),
            'classes': ('collapse',)
        }),
        ('Información Temporal', {
            'fields': ('created_at',),
            'classes': ('wide',)
        })
    )

    def event_type_display(self, obj):
        event_colors = {
            'MINT': 'green',
            'TRANSFER': 'blue',
            'ROLE_ADD': 'purple',
            'ROLE_REMOVE': 'orange',
            'HEALTH_UPDATE': 'red',
            'LOCATION_UPDATE': 'teal',
            'BATCH_CREATED': 'indigo',
            'TOKEN_MINTED': 'pink',
            'IOT_DATA': 'brown'
        }
        color = event_colors.get(obj.event_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_event_type_display()
        )
    event_type_display.short_description = 'Tipo de Evento'
    event_type_display.admin_order_field = 'event_type'

    def short_hash(self, obj):
        return obj.short_hash
    short_hash.short_description = 'Hash'

    def animal_link(self, obj):
        if obj.animal:
            url = reverse('admin:cattle_animal_change', args=[obj.animal.id])
            return format_html('<a href="{}">{}</a>', url, obj.animal.ear_tag)
        return "—"
    animal_link.short_description = 'Animal'

    def batch_link(self, obj):
        if obj.batch:
            url = reverse('admin:cattle_batch_change', args=[obj.batch.id])
            return format_html('<a href="{}">{}</a>', url, obj.batch.name)
        return "—"
    batch_link.short_description = 'Lote'

    def from_address_short(self, obj):
        if obj.from_address:
            return f"{obj.from_address[:8]}...{obj.from_address[-6:]}"
        return "—"
    from_address_short.short_description = 'From'

    def to_address_short(self, obj):
        if obj.to_address:
            return f"{obj.to_address[:8]}...{obj.to_address[-6:]}"
        return "—"
    to_address_short.short_description = 'To'

    def polyscan_link(self, obj):
        if obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 PolyScan</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Blockchain'

    def metadata_prettified(self, obj):
        return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>', 
                          json.dumps(obj.metadata, indent=2, ensure_ascii=False))
    metadata_prettified.short_description = 'Metadata (Formateada)'

@admin.register(ContractInteraction)
class ContractInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'contract_type_display', 'action_type_display', 'short_hash',
        'caller_short', 'status_display', 'gas_used_display',
        'gas_cost_display', 'created_at'
    ]
    list_filter = [
        'contract_type', 'action_type', 'status', 'created_at'
    ]
    search_fields = [
        'transaction_hash', 'caller_address', 'target_address'
    ]
    readonly_fields = [
        'transaction_hash', 'block_number', 'created_at',
        'updated_at', 'polyscan_link', 'gas_cost_eth',
        'gas_cost_usd', 'parameters_prettified'
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
                'parameters_prettified', 'gas_used', 'gas_price', 
                'gas_cost_eth', 'gas_cost_usd'
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

    def contract_type_display(self, obj):
        type_colors = {
            'NFT': 'blue',
            'TOKEN': 'green',
            'REGISTRY': 'purple',
            'IOT': 'orange',
            'BATCH': 'teal'
        }
        color = type_colors.get(obj.contract_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_contract_type_display()
        )
    contract_type_display.short_description = 'Tipo Contrato'

    def action_type_display(self, obj):
        return obj.get_action_type_display()
    action_type_display.short_description = 'Acción'

    def status_display(self, obj):
        status_colors = {
            'SUCCESS': 'green',
            'FAILED': 'red',
            'PENDING': 'orange'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Estado'

    def caller_short(self, obj):
        if obj.caller_address:
            return f"{obj.caller_address[:8]}...{obj.caller_address[-6:]}"
        return "—"
    caller_short.short_description = 'Caller'

    def short_hash(self, obj):
        return obj.short_hash
    short_hash.short_description = 'Tx Hash'

    def gas_used_display(self, obj):
        if obj.gas_used:
            return f"{obj.gas_used:,}"
        return "—"
    gas_used_display.short_description = 'Gas Usado'

    def gas_cost_display(self, obj):
        if obj.gas_cost_eth:
            return f"{obj.gas_cost_eth:.6f} ETH"
        return "—"
    gas_cost_display.short_description = 'Costo'

    def gas_cost_eth(self, obj):
        if obj.gas_used and obj.gas_price:
            cost = (obj.gas_used * obj.gas_price) / 10**18
            return f"{cost:.8f}"
        return "N/A"
    gas_cost_eth.short_description = 'Costo (ETH)'

    def gas_cost_usd(self, obj):
        eth_price = 3000  # Precio estimado de ETH en USD
        if obj.gas_used and obj.gas_price:
            cost_eth = (obj.gas_used * obj.gas_price) / 10**18
            return f"${cost_eth * eth_price:.2f} USD"
        return "N/A"
    gas_cost_usd.short_description = 'Costo (USD)'

    def polyscan_link(self, obj):
        if obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 PolyScan</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Explorer'

    def parameters_prettified(self, obj):
        return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>', 
                          json.dumps(obj.parameters, indent=2, ensure_ascii=False))
    parameters_prettified.short_description = 'Parámetros (Formateados)'

@admin.register(NetworkState)
class NetworkStateAdmin(admin.ModelAdmin):
    list_display = [
        'network_name', 'chain_id', 'last_block_number', 
        'average_gas_price_gwei', 'active_nodes', 
        'last_sync_ago', 'sync_status'
    ]
    readonly_fields = [
        'last_sync_time', 'created_at', 'average_gas_price_gwei',
        'sync_status', 'last_sync_ago'
    ]
    fieldsets = (
        ('Estado de Red', {
            'fields': (
                'network_name', 'chain_id', 'last_block_number', 
                'average_gas_price', 'average_gas_price_gwei'
            )
        }),
        ('Métricas de Red', {
            'fields': ('active_nodes', 'sync_enabled', 'sync_status')
        }),
        ('Configuración', {
            'fields': ('rpc_url', 'block_time', 'native_currency', 'is_testnet')
        }),
        ('Timestamps', {
            'fields': ('last_sync_time', 'last_sync_ago', 'created_at')
        })
    )

    def average_gas_price_gwei(self, obj):
        if obj.average_gas_price:
            return f"{obj.average_gas_price / 10**9:.2f} Gwei"
        return "N/A"
    average_gas_price_gwei.short_description = 'Precio Gas (Gwei)'

    def sync_status(self, obj):
        color = 'green' if obj.sync_enabled else 'red'
        status = 'Sincronizando' if obj.sync_enabled else 'Detenido'
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, status
        )
    sync_status.short_description = 'Estado Sync'

    def last_sync_ago(self, obj):
        from django.utils import timezone
        from django.utils.timesince import timesince
        if obj.last_sync_time:
            return timesince(obj.last_sync_time, timezone.now())
        return "Nunca"
    last_sync_ago.short_description = 'Última Sync'

@admin.register(SmartContract)
class SmartContractAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'contract_type_display', 'short_address',
        'version', 'is_active_display', 'deployment_block',
        'is_upgradeable_display'
    ]
    list_filter = [
        'contract_type', 'is_active', 'version', 'is_upgradeable'
    ]
    search_fields = [
        'name', 'address', 'deployment_tx_hash', 'deployer_address'
    ]
    readonly_fields = [
        'deployment_block', 'created_at', 'updated_at',
        'polyscan_link', 'deployment_polyscan_link', 'short_address',
        'abi_prettified'
    ]
    fieldsets = (
        ('Información del Contrato', {
            'fields': (
                'name', 'contract_type', 'version', 'is_active'
            )
        }),
        ('Addresses', {
            'fields': ('address', 'short_address', 'deployer_address')
        }),
        ('Información de Deployment', {
            'fields': (
                'deployment_block', 'deployment_tx_hash',
                'polyscan_link', 'deployment_polyscan_link'
            )
        }),
        ('Configuración Avanzada', {
            'fields': (
                'is_upgradeable', 'implementation_address', 
                'proxy_address', 'admin_address'
            ),
            'classes': ('collapse',)
        }),
        ('ABI', {
            'fields': ('abi_prettified',),
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
            'IOT': 'orange',
            'BATCH': 'teal'
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

    def is_upgradeable_display(self, obj):
        color = 'green' if obj.is_upgradeable else 'gray'
        status = 'Upgradeable' if obj.is_upgradeable else 'No Upgradeable'
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, status
        )
    is_upgradeable_display.short_description = 'Upgradeable'

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

    def abi_prettified(self, obj):
        return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; max-height: 300px;">{}</pre>', 
                          json.dumps(obj.abi, indent=2, ensure_ascii=False))
    abi_prettified.short_description = 'ABI (Formateada)'

@admin.register(GasPriceHistory)
class GasPriceHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'gas_price_gwei', 'block_number', 'timestamp'
    ]
    list_filter = [
        'timestamp'
    ]
    readonly_fields = [
        'timestamp'
    ]
    fieldsets = (
        ('Información de Gas', {
            'fields': (
                'gas_price', 'gas_price_gwei', 'block_number'
            )
        }),
        ('Temporal', {
            'fields': ('timestamp',)
        })
    )

    def gas_price_gwei(self, obj):
        return f"{obj.gas_price_gwei:.2f} Gwei"
    gas_price_gwei.short_description = 'Precio Gas'

@admin.register(TransactionPool)
class TransactionPoolAdmin(admin.ModelAdmin):
    list_display = [
        'short_hash', 'status_display', 'retry_count',
        'last_retry', 'created_at'
    ]
    list_filter = [
        'status', 'created_at'
    ]
    search_fields = [
        'transaction_hash'
    ]
    readonly_fields = [
        'transaction_hash', 'created_at', 'updated_at',
        'polyscan_link', 'short_hash', 'raw_transaction_prettified'
    ]
    fieldsets = (
        ('Información de Transacción', {
            'fields': (
                'transaction_hash', 'short_hash', 'status', 'polyscan_link'
            )
        }),
        ('Intentos', {
            'fields': ('retry_count', 'last_retry')
        }),
        ('Datos Crudos', {
            'fields': ('raw_transaction_prettified',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )

    def status_display(self, obj):
        status_colors = {
            'PENDING': 'orange',
            'PROCESSING': 'blue',
            'CONFIRMED': 'green',
            'FAILED': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Estado'

    def short_hash(self, obj):
        return obj.short_hash
    short_hash.short_description = 'Tx Hash'

    def polyscan_link(self, obj):
        if obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 PolyScan</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Explorer'

    def raw_transaction_prettified(self, obj):
        try:
            tx_data = json.loads(obj.raw_transaction)
            return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>', 
                              json.dumps(tx_data, indent=2, ensure_ascii=False))
        except:
            return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>', 
                              obj.raw_transaction)
    raw_transaction_prettified.short_description = 'Transacción Cruda (Formateada)'

# Configuración del Admin Site
admin.site.site_header = "🐄 GanadoChain Administration"
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