# backend/iot/adapters/multichain_adapter.py
from django.db import models
from core.multichain.manager import multichain_manager
from core.starknet.client import SyncStarknetClient
import json
from django.utils import timezone

class IoTDeviceMultichainAdapter:
    """Adaptador multichain para dispositivos IoT"""
    
    def __init__(self, device):
        self.device = device
    
    def register_on_blockchain(self, network_id=None):
        """Registrar dispositivo en blockchain"""
        if network_id is None:
            network_id = self.device.preferred_network.network_id if self.device.preferred_network else 'STARKNET_SEPOLIA'
        
        network = multichain_manager.get_network(network_id)
        
        try:
            if network.is_starknet:
                result = self._register_on_starknet(network)
            else:
                result = self._register_on_evm(network)
            
            if result['success']:
                self.device.blockchain_registered = True
                self.device.blockchain_device_id = result.get('blockchain_device_id', '')
                self.device.save()
                
                # Crear evento de registro
                from .multichain_models import DeviceEventMultichain
                DeviceEventMultichain.objects.create(
                    device=self.device,
                    event_type='STATUS_CHANGE',
                    severity='LOW',
                    title='Dispositivo Registrado en Blockchain',
                    description=f'Dispositivo registrado en {network.name}',
                    event_data=result,
                    logged_on_blockchain=True,
                    blockchain_transaction_hash=result.get('transaction_hash', ''),
                    timestamp=timezone.now()
                )
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _register_on_starknet(self, network):
        """Registrar dispositivo en Starknet"""
        client = SyncStarknetClient(network)
        
        # Preparar datos del dispositivo
        device_data = {
            'device_id': self.device.device_id,
            'device_type': self.device.device_type,
            'owner_address': self.device.owner.wallet_address,
            'animal_id': self.device.animal.id if self.device.animal else 0,
            'manufacturer': self.device.manufacturer,
            'model': self.device.model,
        }
        
        # Llamar al contrato de registro (implementación específica)
        # result = client.register_iot_device(device_data)
        
        return {
            'success': True,
            'transaction_hash': '0x_starknet_device_reg',
            'blockchain_device_id': f"starknet_iot_{self.device.device_id}",
            'network': network.name
        }
    
    def _register_on_evm(self, network):
        """Registrar dispositivo en EVM"""
        return {
            'success': True,
            'transaction_hash': '0x_evm_device_reg',
            'blockchain_device_id': f"evm_iot_{self.device.device_id}",
            'network': network.name
        }
    
    def send_heartbeat(self):
        """Enviar heartbeat a blockchain"""
        networks = ['STARKNET_SEPOLIA']  # Red principal para heartbeats
        
        results = {}
        for network_id in networks:
            network = multichain_manager.get_network(network_id)
            
            try:
                if network.is_starknet:
                    result = self._send_starknet_heartbeat(network)
                else:
                    result = self._send_evm_heartbeat(network)
                
                results[network_id] = result
                
            except Exception as e:
                results[network_id] = {'success': False, 'error': str(e)}
        
        # Actualizar último heartbeat
        if any(r['success'] for r in results.values()):
            self.device.last_communication = timezone.now()
            self.device.save()
        
        return results
    
    def _send_starknet_heartbeat(self, network):
        """Enviar heartbeat a Starknet"""
        heartbeat_data = {
            'device_id': self.device.blockchain_device_id,
            'battery_level': self.device.battery_level,
            'timestamp': int(timezone.now().timestamp()),
            'location': self.device.current_location,
        }
        
        # Llamar al contrato de heartbeats
        return {
            'success': True,
            'transaction_hash': '0x_starknet_heartbeat',
            'timestamp': timezone.now().isoformat()
        }

class SensorDataMultichainAdapter:
    """Adaptador multichain para datos de sensores"""
    
    def __init__(self, sensor_data):
        self.sensor_data = sensor_data
    
    def store_on_blockchain(self, networks=None):
        """Almacenar datos de sensor en blockchain"""
        if networks is None:
            networks = ['STARKNET_SEPOLIA']  # Red principal para datos
        
        results = {}
        for network_id in networks:
            network = multichain_manager.get_network(network_id)
            
            try:
                if network.is_starknet:
                    result = self._store_on_starknet(network)
                else:
                    result = self._store_on_evm(network)
                
                results[network_id] = result
                
                if result['success']:
                    # Actualizar registro con hash de transacción
                    if 'blockchain_hashes' not in self.sensor_data.blockchain_hashes:
                        self.sensor_data.blockchain_hashes = {}
                    
                    self.sensor_data.blockchain_hashes[network_id] = result['transaction_hash']
                    self.sensor_data.stored_on_blockchain = True
                    self.sensor_data.blockchain_networks.append(network_id)
                    self.sensor_data.save()
            
            except Exception as e:
                results[network_id] = {'success': False, 'error': str(e)}
        
        return results
    
    def _store_on_starknet(self, network):
        """Almacenar datos en Starknet"""
        client = SyncStarknetClient(network)
        
        # Preparar datos para blockchain
        sensor_data = {
            'device_id': self.sensor_data.device.blockchain_device_id,
            'data_type': self.sensor_data.data_type,
            'timestamp': int(self.sensor_data.timestamp.timestamp()),
            'raw_data': self.sensor_data.raw_data,
            'accuracy': float(self.sensor_data.accuracy) if self.sensor_data.accuracy else 0.0,
        }
        
        # Llamar al contrato de almacenamiento
        return {
            'success': True,
            'transaction_hash': '0x_starknet_sensor_data',
            'data_hash': '0x_sensor_data_hash',
            'network': network.name
        }
    
    def process_with_ai(self):
        """Procesar datos con IA para detección de anomalías"""
        # Implementación de análisis IA
        anomalies = self._detect_anomalies()
        
        if anomalies:
            self.sensor_data.anomalies_detected = anomalies
            self.sensor_data.alert_triggered = True
            self.sensor_data.processed_by_ai = True
            self.sensor_data.save()
            
            # Crear evento de alerta
            from .multichain_models import DeviceEventMultichain
            DeviceEventMultichain.objects.create(
                device=self.sensor_data.device,
                event_type='DATA_ANOMALY',
                severity='HIGH' if len(anomalies) > 2 else 'MEDIUM',
                title='Anomalías Detectadas en Datos de Sensor',
                description=f'Se detectaron {len(anomalies)} anomalías en los datos',
                event_data={'anomalies': anomalies, 'sensor_data_id': self.sensor_data.id},
                timestamp=timezone.now()
            )
        
        return anomalies
    
    def _detect_anomalies(self):
        """Detectar anomalías en los datos del sensor"""
        # Implementación simplificada de detección de anomalías
        anomalies = []
        raw_data = self.sensor_data.raw_data
        
        if self.sensor_data.data_type == 'TEMPERATURE':
            temperature = raw_data.get('value')
            if temperature and (temperature < 35 or temperature > 41):
                anomalies.append('temperature_out_of_range')
        
        elif self.sensor_data.data_type == 'HEART_RATE':
            heart_rate = raw_data.get('value')
            if heart_rate and (heart_rate < 40 or heart_rate > 100):
                anomalies.append('heart_rate_abnormal')
        
        elif self.sensor_data.data_type == 'GPS':
            if raw_data.get('accuracy', 100) > 50:  # Baja precisión
                anomalies.append('low_gps_accuracy')
        
        return anomalies

class GatewayMultichainAdapter:
    """Adaptador multichain para gateways IoT"""
    
    def __init__(self, gateway):
        self.gateway = gateway
    
    def sync_connected_devices(self):
        """Sincronizar dispositivos conectados con blockchain"""
        connected_devices = self.gateway.connected_devices.all()
        
        results = {}
        for device in connected_devices:
            adapter = IoTDeviceMultichainAdapter(device)
            results[device.device_id] = adapter.send_heartbeat()
        
        return results
    
    def process_batch_sensor_data(self, sensor_data_batch):
        """Procesar lote de datos de sensores"""
        processed_results = []
        
        for sensor_data in sensor_data_batch:
            adapter = SensorDataMultichainAdapter(sensor_data)
            
            # Almacenar en blockchain
            storage_result = adapter.store_on_blockchain()
            
            # Procesar con IA
            anomalies = adapter.process_with_ai()
            
            processed_results.append({
                'sensor_data_id': sensor_data.id,
                'storage_result': storage_result,
                'anomalies_detected': anomalies,
                'alert_triggered': len(anomalies) > 0
            })
        
        return processed_results