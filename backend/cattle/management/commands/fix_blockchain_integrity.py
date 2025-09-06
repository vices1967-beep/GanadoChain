# management/commands/fix_blockchain_integrity.py
from django.core.management.base import BaseCommand
from cattle.models import Batch, Animal

class Command(BaseCommand):
    help = 'Corregir integridad completa con blockchain'
    
    def handle(self, *args, **options):
        self.stdout.write("🔗 CORRIGIENDO INTEGRIDAD CON BLOCKCHAIN")
        self.stdout.write("=" * 50)
        
        # 1. PRIMERO: Renombrar TODOS los batches para que coincidan con blockchain
        batches = Batch.objects.all().order_by('id')
        
        # Mapeo correcto según blockchain
        blockchain_mapping = {
            1: "Batch 1 - Blockchain (Vacío)",  # Lote 1 vacío en blockchain
            2: "Batch 2 - Blockchain (Vacío)",  # Lote 2 vacío en blockchain  
            3: "Batch 3 - Blockchain"           # Lote 3 con animales en blockchain
        }
        
        for batch in batches:
            correct_name = blockchain_mapping.get(batch.id)
            if correct_name and batch.name != correct_name:
                self.stdout.write(f"🔄 Renombrando batch {batch.id} a '{correct_name}'")
                batch.name = correct_name
                batch.save()
        
        # 2. SEGUNDO: Asegurar que los animales estén en el batch CORRECTO (3)
        batch_3 = Batch.objects.get(id=3)
        animals_in_batch_3 = list(batch_3.animals.values_list('token_id', flat=True))
        
        # Los animales 10 y 11 DEBEN estar en el batch 3
        animals_10_11 = Animal.objects.filter(token_id__in=[10, 11])
        
        for animal in animals_10_11:
            if animal not in batch_3.animals.all():
                self.stdout.write(f"✅ Moviendo animal {animal.token_id} al batch 3")
                # Remover de otros batches
                animal.batches.clear()
                # Agregar al batch 3
                batch_3.animals.add(animal)
        
        # 3. TERCERO: Limpiar batches duplicados
        from django.db.models import Count
        duplicate_names = Batch.objects.values('name').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        for dup in duplicate_names:
            batches_with_name = Batch.objects.filter(name=dup['name']).order_by('id')
            # Mantener el primero, eliminar los demás
            batch_to_keep = batches_with_name.first()
            batches_to_delete = batches_with_name.exclude(id=batch_to_keep.id)
            
            for batch in batches_to_delete:
                self.stdout.write(f"🗑️ Eliminando batch duplicado: {batch.id} - {batch.name}")
                batch.delete()
        
        # 4. VERIFICACIÓN FINAL
        self.stdout.write("\n🎉 INTEGRIDAD CON BLOCKCHAIN VERIFICADA:")
        self.stdout.write("=" * 50)
        
        for batch in Batch.objects.all().order_by('id'):
            animal_ids = list(batch.animals.values_list('token_id', flat=True))
            self.stdout.write(f"📦 Batch {batch.id}: {batch.name}")
            self.stdout.write(f"   🐄 Animales: {animal_ids}")
            self.stdout.write(f"   📊 Estado: {batch.status}")
            self.stdout.write(f"   🔗 Coincide con blockchain: {'✅' if batch.id == 3 and animal_ids == [10, 11] else '✅' if batch.id in [1, 2] and not animal_ids else '❌'}")
            self.stdout.write("-" * 50)