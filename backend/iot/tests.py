from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cattle.models import Cattle
from iot.models import Device, SensorData
from iot.forms import DeviceForm
from datetime import datetime, timedelta

User = get_user_model()

class IoTViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='farmer',
            password='testpass123',
            email='farmer@example.com',
            user_type='farmer'
        )
        self.other_user = User.objects.create_user(
            username='otherfarmer',
            password='testpass123',
            email='other@example.com',
            user_type='farmer'
        )
        
        # Crear ganado para el usuario principal
        self.cattle = Cattle.objects.create(
            ear_tag_id='FARMER001',
            name='My Cow',
            breed='Angus',
            gender='female',
            date_of_birth='2020-01-01',
            weight=450.50,
            owner=self.user
        )
        
        # Crear ganado para otro usuario
        self.other_cattle = Cattle.objects.create(
            ear_tag_id='OTHER001',
            name='Other Cow',
            breed='Hereford',
            gender='male',
            date_of_birth='2019-05-15',
            weight=600.75,
            owner=self.other_user
        )
        
        # Crear dispositivos
        self.device = Device.objects.create(
            device_id='DEV001',
            device_type='sensor',
            cattle=self.cattle,
            status='active',
            description='Temperature sensor'
        )
        
        self.other_device = Device.objects.create(
            device_id='DEV002',
            device_type='tracker',
            cattle=self.other_cattle,
            status='active',
            description='GPS tracker'
        )
        
        # Crear datos de sensor
        self.sensor_data = SensorData.objects.create(
            device=self.device,
            timestamp=datetime.now() - timedelta(hours=1),
            temperature=38.5,
            heart_rate=65,
            movement=12.3456
        )

    def test_device_list_view(self):
        """Test para listado de dispositivos"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('iot:device_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'iot/device_list.html')
        
        # Verificar que solo muestra los dispositivos del usuario autenticado
        devices_in_context = list(response.context['devices'])
        self.assertEqual(len(devices_in_context), 1)
        self.assertEqual(devices_in_context[0], self.device)
        self.assertNotIn(self.other_device, devices_in_context)

    def test_add_device_view_get(self):
        """Test para GET del formulario de añadir dispositivo"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('iot:add_device'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'iot/device_form.html')
        self.assertIsInstance(response.context['form'], DeviceForm)
        
        # Verificar que el queryset de cattle está filtrado por el usuario
        cattle_queryset = response.context['form'].fields['cattle'].queryset
        self.assertEqual(list(cattle_queryset), [self.cattle])

    def test_add_device_view_post_success(self):
        """Test para añadir dispositivo exitosamente"""
        self.client.login(username='farmer', password='testpass123')
        
        data = {
            'device_id': 'NEWDEV001',
            'device_type': 'feeder',
            'cattle': self.cattle.id,
            'status': 'active',
            'description': 'Automatic feeder'
        }
        response = self.client.post(reverse('iot:add_device'), data)
        
        # Debería redireccionar al detalle del nuevo dispositivo
        new_device = Device.objects.get(device_id='NEWDEV001')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('iot:device_detail', args=[new_device.id]))
        
        # Verificar que el dispositivo fue creado con el cattle correcto
        self.assertEqual(new_device.cattle, self.cattle)

    def test_sensor_data_view(self):
        """Test para listado de datos de sensores"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('iot:sensor_data'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'iot/sensor_data.html')
        
        # Verificar que solo muestra datos de sensores del usuario autenticado
        sensor_data_in_context = list(response.context['sensor_data'])
        self.assertEqual(len(sensor_data_in_context), 1)
        self.assertEqual(sensor_data_in_context[0], self.sensor_data)

    def test_api_sensor_data_authenticated(self):
        """Test para API de datos de sensores (autenticado)"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('iot:api_sensor_data'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Verificar la estructura de la respuesta JSON
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['temperature'], '38.50')

    def test_api_sensor_data_unauthenticated(self):
        """Test para API de datos de sensores (no autenticado) - debe dar 403"""
        response = self.client.get(reverse('iot:api_sensor_data'))
        self.assertEqual(response.status_code, 403)