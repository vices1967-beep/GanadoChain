# backend/iot/management/commands/sync_iot_blockchain.py
from django.core.management.base import BaseCommand
from iot.multichain_models import IoTDeviceMultichain, SensorDataMultichain

class Command(BaseCommand):
    help = 'Sincronizar datos IoT con blockchain'
    
    def add_arguments(self, parser):
        parser.add_argument('--devices', action='store_true', help='Sincronizar dispositivos')
        parser.add_argument('--data', action='store_true', help='Sincronizar datos de sensores')
        parser.add_argument('--network', type=str, default='STARKNET_SEPOLIA', help='Red blockchain a usar')
    
    def handle(self, *args, **options):
        network_id = options['network']
        
        if options['devices']:
            self.sync_devices(network_id)
        
        if options['data']:
            self.sync_sensor_data(network_id)
    
    def sync_devices(self, network_id):
        """Sincronizar dispositivos no registrados"""
        devices = IoTDeviceMultichain.objects.filter(blockchain_registered=False)
        
        self.stdout.write(f'Sincronizando {devices.count()} dispositivos...')
        
        for device in devices:
            adapter = IoTDeviceMultichainAdapter(device)
            result = adapter.register_on_blockchain(network_id)
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f'✅ {device.device_id} registrado'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ {device.device_id}: {result["error"]}'))
    
    def sync_sensor_data(self, network_id):
        """Sincronizar datos de sensores no almacenados"""
        sensor_data = SensorDataMultichain.objects.filter(stored_on_blockchain=False)[:100]  # Límite por ejecución
        
        self.stdout.write(f'Sincronizando {sensor_data.count()} registros de sensores...')
        
        for data in sensor_data:
            adapter = SensorDataMultichainAdapter(data)
            result = adapter.store_on_blockchain([network_id])
            
            if any(r['success'] for r in result.values()):
                self.stdout.write(self.style.SUCCESS(f'✅ Datos {data.id} almacenados'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Datos {data.id} no almacenados'))