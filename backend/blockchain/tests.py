from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cattle.models import Cattle
from blockchain.models import Block, Transaction
from blockchain.forms import TransactionForm
from datetime import datetime

User = get_user_model()

class BlockchainViewsTestCase(TestCase):
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
        
        # Crear bloques y transacciones
        self.block = Block.objects.create(
            index=1,
            timestamp=datetime.now(),
            previous_hash='0' * 64,
            hash='a' * 64,
            nonce=12345,
            merkle_root='b' * 64
        )
        
        self.transaction = Transaction.objects.create(
            block=self.block,
            transaction_hash='tx1' * 21,  # 64 caracteres
            transaction_type='health',
            cattle=self.cattle,
            data={'diagnosis': 'Healthy', 'action': 'Routine checkup'},
            timestamp=datetime.now(),
            created_by=self.user
        )

    def test_transaction_list_view(self):
        """Test para listado de transacciones"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('blockchain:transaction_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blockchain/transaction_list.html')
        
        # Verificar que solo muestra transacciones del usuario autenticado
        transactions_in_context = list(response.context['transactions'])
        self.assertEqual(len(transactions_in_context), 1)
        self.assertEqual(transactions_in_context[0], self.transaction)

    def test_add_transaction_view_get(self):
        """Test para GET del formulario de añadir transacción"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('blockchain:add_transaction'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blockchain/transaction_form.html')
        self.assertIsInstance(response.context['form'], TransactionForm)
        
        # Verificar que el queryset de cattle está filtrado por el usuario
        cattle_queryset = response.context['form'].fields['cattle'].queryset
        self.assertEqual(list(cattle_queryset), [self.cattle])

    def test_add_transaction_view_post_success(self):
        """Test para añadir transacción exitosamente"""
        self.client.login(username='farmer', password='testpass123')
        
        data = {
            'transaction_type': 'health',
            'cattle': self.cattle.id,
            'data': '{"diagnosis": "New diagnosis", "treatment": "Medication"}'
        }
        response = self.client.post(reverse('blockchain:add_transaction'), data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('blockchain:transaction_list'))
        
        # Verificar que la transacción fue creada con los datos correctos
        new_transaction = Transaction.objects.filter(cattle=self.cattle).latest('id')
        self.assertEqual(new_transaction.transaction_type, 'health')
        self.assertEqual(new_transaction.created_by, self.user)

    def test_blockchain_view(self):
        """Test para visualización de la blockchain"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('blockchain:blockchain_view'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blockchain/blockchain.html')
        
        # Verificar que muestra los bloques
        blocks_in_context = list(response.context['blocks'])
        self.assertEqual(len(blocks_in_context), 1)
        self.assertEqual(blocks_in_context[0], self.block)

    def test_api_verify_data_authenticated_valid(self):
        """Test para API de verificación (autenticado, hash válido)"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(
            reverse('blockchain:api_verify_data') + f'?hash={self.transaction.transaction_hash}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Verificar la respuesta de verificación exitosa
        data = response.json()
        self.assertTrue(data['verified'])
        self.assertEqual(data['transaction'], self.transaction.transaction_hash)

    def test_api_verify_data_authenticated_invalid(self):
        """Test para API de verificación (autenticado, hash inválido)"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(
            reverse('blockchain:api_verify_data') + '?hash=invalidhash'
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Verificar la respuesta de verificación fallida
        data = response.json()
        self.assertFalse(data['verified'])

    def test_api_blockchain_data_public(self):
        """Test para API de datos de blockchain (pública)"""
        response = self.client.get(reverse('blockchain:api_blockchain_data'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Verificar la estructura de la respuesta JSON
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['index'], 1)
        self.assertEqual(data[0]['hash'], 'a' * 64)