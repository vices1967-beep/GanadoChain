# core/management/commands/setup_admin_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Configura el usuario administrador con su wallet y todos los roles del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario del administrador (por defecto: "vices")',
            default='vices'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Establece una contraseña para el usuario (opcional)',
            default=None
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email del administrador (por defecto: username@ganadochain.com)',
            default=None
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar actualización incluso si el usuario ya existe',
            default=False
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']
        email = options['email']
        force_update = options['force']
        verbosity = options.get('verbosity', 1)

        # 1. OBTENER LA WALLET DEL ADMIN DESDE .ENV
        admin_wallet_address = os.environ.get('ADMIN_WALLET_ADDRESS', '').lower()
        
        if not admin_wallet_address:
            self.stderr.write(self.style.ERROR('❌ ADMIN_WALLET_ADDRESS no configurada en .env'))
            self.stderr.write('Por favor, agrega ADMIN_WALLET_ADDRESS=0xTuDireccion a tu archivo .env')
            return

        # 2. OBTENER OTRAS CONFIGURACIONES DE .ENV
        rpc_url = os.environ.get('BLOCKCHAIN_RPC_URL', 'https://rpc-amoy.polygon.technology')
        registry_address = os.environ.get('REGISTRY_ADDRESS', '')
        token_address = os.environ.get('GANADO_TOKEN_ADDRESS', '')
        nft_address = os.environ.get('ANIMAL_NFT_ADDRESS', '')

        # 3. DEFINIR TODOS LOS ROLES DEL SISTEMA
        roles_para_el_admin = [
            'PRODUCER_ROLE',
            'VET_ROLE', 
            'AUDITOR_ROLE',
            'FRIGORIFICO_ROLE',
            'IOT_ROLE',
            'DAO_ROLE',
            'DEFAULT_ADMIN_ROLE'
        ]

        # 4. CONFIGURAR EMAIL POR DEFECTO SI NO SE PROPORCIONA
        if not email:
            email = f'{username}@ganadochain.com'

        # 5. BUSCAR O CREAR EL USUARIO ADMINISTRADOR
        try:
            usuario, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'wallet_address': admin_wallet_address,
                    'role': 'ADMIN',
                    'blockchain_roles': roles_para_el_admin,
                    'is_verified': True,
                    'is_blockchain_active': True,
                    'is_staff': True,
                    'is_superuser': True,
                    'first_name': 'Administrador',
                    'last_name': 'del Sistema'
                }
            )

            if created:
                # Para un usuario NUEVO, establecer contraseña solo si se proporciona
                if password:
                    usuario.set_password(password)
                    if verbosity >= 1:
                        self.stdout.write(self.style.WARNING('⚠️  Se estableció una contraseña para el nuevo usuario.'))
                else:
                    usuario.set_unusable_password()
                    if verbosity >= 1:
                        self.stdout.write(self.style.WARNING('⚠️  Nuevo usuario creado SIN contraseña (solo auth por wallet).'))
                
                usuario.save()
                action_msg = "Creado"
            else:
                # Para un usuario EXISTENTE
                action_msg = "Encontrado"
                
                # Actualizar solo si se fuerza o si no tiene la configuración correcta
                needs_update = (
                    force_update or
                    usuario.wallet_address != admin_wallet_address or
                    usuario.role != 'ADMIN' or
                    usuario.blockchain_roles != roles_para_el_admin or
                    not usuario.is_verified or
                    not usuario.is_blockchain_active or
                    not usuario.is_staff or
                    not usuario.is_superuser
                )
                
                if needs_update:
                    usuario.wallet_address = admin_wallet_address
                    usuario.role = 'ADMIN'
                    usuario.blockchain_roles = roles_para_el_admin
                    usuario.is_verified = True
                    usuario.is_blockchain_active = True
                    usuario.is_staff = True
                    usuario.is_superuser = True
                    usuario.email = email
                    
                    # Solo establecer nueva contraseña si se proporciona explícitamente
                    if password:
                        usuario.set_password(password)
                        if verbosity >= 1:
                            self.stdout.write(self.style.WARNING('⚠️  Contraseña actualizada.'))
                    
                    usuario.save()
                    action_msg = "Actualizado"
                else:
                    if verbosity >= 1:
                        self.stdout.write(self.style.SUCCESS('✅ El usuario ya está correctamente configurado.'))

            # 6. MOSTRAR RESULTADOS DETALLADOS
            if verbosity >= 1:
                self.stdout.write("\n" + "="*60)
                self.stdout.write(self.style.SUCCESS(f'✅ {action_msg} usuario administrador: {usuario.username}'))
                self.stdout.write("="*60)
                
                self.stdout.write(f'   📧 Email: {usuario.email}')
                self.stdout.write(f'   👛 Wallet: {usuario.wallet_address}')
                self.stdout.write(f'   🎯 Rol de Sistema: {usuario.get_role_display()}')
                self.stdout.write(f'   🔗 Roles Blockchain: {len(usuario.blockchain_roles)} roles')
                self.stdout.write(f'   ✅ Verificado: {usuario.is_verified}')
                self.stdout.write(f'   🚀 Activo en Blockchain: {usuario.is_blockchain_active}')
                self.stdout.write(f'   🛠️  Staff: {usuario.is_staff}')
                self.stdout.write(f'   👑 Superusuario: {usuario.is_superuser}')
                self.stdout.write(f'   🔐 Tiene contraseña: {usuario.has_usable_password()}')

            if verbosity >= 2:
                self.stdout.write(f'\n   📋 Lista completa de roles:')
                for role in usuario.blockchain_roles:
                    self.stdout.write(f'      • {role}')

            # 7. MOSTRAR INFORMACIÓN DE CONFIGURACIÓN BLOCKCHAIN
            if verbosity >= 1:
                self.stdout.write(f'\n🌐 Configuración Blockchain:')
                self.stdout.write(f'   📡 RPC: {rpc_url}')
                if registry_address:
                    self.stdout.write(f'   🏛️  Registry: {registry_address}')
                if token_address:
                    self.stdout.write(f'   💰 Token: {token_address}')
                if nft_address:
                    self.stdout.write(f'   🐄 NFT: {nft_address}')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Error configurando el usuario administrador: {e}'))
            import traceback
            self.stderr.write(traceback.format_exc())
            return

        # 8. MENSAJES DE SIGUIENTES PASOS
        if verbosity >= 1:
            self.stdout.write("\n" + "="*60)
            self.stdout.write(self.style.SUCCESS('🎉 Configuración del administrador completada.'))
            
            if not usuario.has_usable_password():
                self.stdout.write(self.style.WARNING(
                    '\n⚠️  ATENCIÓN: Este usuario no tiene contraseña utilizable.'
                ))
                self.stdout.write('   Para poder acceder al admin de Django, ejecuta:')
                self.stdout.write(self.style.NOTICE(
                    f'   python manage.py setup_admin_user --username={username} --password=tu_contraseña'
                ))
            
            self.stdout.write(self.style.WARNING(
                '\n⚠️  RECUERDA: Este usuario debe tener la private key correspondiente '
                'a esta wallet en la variable ADMIN_PRIVATE_KEY de tu .env'
            ))
            
            self.stdout.write(self.style.SUCCESS(
                '\n📋 Próximo paso: Conceder roles on-chain a los usuarios del DAO'
            ))
            self.stdout.write(self.style.NOTICE(
                '   python manage.py grant_dao_roles'
            ))
            self.stdout.write("="*60)

    def get_contract_addresses(self):
        """Obtiene las direcciones de los contratos desde .env"""
        return {
            'registry': os.environ.get('REGISTRY_ADDRESS', 'No configurado'),
            'token': os.environ.get('GANADO_TOKEN_ADDRESS', 'No configurado'),
            'nft': os.environ.get('ANIMAL_NFT_ADDRESS', 'No configurado')
        }