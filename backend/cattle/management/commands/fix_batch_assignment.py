# management/commands/fix_batch_assignment.py
from django.core.management.base import BaseCommand
from cattle.models import Batch, Animal

class Command(BaseCommand):
    help = 'Corregir asignación de animales entre batches'
    
    def handle(self, *args, **options):
        # Encontrar el batch que tiene los 2 animales (debería ser el batch real)
        batch_with_animals = None
        for batch in Batch.objects.all():
            if batch.animals.count() == 2:
                batch_with_animals = batch
                break
        
        if not batch_with_animals:
            self.stdout.write(self.style.ERROR('❌ No se encontró batch con 2 animales'))
            return
            
        # Verificar que los animales son 10 y 11
        animal_ids = list(batch_with_animals.animals.values_list('token_id', flat=True))
        self.stdout.write(f"📊 Batch {batch_with_animals.id} tiene animales: {animal_ids}")
        
        # El batch con animales debería ser el "Batch 1" (principal)
        if batch_with_animals.name != "Batch 1 - Blockchain":
            self.stdout.write(f"🔄 Renombrando batch {batch_with_animals.id} a 'Batch 1 - Blockchain'")
            batch_with_animals.name = "Batch 1 - Blockchain"
            batch_with_animals.save()
        
        # Los batches vacíos pueden quedar como "Batch 2" y "Batch 3"
        empty_batches = Batch.objects.filter(animals__isnull=True).distinct()
        for i, batch in enumerate(empty_batches, 2):
            expected_name = f"Batch {i} - Blockchain"
            if batch.name != expected_name:
                self.stdout.write(f"🔄 Renombrando batch {batch.id} a '{expected_name}'")
                batch.name = expected_name
                batch.save()
        
        self.stdout.write(self.style.SUCCESS('✅ Asignación corregida'))
        
        # Verificación final
        self.stdout.write("\n📊 ESTADO FINAL:")
        for batch in Batch.objects.all().order_by('id'):
            self.stdout.write(f"Batch {batch.id}: {batch.name}")
            self.stdout.write(f"   Animales: {batch.animals.count()}")
            self.stdout.write(f"   Estado: {batch.status}")
            self.stdout.write("-" * 30)