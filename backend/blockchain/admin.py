from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    BlockchainEvent, ContractInteraction, 
    NetworkState, SmartContract, GasPriceHistory, TransactionPool,
    GovernanceProposal, Vote
)
from .market_models import MarketListing, Trade
from core.admin import format_json_field, status_badge, warning_badge, get_admin_change_link
import json

@admin.register(BlockchainEvent)
class BlockchainEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_type_display', 'short_hash', 'block_number', 
        'animal_link', 'batch_link', 'from_address_short', 
        'to_address_short', 'created_at', 'polyscan_link',
        'event_state_display'
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
        'metadata_prettified', 'event_state_link'
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

    def event_state_display(self, obj):
        return format_html('<span style="color: gray;">● SIN ESTADO</span>')
    event_state_display.short_description = 'Estado'

    def event_state_link(self, obj):
        return "—"
    event_state_link.short_description = 'Estado Extendido'

    def short_hash(self, obj):
        if obj.transaction_hash:
            return f"{obj.transaction_hash[:8]}...{obj.transaction_hash[-6:]}"
        return "—"
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
        if hasattr(obj, 'polyscan_url') and obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 PolyScan</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Blockchain'

    def metadata_prettified(self, obj):
        return format_json_field(obj.metadata)
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
                'contract_type', 'action_type', 'status_display'
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
        if obj.status == 'SUCCESS':
            return status_badge(obj.get_status_display(), True)
        elif obj.status == 'FAILED':
            return status_badge(obj.get_status_display(), False)
        else:
            return warning_badge(obj.get_status_display())
    status_display.short_description = 'Estado'

    def caller_short(self, obj):
        if obj.caller_address:
            return f"{obj.caller_address[:8]}...{obj.caller_address[-6:]}"
        return "—"
    caller_short.short_description = 'Caller'

    def short_hash(self, obj):
        if obj.transaction_hash:
            return f"{obj.transaction_hash[:8]}...{obj.transaction_hash[-6:]}"
        return "—"
    short_hash.short_description = 'Tx Hash'

    def gas_used_display(self, obj):
        if obj.gas_used:
            return f"{obj.gas_used:,}"
        return "—"
    gas_used_display.short_description = 'Gas Usado'

    def gas_cost_display(self, obj):
        if obj.gas_used and obj.gas_price:
            cost = (obj.gas_used * obj.gas_price) / 10**18
            return f"{cost:.6f} ETH"
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
        if hasattr(obj, 'polyscan_url') and obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 PolyScan</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Explorer'

    def parameters_prettified(self, obj):
        return format_json_field(obj.parameters)
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
        if obj.sync_enabled:
            return status_badge('Sincronizando', True)
        return status_badge('Detenido', False)
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
        if obj.address:
            return f"{obj.address[:8]}...{obj.address[-6:]}"
        return "—"
    short_address.short_description = 'Address'

    def is_active_display(self, obj):
        if obj.is_active:
            return status_badge('Activo', True)
        return status_badge('Inactivo', False)
    is_active_display.short_description = 'Estado'

    def is_upgradeable_display(self, obj):
        if obj.is_upgradeable:
            return status_badge('Upgradeable', True)
        return status_badge('No Upgradeable', False)
    is_upgradeable_display.short_description = 'Upgradeable'

    def polyscan_link(self, obj):
        if hasattr(obj, 'polyscan_url') and obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 Ver Contrato</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Contrato'

    def deployment_polyscan_link(self, obj):
        if hasattr(obj, 'deployment_polyscan_url') and obj.deployment_polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 Ver Deployment</a>',
                obj.deployment_polyscan_url
            )
        return "N/A"
    deployment_polyscan_link.short_description = 'Deployment'

    def abi_prettified(self, obj):
        return format_json_field(obj.abi)
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
        if obj.gas_price:
            return f"{obj.gas_price / 10**9:.2f} Gwei"
        return "N/A"
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
                'transaction_hash', 'short_hash', 'status_display', 'polyscan_link'
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
        if obj.transaction_hash:
            return f"{obj.transaction_hash[:8]}...{obj.transaction_hash[-6:]}"
        return "—"
    short_hash.short_description = 'Tx Hash'

    def polyscan_link(self, obj):
        if hasattr(obj, 'polyscan_url') and obj.polyscan_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🔗 PolyScan</a>',
                obj.polyscan_url
            )
        return "N/A"
    polyscan_link.short_description = 'Explorer'

    def raw_transaction_prettified(self, obj):
        try:
            tx_data = json.loads(obj.raw_transaction)
            return format_json_field(tx_data)
        except:
            return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>', 
                              obj.raw_transaction)
    raw_transaction_prettified.short_description = 'Transacción Cruda (Formateada)'

# Admin para modelos de Gobernanza
@admin.register(GovernanceProposal)
class GovernanceProposalAdmin(admin.ModelAdmin):
    list_display = [
        'title_short', 'proposal_type_display', 'proposed_by_link',
        'voting_status', 'status_display', 'total_votes_calculated',
        'created_at'
    ]
    list_filter = [
        'proposal_type', 'status', 'created_at', 'voting_start', 'voting_end'
    ]
    search_fields = [
        'title', 'description', 'proposed_by__email', 
        'proposed_by__first_name', 'proposed_by__last_name'
    ]
    readonly_fields = [
        'created_at', 'parameters_prettified', 'proposed_by_link',
        'voting_status', 'total_votes_calculated', 'yes_votes_calculated', 
        'no_votes_calculated', 'blockchain_proposal_link'
    ]
    fieldsets = (
        ('Información de la Propuesta', {
            'fields': (
                'title', 'description', 'proposal_type', 'proposed_by_link'
            )
        }),
        ('Votación', {
            'fields': (
                'voting_start', 'voting_end', 'status', 'voting_status',
                'total_votes_calculated', 'yes_votes_calculated', 'no_votes_calculated'
            )
        }),
        ('Parámetros', {
            'fields': ('parameters_prettified',),
            'classes': ('collapse',)
        }),
        ('Blockchain', {
            'fields': ('blockchain_proposal_id', 'blockchain_proposal_link'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )

    def title_short(self, obj):
        if obj.title:
            return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
        return "—"
    title_short.short_description = 'Título'

    def proposal_type_display(self, obj):
        type_colors = {
            'PARAMETER_CHANGE': 'blue',
            'UPGRADE': 'green',
            'GRANT': 'purple',
            'POLICY': 'orange'
        }
        color = type_colors.get(obj.proposal_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_proposal_type_display()
        )
    proposal_type_display.short_description = 'Tipo'

    def proposed_by_link(self, obj):
        if obj.proposed_by:
            return get_admin_change_link(obj.proposed_by, 'users', 'user')
        return "—"
    proposed_by_link.short_description = 'Propuesto por'

    def status_display(self, obj):
        status_colors = {
            'PENDING': 'orange',
            'ACTIVE': 'blue',
            'APPROVED': 'green',
            'REJECTED': 'red',
            'EXECUTED': 'purple'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, obj.status
        )
    status_display.short_description = 'Estado'

    def voting_status(self, obj):
        from django.utils import timezone
        now = timezone.now()
        if now < obj.voting_start:
            return format_html('<span style="color: orange;">⏰ Pendiente</span>')
        elif obj.voting_start <= now <= obj.voting_end:
            return format_html('<span style="color: green;">✅ Activa</span>')
        else:
            return format_html('<span style="color: blue;">✅ Completada</span>')
    voting_status.short_description = 'Estado Votación'

    def total_votes_calculated(self, obj):
        return obj.votes.count()
    total_votes_calculated.short_description = 'Total Votos'

    def yes_votes_calculated(self, obj):
        return obj.votes.filter(vote_value=True).count()
    yes_votes_calculated.short_description = 'Votos Sí'

    def no_votes_calculated(self, obj):
        return obj.votes.filter(vote_value=False).count()
    no_votes_calculated.short_description = 'Votos No'

    def parameters_prettified(self, obj):
        return format_json_field(obj.parameters) if obj.parameters else "—"
    parameters_prettified.short_description = 'Parámetros'

    def blockchain_proposal_link(self, obj):
        if obj.blockchain_proposal_id:
            return format_html(
                '<a href="https://polygonscan.com/tx/{}" target="_blank">🔗 Ver en Blockchain</a>',
                obj.blockchain_proposal_id
            )
        return "—"
    blockchain_proposal_link.short_description = 'Enlace Blockchain'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = [
        'proposal_link', 'voter_link', 'vote_value_display',
        'voting_power', 'created_at', 'blockchain_link'
    ]
    list_filter = ['vote_value', 'created_at']
    search_fields = [
        'proposal__title', 'voter__email', 
        'voter__first_name', 'voter__last_name'
    ]
    readonly_fields = [
        'created_at', 'proposal_link', 'voter_link',
        'vote_value_display', 'blockchain_link'
    ]
    fieldsets = (
        ('Información del Voto', {
            'fields': (
                'proposal_link', 'voter_link', 'vote_value', 'voting_power'
            )
        }),
        ('Blockchain', {
            'fields': ('blockchain_vote_hash', 'blockchain_link')
        }),
        ('Temporal', {
            'fields': ('created_at',)
        })
    )

    def proposal_link(self, obj):
        if obj.proposal:
            return get_admin_change_link(obj.proposal, 'blockchain', 'governanceproposal')
        return "—"
    proposal_link.short_description = 'Propuesta'

    def voter_link(self, obj):
        if obj.voter:
            return get_admin_change_link(obj.voter, 'users', 'user')
        return "—"
    voter_link.short_description = 'Votante'

    def vote_value_display(self, obj):
        if obj.vote_value:
            return format_html('<span style="color: green;">✅ Sí</span>')
        else:
            return format_html('<span style="color: red;">❌ No</span>')
    vote_value_display.short_description = 'Voto'

    def blockchain_link(self, obj):
        if obj.blockchain_vote_hash:
            return format_html(
                '<a href="https://polygonscan.com/tx/{}" target="_blank">🔗 Ver en Blockchain</a>',
                obj.blockchain_vote_hash
            )
        return "—"
    blockchain_link.short_description = 'Enlace Blockchain'

# Admin para modelos de Mercado
@admin.register(MarketListing)
class MarketListingAdmin(admin.ModelAdmin):
    list_display = [
        'animal_link', 'seller_link', 'price_display',
        'currency', 'listing_status', 'expiration_status',
        'listing_date'
    ]
    list_filter = ['currency', 'is_active', 'listing_date', 'expiration_date']
    search_fields = [
        'animal__ear_tag', 'seller__email', 
        'seller__first_name', 'seller__last_name'
    ]
    readonly_fields = [
        'listing_date', 'animal_link', 'seller_link',
        'blockchain_link', 'listing_status', 'expiration_status'
    ]
    fieldsets = (
        ('Información del Listado', {
            'fields': (
                'animal_link', 'seller_link', 'price', 'currency'
            )
        }),
        ('Fechas', {
            'fields': ('listing_date', 'expiration_date')
        }),
        ('Estado', {
            'fields': ('is_active', 'listing_status', 'expiration_status')
        }),
        ('Blockchain', {
            'fields': ('blockchain_listing_id', 'blockchain_link'),
            'classes': ('collapse',)
        })
    )

    def animal_link(self, obj):
        if obj.animal:
            return get_admin_change_link(obj.animal, 'cattle', 'animal')
        return "—"
    animal_link.short_description = 'Animal'

    def seller_link(self, obj):
        if obj.seller:
            return get_admin_change_link(obj.seller, 'users', 'user')
        return "—"
    seller_link.short_description = 'Vendedor'

    def price_display(self, obj):
        if obj.price and obj.currency:
            return f"{obj.price} {obj.currency}"
        return "—"
    price_display.short_description = 'Precio'

    def listing_status(self, obj):
        if obj.is_active:
            return status_badge('Activo', True)
        return status_badge('Inactivo', False)
    listing_status.short_description = 'Estado'

    def expiration_status(self, obj):
        from django.utils import timezone
        if obj.expiration_date and obj.expiration_date < timezone.now():
            return format_html('<span style="color: red;">❌ Expirado</span>')
        elif obj.expiration_date:
            days_left = (obj.expiration_date - timezone.now()).days
            return format_html('<span style="color: green;">✅ {} días</span>', days_left)
        return "—"
    expiration_status.short_description = 'Expiración'

    def blockchain_link(self, obj):
        if obj.blockchain_listing_id:
            return format_html(
                '<a href="https://polygonscan.com/address/{}" target="_blank">🔗 Ver en Blockchain</a>',
                obj.blockchain_listing_id
            )
        return "—"
    blockchain_link.short_description = 'Enlace Blockchain'

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = [
        'listing_link', 'buyer_link', 'price_display',
        'platform_fee_display', 'status_display', 'trade_date'
    ]
    list_filter = ['status', 'trade_date']
    search_fields = [
        'listing__animal__ear_tag', 'buyer__email', 
        'buyer__first_name', 'buyer__last_name',
        'transaction_hash'
    ]
    readonly_fields = [
        'trade_date', 'listing_link', 'buyer_link',
        'blockchain_link', 'status_display'
    ]
    fieldsets = (
        ('Información de la Transacción', {
            'fields': (
                'listing_link', 'buyer_link', 'price', 'currency', 'platform_fee'
            )
        }),
        ('Estado', {
            'fields': ('status', 'status_display')
        }),
        ('Blockchain', {
            'fields': ('transaction_hash', 'blockchain_link')
        }),
        ('Temporal', {
            'fields': ('trade_date',)
        })
    )

    def listing_link(self, obj):
        if obj.listing:
            return get_admin_change_link(obj.listing, 'blockchain', 'marketlisting')
        return "—"
    listing_link.short_description = 'Listado'

    def buyer_link(self, obj):
        if obj.buyer:
            return get_admin_change_link(obj.buyer, 'users', 'user')
        return "—"
    buyer_link.short_description = 'Comprador'

    def price_display(self, obj):
        if obj.price and obj.currency:
            return f"{obj.price} {obj.currency}"
        return "—"
    price_display.short_description = 'Precio'

    def platform_fee_display(self, obj):
        if obj.platform_fee and obj.currency:
            return f"{obj.platform_fee} {obj.currency}"
        return "—"
    platform_fee_display.short_description = 'Comisión'

    def status_display(self, obj):
        status_colors = {
            'PENDING': 'orange',
            'COMPLETED': 'green',
            'FAILED': 'red',
            'CANCELLED': 'gray'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_display.short_description = 'Estado'

    def blockchain_link(self, obj):
        if obj.transaction_hash:
            return format_html(
                '<a href="https://polygonscan.com/tx/{}" target="_blank">🔗 Ver en Blockchain</a>',
                obj.transaction_hash
            )
        return "—"
    blockchain_link.short_description = 'Enlace Blockchain'

# Configuración del Admin Site
admin.site.site_header = "🐄 GanadoChain - Blockchain Administration"
admin.site.site_title = "GanadoChain Blockchain Admin"
admin.site.index_title = "Administración de Blockchain"

# Personalizar el orden de las apps
def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    
    # Reordenar las apps
    app_ordering = {
        'cattle': 1,      # Primero: Módulo de Animales
        'blockchain': 2,  # Segundo: Blockchain
        'iot': 3,         # Tercero: IoT
        'users': 4,       # Usuarios
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