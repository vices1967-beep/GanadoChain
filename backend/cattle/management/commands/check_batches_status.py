# management/commands/check_batches_status.py
from django.core.management.base import BaseCommand
from cattle.models import Batch

class Command(BaseCommand):
    help = 'Verificar estado actual de los batches en la base de datos'
    
    def handle(self, *args, **options):
        batches = Batch.objects.all().order_by('id')
        
        if not batches.exists():
            self.stdout.write(self.style.WARNING('⚠️ No hay batches en la base de datos'))
            return
            
        self.stdout.write("📊 ESTADO ACTUAL DE BATCHES:")
        self.stdout.write("=" * 50)
        
        for batch in batches:
            self.stdout.write(f"Batch {batch.id}: {batch.name}")
            self.stdout.write(f"   Estado: {batch.status}")
            self.stdout.write(f"   Animales: {batch.animals.count()}")
            self.stdout.write(f"   IPFS Hash: {batch.ipfs_hash}")
            self.stdout.write("-" * 30)