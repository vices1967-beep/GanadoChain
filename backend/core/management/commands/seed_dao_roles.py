# core/management/commands/seed_dao_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

class Command(BaseCommand):
    help = 'Crea o actualiza los usuarios predefinidos con roles específicos para el DAO'

    def handle(self, *args, **options):
        # Datos de los usuarios a crear. La clave es el username para buscar/crear.
        dao_users = {
            'productor_dao': {
                'wallet_address': '0xFdA1b969c9e33910F221326f70A661C517d16f90',
                'role': 'PRODUCER',
                'blockchain_roles': ['PRODUCER_ROLE'],
                'email': 'productor@dao.com',
                'first_name': 'Productor',
                'last_name': 'DAO',
                'is_verified': False,
                'is_blockchain_active': True,
            },
            'veterinario_dao': {
                'wallet_address': '0x59eBcf4d12350D804F0d773b522b30d1Bf38ac6a',
                'role': 'VET',
                'blockchain_roles': ['VET_ROLE'],
                'email': 'veterinario@dao.com',
                'first_name': 'Veterinario',
                'last_name': 'DAO',
                'is_verified': False,
                'is_blockchain_active': True,
            },
            'auditor_dao': {
                'wallet_address': '0x4eE2a4e9ca534D35b7745d42FcF84677cb3ee97a',
                'role': 'AUDITOR',
                'blockchain_roles': ['AUDITOR_ROLE'],
                'email': 'auditor@dao.com',
                'first_name': 'Auditor',
                'last_name': 'DAO',
                'is_verified': False,
                'is_blockchain_active': True,
            },
            'frigorifico_dao': {
                'wallet_address': '0x41174B08Ea79e38009A0D548Bd7538cCb2467FD9',
                'role': 'FRIGORIFICO',
                'blockchain_roles': ['FRIGORIFICO_ROLE'],
                'email': 'frigorifico@dao.com',
                'first_name': 'Frigorífico',
                'last_name': 'DAO',
                'is_verified': False,
                'is_blockchain_active': True,
            },
            'iot_dao': {
                'wallet_address': '0xAFb91F92eC68F0eCa3cB98760C7e6171Dea38b53',
                'role': 'IOT',
                'blockchain_roles': ['IOT_ROLE'],
                'email': 'iot@dao.com',
                'first_name': 'Dispositivo',
                'last_name': 'IoT',
                'is_verified': False,
                'is_blockchain_active': True,
            },
        }

        User = get_user_model()
        verbosity = options.get('verbosity', 1)

        for username, user_data in dao_users.items():
            wallet_address = user_data.pop('wallet_address')
            blockchain_roles = user_data.pop('blockchain_roles')

            # Intentar obtener el usuario por wallet_address (campo único)
            # Usamos update_or_create en el campo único 'wallet_address'
            user, created = User.objects.update_or_create(
                wallet_address__iexact=wallet_address, # Busca ignorando mayúsculas/minúsculas
                defaults={
                    'username': username, # Se actualiza el username también por si acaso
                    'wallet_address': wallet_address.lower(), # Guardar en minúsculas
                    **user_data
                }
            )

            # Marcar la contraseña como "no utilizable". Esto es clave.
            # Esto evita que puedan iniciar sesión con user/password tradicional.
            if created:
                user.set_unusable_password()
                user.save()

            # Sincronizar los roles de blockchain (asegurarse de que solo tiene los definidos)
            current_roles = set(user.blockchain_roles)
            defined_roles = set(blockchain_roles)
            
            # Añadir los que faltan
            for role in (defined_roles - current_roles):
                user.add_blockchain_role(role)
            # Eliminar los que sobran (por si se cambió la definición)
            for role in (current_roles - defined_roles):
                user.remove_blockchain_role(role)

            action = "Creado" if created else "Actualizado"
            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(f'{action} usuario {user.username} ({user.wallet_short}) con roles: {", ".join(user.blockchain_roles)}')
                )

        if verbosity >= 1:
            self.stdout.write(self.style.SUCCESS('Semilla de usuarios DAO completada con éxito.'))