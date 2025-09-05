"""
Tests simplificados para la aplicación core - Versión que evita problemas complejos
"""
import os
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from core.metrics_models import SystemMetrics

# Configurar variable de entorno para testing
os.environ['TESTING'] = 'True'

User = get_user_model()

class CoreModelsTests(TestCase):
    """Tests básicos para los modelos"""
    
    def test_create_system_metrics(self):
        """Test para crear métricas del sistema"""
        metrics = SystemMetrics.objects.create(
            date=timezone.now().date(),
            total_animals=100,
            total_users=10,
            total_transactions=50,
            active_devices=5,
            average_gas_price=30.5
        )
        self.assertEqual(metrics.total_animals, 100)
        self.assertEqual(metrics.total_users, 10)

class CoreBasicViewsTests(APITestCase):
    """Tests básicos para vistas simples"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            wallet_address='0x742d35cc6634c0532925a3b844bc454e4438f44e'
        )
    
    def test_api_info_view(self):
        """Test para APIInfoView"""
        url = reverse('api-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_home_view(self):
        """Test para home view"""
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_system_config_view_unauthenticated(self):
        """Test para SystemConfigView sin autenticación"""
        url = reverse('system-config')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('django.conf.settings')
    def test_system_config_view_authenticated(self, mock_settings):
        """Test para SystemConfigView con usuario autenticado"""
        mock_settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        mock_settings.BLOCKCHAIN_CHAIN_ID = 80002
        
        url = reverse('system-config')
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class SystemMetricsTests(APITestCase):
    """Tests específicos para métricas del sistema"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            wallet_address='0x742d35cc6634c0532925a3b844bc454e4438f44e'
        )
        
        # Crear métricas
        self.metrics = SystemMetrics.objects.create(
            date=timezone.now().date(),
            total_animals=100,
            total_users=10,
            total_transactions=50
        )
    
    def test_system_metrics_list_view_authenticated(self):
        """Test para listar métricas"""
        url = reverse('metrics-list')
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_system_metrics_latest_view(self):
        """Test para obtener la última métrica"""
        url = reverse('metrics-latest')
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# Tests de utilidad
class UtilityTests(TestCase):
    """Tests de utilidad varios"""
    
    def test_string_representation(self):
        """Test para representación en string de modelos"""
        metric = SystemMetrics(
            date=timezone.now().date(),
            total_animals=100
        )
        self.assertIn(str(metric.date), str(metric))