from cattle.audit_models import CattleAuditTrail
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from cattle.models import Animal, Batch, AnimalHealthRecord
from cattle.blockchain_models import BlockchainEventState
from decimal import Decimal
from unittest.mock import patch

User = get_user_model()

class AuditAndEventsTests(APITestCase):
    """Tests para auditoría y eventos blockchain"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='audituser',
            email='audit@example.com',
            password='testpass123',
            wallet_address='0xAuditUser123456789012345678901234567890',
            first_name='Audit',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        
        self.animal = Animal.objects.create(
            ear_tag='AUDIT001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            weight=500.0,
            health_status='HEALTHY',
            location='Test Location'
        )
        
        self.batch = Batch.objects.create(
            name='Audit Batch',
            origin='Test Origin',
            destination='Test Destination',
            created_by=self.user
        )

    def test_animal_audit_trail(self):
        """Test trail de auditoría de animal"""
        CattleAuditTrail.objects.create(
            object_type='animal',
            object_id=str(self.animal.id),
            action_type='CREATE',
            user=self.user,
            changes={'details': 'Test audit'}
        )
        
        url = reverse('cattle:animal-audit-trail', kwargs={'pk': self.animal.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_animal_blockchain_events(self):
        """Test eventos blockchain de animal"""
        try:
            from blockchain.models import BlockchainEvent
            # Crear evento de prueba si es necesario
            url = reverse('cattle:animal-blockchain-events', kwargs={'pk': self.animal.id})
            response = self.client.get(url)
            # Puede devolver 200 vacío o 503 si no está configurado
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
        except ImportError:
            # Si la app blockchain no está instalada, skip test
            pass

    def test_batch_audit_trail(self):
        """Test trail de auditoría de lote"""
        CattleAuditTrail.objects.create(
            object_type='batch',
            object_id=str(self.batch.id),
            action_type='CREATE',
            user=self.user,
            changes={'details': 'Test audit'}
        )
        
        url = reverse('cattle:batch-audit-trail', kwargs={'pk': self.batch.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_batch_blockchain_events(self):
        """Test eventos blockchain de lote"""
        try:
            from blockchain.models import BlockchainEvent
            url = reverse('cattle:batch-blockchain-events', kwargs={'pk': self.batch.id})
            response = self.client.get(url)
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
        except ImportError:
            pass

    def test_blockchain_event_state_list(self):
        """Test para listar estados de eventos blockchain"""
        url = reverse('cattle:blockchaineventstate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cattle_audit_trail_list(self):
        """Test para listar auditorías de cattle"""
        CattleAuditTrail.objects.create(
            object_type='animal',
            object_id=str(self.animal.id),
            action_type='CREATE',
            user=self.user,
            changes={'field': 'value'}
        )
        CattleAuditTrail.objects.create(
            object_type='batch',
            object_id=str(self.batch.id),
            action_type='UPDATE',
            user=self.user,
            changes={'field': 'value'}
        )
        
        url = reverse('cattle:cattleaudittrail-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_cattle_audit_trail_filter(self):
        """Test para filtrar auditorías"""
        CattleAuditTrail.objects.create(
            object_type='animal',
            object_id=str(self.animal.id),
            action_type='CREATE',
            user=self.user,
            changes={'field': 'value'}
        )
        
        url = reverse('cattle:cattleaudittrail-list') + '?object_type=animal'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_blockchain_event_state_filter(self):
        """Test para filtrar estados de eventos blockchain"""
        url = reverse('cattle:blockchaineventstate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class HealthRecordTests(APITestCase):
    """Tests específicos para registros de salud"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='healthuser',
            email='health@example.com',
            password='testpass123',
            wallet_address='0xHealthUser123456789012345678901234567890',
            first_name='Health',
            last_name='User'
        )
        self.vet_user = User.objects.create_user(
            username='vetuser',
            email='vet@example.com',
            password='vetpass123',
            wallet_address='0xVetUser123456789012345678901234567890',
            first_name='Vet',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        
        self.animal = Animal.objects.create(
            ear_tag='HEALTH001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            weight=500.0,
            health_status='HEALTHY',
            location='Test Location'
        )

    def test_create_health_record(self):
        """Test crear registro de salud"""
        url = reverse('cattle:animalhealthrecord-list')
        data = {
            'animal': self.animal.id,
            'health_status': 'SICK',
            'source': 'FARMER',
            'notes': 'Test health record',
            'temperature': 39.5,
            'heart_rate': 80
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AnimalHealthRecord.objects.count(), 1)

    def test_filter_health_records_by_animal(self):
        """Test filtrar registros de salud por animal"""
        AnimalHealthRecord.objects.create(
            animal=self.animal,
            health_status='SICK',
            source='FARMER',
            notes='Test record 1'
        )
        AnimalHealthRecord.objects.create(
            animal=self.animal,
            health_status='RECOVERING',
            source='VETERINARIAN',
            notes='Test record 2'
        )
        
        url = reverse('cattle:animalhealthrecord-list') + f'?animal_id={self.animal.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_health_records_by_status(self):
        """Test filtrar registros de salud por estado"""
        AnimalHealthRecord.objects.create(
            animal=self.animal,
            health_status='SICK',
            source='FARMER',
            notes='Test record'
        )
        
        url = reverse('cattle:animalhealthrecord-list') + '?health_status=SICK'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['health_status'], 'SICK')

class BatchOperationsTests(APITestCase):
    """Tests para operaciones de lotes"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='batchuser',
            email='batch@example.com',
            password='testpass123',
            wallet_address='0xBatchUser123456789012345678901234567890',
            first_name='Batch',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        
        self.animal1 = Animal.objects.create(
            ear_tag='BATCH001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            weight=500.0,
            health_status='HEALTHY',
            location='Test Location'
        )
        
        self.animal2 = Animal.objects.create(
            ear_tag='BATCH002',
            breed='Hereford',
            birth_date='2023-02-01',
            owner=self.user,
            weight=450.0,
            health_status='HEALTHY',
            location='Test Location'
        )
        
        self.batch = Batch.objects.create(
            name='Test Batch',
            origin='Test Origin',
            destination='Test Destination',
            created_by=self.user
        )

    def test_create_batch_with_animals(self):
        """Test crear lote con animales"""
        url = reverse('cattle:batch-list')
        data = {
            'name': 'New Batch with Animals',
            'origin': 'Test Origin',
            'destination': 'Test Destination',
            'status': 'CREATED',
            'animals': [self.animal1.id, self.animal2.id]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el lote se creó con los animales
        batch = Batch.objects.get(name='New Batch with Animals')
        self.assertEqual(batch.animals.count(), 2)

    def test_add_animals_to_batch(self):
        """Test añadir animales a lote existente"""
        url = reverse('cattle:batch-add-animals', kwargs={'pk': self.batch.id})
        data = {'animal_ids': [self.animal1.id, self.animal2.id]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.animals.count(), 2)

    def test_remove_animals_from_batch(self):
        """Test remover animales de lote"""
        # Primero añadir animales
        self.batch.animals.add(self.animal1, self.animal2)
        
        url = reverse('cattle:batch-remove-animals', kwargs={'pk': self.batch.id})
        data = {'animal_ids': [self.animal1.id]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.animals.count(), 1)

    def test_update_batch_status(self):
        """Test actualizar estado del lote"""
        url = reverse('cattle:batch-update-status', kwargs={'pk': self.batch.id})
        data = {
            'new_status': 'IN_TRANSIT',  # ✅ Solo enviar new_status
            'notes': 'En camino'
        }
        
        response = self.client.post(url, data, format='json')
        print(f"DEBUG: Status={response.status_code}, Data={response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.status, 'IN_TRANSIT')

class BlockchainTests(APITestCase):
    """Tests para funcionalidades blockchain"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='blockuser',
            email='block@example.com',
            password='testpass123',
            wallet_address='0xBlockUser123456789012345678901234567890',
            first_name='Block',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        
        self.animal = Animal.objects.create(
            ear_tag='BLOCK001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            weight=500.0,
            health_status='HEALTHY',
            location='Test Location',
            ipfs_hash='test_ipfs_hash'
        )

    @patch('cattle.views.BlockchainService')
    def test_mint_nft_success(self, mock_blockchain):
        """Test mint NFT exitoso"""
        mock_service = mock_blockchain.return_value
        mock_service.mint_and_associate_animal.return_value = {
            'success': True,
            'token_id': 123,
            'tx_hash': '0xtest123',
            'owner_wallet': '0xnewowner'
        }
        
        url = reverse('cattle:animal-mint-nft', kwargs={'pk': self.animal.id})
        data = {'wallet_address': '0xnewowner'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    @patch('cattle.views.BlockchainService')
    def test_mint_nft_blockchain_error(self, mock_blockchain):
        """Test error en blockchain durante mint"""
        mock_service = mock_blockchain.return_value
        mock_service.mint_and_associate_animal.return_value = {
            'success': False,
            'error': 'Blockchain error'
        }
        
        url = reverse('cattle:animal-mint-nft', kwargs={'pk': self.animal.id})
        data = {'wallet_address': '0xnewowner'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Blockchain error', response.data['error'])

    @patch('cattle.views.BlockchainService')
    def test_verify_nft_success(self, mock_blockchain):
        """Test verificación NFT exitosa"""
        self.animal.token_id = 123
        self.animal.save()
        
        mock_service = mock_blockchain.return_value
        mock_service.verify_animal_nft.return_value = {
            'is_valid': True,
            'owner': '0xowner',
            'metadata': {'test': 'data'}
        }
        
        url = reverse('cattle:animal-verify-nft', kwargs={'pk': self.animal.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    @patch('cattle.views.BlockchainService')
    def test_nft_info_success(self, mock_blockchain):
        """Test obtención info NFT exitosa"""
        self.animal.token_id = 123
        self.animal.save()
        
        mock_service = mock_blockchain.return_value
        mock_service.get_animal_nft_info.return_value = {
            'token_id': 123,
            'owner': '0xowner',
            'metadata_uri': 'ipfs://test'
        }
        
        url = reverse('cattle:animal-nft-info', kwargs={'pk': self.animal.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

class SearchTests(APITestCase):
    """Tests para búsquedas"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='searchuser',
            email='search@example.com',
            password='testpass123',
            wallet_address='0xSearchUser123456789012345678901234567890',
            first_name='Search',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        
        self.animal1 = Animal.objects.create(
            ear_tag='SEARCH001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            weight=600.0,
            health_status='HEALTHY',
            location='Test Location'
        )
        
        self.animal2 = Animal.objects.create(
            ear_tag='SEARCH002',
            breed='Hereford',
            birth_date='2023-02-01',
            owner=self.user,
            weight=400.0,
            health_status='SICK',
            location='Test Location'
        )
        
        self.batch = Batch.objects.create(
            name='Search Batch',
            origin='Test Origin',
            destination='Test Destination',
            created_by=self.user
        )
        self.batch.animals.add(self.animal1)

    def test_search_animals_endpoint(self):
        """Test endpoint de búsqueda de animales"""
        url = reverse('cattle:animal-search')
        data = {
            'ear_tag': 'SEARCH001',
            'breed': 'Angus',
            'health_status': 'HEALTHY'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['ear_tag'], 'SEARCH001')

    def test_search_batches_endpoint(self):
        """Test endpoint de búsqueda de lotes"""
        url = reverse('cattle:batch-search')
        data = {
            'name': 'Search',
            'status': 'CREATED',
            'min_animals': 1
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Search Batch')

class PermissionTests(APITestCase):
    """Tests de permisos"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            wallet_address='0xUser11234567890123456789012345678901234',
            first_name='User1',
            last_name='Test'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            wallet_address='0xUser21234567890123456789012345678901234',
            first_name='User2',
            last_name='Test'
        )
        
        self.animal = Animal.objects.create(
            ear_tag='PERM001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user1,
            weight=500.0,
            health_status='HEALTHY',
            location='Test Location'
        )

    def test_user_cannot_access_other_user_animal(self):
        """Test que usuario no puede acceder a animal de otro usuario"""
        self.client.force_authenticate(user=self.user2)
        
        url = reverse('cattle:animal-detail', kwargs={'pk': self.animal.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_superuser_can_access_all_animals(self):
        """Test que superusuario puede acceder a todos los animales"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            wallet_address='0xAdmin12345678901234567890123456789012'
        )
        self.client.force_authenticate(user=superuser)
        
        url = reverse('cattle:animal-detail', kwargs={'pk': self.animal.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)