from django.db.models.signals import Signal
from django.dispatch import receiver

# Señal para cambios de lote
animal_batch_changed = Signal()

@receiver(animal_batch_changed)
def handle_animal_batch_change(sender, **kwargs):
    """
    Maneja la lógica cuando un animal cambia de lote
    """
    animal = kwargs['animal']
    old_batch = kwargs['old_batch']
    new_batch = kwargs['new_batch']
    
    # Aquí puedes añadir lógica adicional como:
    # - Registrar en blockchain el cambio
    # - Crear registro de auditoría
    # - Enviar notificaciones
    # - Actualizar métricas