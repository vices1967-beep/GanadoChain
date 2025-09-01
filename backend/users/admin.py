from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'wallet_address', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'wallet_address')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información GanadoChain', {
            'fields': ('role', 'wallet_address', 'is_verified')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información GanadoChain', {
            'fields': ('role', 'wallet_address', 'is_verified')
        }),
    )