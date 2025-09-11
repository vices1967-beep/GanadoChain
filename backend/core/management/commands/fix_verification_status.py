from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Pone is_verified=False en los usuarios del DAO hasta que se verifiquen on-chain'

    def handle(self, *args, **options):
        User = get_user_model()
        dao_wallets = [
            '0xFdA1b969c9e33910F221326f70A661C517d16f90',
            '0x59eBcf4d12350D804F0d773b522b30d1Bf38ac6a',
            '0x4eE2a4e9ca534D35b7745d42FcF84677cb3ee97a',
            '0x41174B08Ea79e38009A0D548Bd7538cCb2467FD9',
            '0xAFb91F92eC68F0eCa3cB98760C7e6171Dea38b53'
        ]

        # Poner is_verified=False para los usuarios del DAO
        updated_count = User.objects.filter(wallet_address__in=dao_wallets).update(is_verified=False)

        self.stdout.write(
            self.style.SUCCESS(f'Se actualizaron {updated_count} usuarios. is_verified establecido a False.')
        )