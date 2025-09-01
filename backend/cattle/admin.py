from django.contrib import admin
from django.utils.html import format_html
from .models import Animal, Batch

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = [
        'ear_tag', 
        'breed', 
        'owner', 
        'health_status',
        'token_id',
        'is_minted_display',
        'mint_transaction_short',
        'created_at'
    ]
    
    list_filter = [
        'health_status',
        'breed',
        'owner',
        'created_at'
    ]
    
    search_fields = [
        'ear_tag',
        'breed',
        'token_id',
        'mint_transaction_hash',
        'ipfs_hash'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'is_minted_display',
        'metadata_uri_display',
        'mint_transaction_link'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'ear_tag', 
                'breed', 
                'birth_date', 
                'weight',
                'health_status',
                'location',
                'owner'
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
                'mint_transaction_link'
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
        if obj.mint_transaction_hash:
            explorer_url = f"https://amoy.polygonscan.com/tx/0x{obj.mint_transaction_hash}"
            return format_html('<a href="{}" target="_blank">Ver en Explorer</a>', explorer_url)
        return "—"
    mint_transaction_link.short_description = 'Enlace Transacción'

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'origin',
        'destination',
        'status',
        'minted_animals_count_display',
        'total_animals_count',
        'created_by',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'created_by',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'origin',
        'destination',
        'ipfs_hash',
        'blockchain_tx'
    ]
    
    filter_horizontal = ['animals']
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'minted_animals_count_display',
        'total_animals_count_display'
    ]
    
    fieldsets = (
        ('Información del Lote', {
            'fields': (
                'name',
                'origin',
                'destination',
                'status',
                'created_by'
            )
        }),
        ('Animales', {
            'fields': (
                'animals',
                'minted_animals_count_display',
                'total_animals_count_display'
            )
        }),
        ('Blockchain', {
            'fields': (
                'ipfs_hash',
                'blockchain_tx'
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
    
    def minted_animals_count_display(self, obj):
        return f"{obj.minted_animals_count} / {obj.total_animals_count}"
    minted_animals_count_display.short_description = 'Animales con NFT'
    
    def total_animals_count_display(self, obj):
        return obj.total_animals_count
    total_animals_count_display.short_description = 'Total Animales'

    def save_model(self, request, obj, form, change):
        if not change:  # Solo al crear
            obj.created_by = request.user
        super().save_model(request, obj, form, change)