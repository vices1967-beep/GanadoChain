# management/commands/correct_batch_final.py
from django.core.management.base import BaseCommand
from cattle.models import Batch

class Command(BaseCommand):
    help = 'Corrección FINAL: El batch con animales debe ser el Batch 3'
    
    def handle(self, *args, **options):
        # 1. Encontrar el batch que tiene los animales (debe ser el Batch 3)
        batch_with_animals = Batch.objects.filter(animals__isnull=False).first()
        
        if not batch_with_animals:
            self.stdout.write(self.style.ERROR('❌ No se encontró batch con animales'))
            return
        
        # 2. Si el batch con animales NO es el ID 3, necesitamos corregirlo
        if batch_with_animals.id != 3:
            self.stdout.write(f"🔄 El batch con animales es el ID {batch_with_animals.id}, pero debe ser el ID 3")
            
            # Buscar el batch con ID 3 (debe estar vacío)
            batch_3 = Batch.objects.filter(id=3).first()
            
            if batch_3 and batch_3.animals.count() == 0:
                # 3. Mover los animales del batch actual al batch 3
                animals_to_move = list(batch_with_animals.animals.all())
                
                for animal in animals_to_move:
                    batch_with_animals.animals.remove(animal)
                    batch_3.animals.add(animal)
                
                self.stdout.write(f"✅ Animales movidos del batch {batch_with_animals.id} al batch 3")
                
                # 4. Renombrar los batches correctamente
                batch_with_animals.name = f"Batch {batch_with_animals.id} - Blockchain (Vacío)"
                batch_with_animals.save()
                
                batch_3.name = "Batch 3 - Blockchain"
                batch_3.save()
                
                self.stdout.write("✅ Batches renombrados correctamente")
            else:
                self.stdout.write(self.style.ERROR('❌ El batch 3 no existe o no está vacío'))
                return
        else:
            # 5. Si ya es el batch 3, solo asegurar el nombre
            if batch_with_animals.name != "Batch 3 - Blockchain":
                batch_with_animals.name = "Batch 3 - Blockchain"
                batch_with_animals.save()
                self.stdout.write("✅ Batch 3 renombrado correctamente")
        
        # 6. Verificación final
        self.stdout.write("\n📊 ESTADO FINAL CORREGIDO:")
        for batch in Batch.objects.all().order_by('id'):
            animal_ids = list(batch.animals.values_list('token_id', flat=True))
            self.stdout.write(f"Batch {batch.id}: {batch.name}")
            self.stdout.write(f"   Animales: {animal_ids}")
            self.stdout.write(f"   Estado: {batch.status}")
            self.stdout.write("-" * 40)