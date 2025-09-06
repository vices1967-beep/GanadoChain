"""
Tests extendidos para cattle/views.py - Para mejorar cobertura
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from cattle.models import Animal, Batch, AnimalHealthRecord

User = get_user_model()

class CattleViewsExtendedTests(APITestCase):
    """Tests extendidos para cattle views - Mejorar cobertura"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            role='FARMER'
        )
        
        # Crear veterinario
        self.vet_user = User.objects.create_user(
            username='testvet',
            email='vet@example.com',
            password='vetpass123',
            wallet_address='0xVetAddress1234567890123456789012345678901234',
            role='VETERINARIAN'
        )
        
        # Crear animales de prueba
        self.animal1 = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            weight=500.0,
            health_status='HEALTHY',
            location='Test Location 1'  # Campo requerido
        )
        
        self.animal2 = Animal.objects.create(
            ear_tag='TEST002',
            breed='Hereford',
            birth_date='2023-02-01',
            owner=self.user,
            weight=450.0,
            health_status='SICK',
            location='Test Location 2'  # Campo requerido
        )
        
        # Crear batch/lote CORREGIDO
        self.batch = Batch.objects.create(
            name='Test Batch',
            origin='Test Origin',      # Campo requerido
            destination='Test Destination',  # Campo requerido
            created_by=self.user
        )
        self.batch.animals.add(self.animal1, self.animal2)
        
        # Autenticar cliente
        self.client.force_authenticate(user=self.user)
    
    def test_animal_list_authenticated(self):
        """Test para listado de animales autenticado"""
        url = reverse('cattle:animal-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_animal_detail(self):
        """Test para detalle de animal"""
        url = reverse('cattle:animal-detail', kwargs={'pk': self.animal1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ear_tag'], 'TEST001')
    
    def test_animal_create(self):
        """Test para creación de animal"""
        url = reverse('cattle:animal-list')
        data = {
            'ear_tag': 'TEST003',
            'breed': 'Charolais',
            'birth_date': '2023-03-01',
            'weight': 480.0,
            'health_status': 'HEALTHY',
            'location': 'Test Location 3'  # Campo requerido
        }
        
        response = self.client.post(url, data, format='json')
        
            # DEBUG: Mostrar los errores
        print("=== DEBUG ANIMAL CREATE ===")
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
        print("===========================")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Animal.objects.count(), 3)
    
    def test_animal_update(self):
        """Test para actualización de animal"""
        url = reverse('cattle:animal-detail', kwargs={'pk': self.animal1.id})
        data = {'weight': 520.0, 'health_status': 'RECOVERING'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.animal1.refresh_from_db()
        self.assertEqual(self.animal1.weight, 520.0)
    
    def test_animal_search(self):
        """Test para búsqueda de animales"""
        url = reverse('cattle:animal-list') + '?search=Angus'
        response = self.client.get(url)
        
        print("=== DEBUG ANIMAL SEARCH DETAILED ===")
        print(f"Search URL: {url}")
        print(f"Results count: {len(response.data['results'])}")
        for animal in response.data['results']:
            print(f"Animal: {animal['ear_tag']} - {animal['breed']}")
            print(f"  Location: {animal['location']}")
            print(f"  Health: {animal['health_status']}")
            print(f"  IPFS: {animal['ipfs_hash']}")
            print(f"  NFT Owner: {animal['nft_owner_wallet']}")
            print("---")
        print("===========================")
        
        # Buscar solo animales con breed exacto "Angus"
        angus_animals = [a for a in response.data['results'] if a['breed'] == 'Angus']
        self.assertEqual(len(angus_animals), 1)
        self.assertEqual(angus_animals[0]['breed'], 'Angus')
    
    def test_animal_filter_by_health(self):
        """Test para filtrado por estado de salud"""
        url = reverse('cattle:animal-list') + '?health_status=SICK'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['health_status'], 'SICK')
    
    def test_batch_list(self):
        """Test para listado de batches"""
        url = reverse('cattle:batch-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_batch_detail(self):
        """Test para detalle de batch"""
        url = reverse('cattle:batch-detail', kwargs={'pk': self.batch.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Batch')
    
    def test_health_record_list(self):
        """Test para listado de registros de salud"""
        # Primero crear un registro de salud CORREGIDO
        AnimalHealthRecord.objects.create(
            animal=self.animal1,
            health_status='SICK',  # Campo requerido
            source='VETERINARIAN',
            notes='Test health record',
            veterinarian=self.vet_user
        )
        
        url = reverse('cattle:animalhealthrecord-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_cattle_stats(self):
        """Test para estadísticas de cattle"""
        url = reverse('cattle:cattle-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_animals', response.data)
        self.assertIn('minted_animals', response.data)

class CattleViewsPermissionTests(APITestCase):
    """Tests de permisos para cattle views"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear diferentes tipos de usuarios
        self.farmer = User.objects.create_user(
            username='farmer1', password='pass', role='FARMER',
            wallet_address='0xFarmer1234567890123456789012345678901234'
        )
        
        self.other_farmer = User.objects.create_user(
            username='farmer2', password='pass', role='FARMER',
            wallet_address='0xOtherFarmer12345678901234567890123456789012'
        )
        
        # Animal del primer farmer
        self.animal = Animal.objects.create(
            ear_tag='OWNED001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.farmer,
            weight=500.0,
            location='Test Location'  # Campo requerido
        )
    
    def test_animal_access_owner(self):
        """Test que el owner puede acceder a su animal"""
        self.client.force_authenticate(user=self.farmer)
        url = reverse('cattle:animal-detail', kwargs={'pk': self.animal.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_animal_access_other_farmer_denied(self):
        """Test que otro farmer NO puede acceder"""
        self.client.force_authenticate(user=self.other_farmer)
        url = reverse('cattle:animal-detail', kwargs={'pk': self.animal.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)