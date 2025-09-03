from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cattle.models import Cattle, HealthRecord
from cattle.forms import CattleForm, HealthRecordForm
from datetime import date, timedelta

User = get_user_model()

class CattleViewsTestCase(TestCase):
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
        
        # Crear registro de salud
        self.health_record = HealthRecord.objects.create(
            cattle=self.cattle,
            veterinarian=self.user,
            record_date=date.today() - timedelta(days=10),
            diagnosis='Routine checkup',
            treatment='Vaccination',
            vaccination=True,
            vaccination_date=date.today() - timedelta(days=10)
        )

    def test_cattle_list_view(self):
        """Test para listado de ganado"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:cattle_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cattle/cattle_list.html')
        
        # Verificar que solo muestra el ganado del usuario autenticado
        cattle_in_context = list(response.context['cattle'])
        self.assertEqual(len(cattle_in_context), 1)
        self.assertEqual(cattle_in_context[0], self.cattle)
        self.assertNotIn(self.other_cattle, cattle_in_context)

    def test_cattle_detail_view_owner(self):
        """Test para detalle de ganado (propietario)"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:cattle_detail', args=[self.cattle.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cattle/cattle_detail.html')
        self.assertEqual(response.context['cattle'], self.cattle)
        
        # Verificar que incluye registros de salud
        self.assertIn('health_records', response.context)
        self.assertEqual(len(response.context['health_records']), 1)

    def test_cattle_detail_view_not_owner(self):
        """Test para detalle de ganado (no propietario) - debe dar 404"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:cattle_detail', args=[self.other_cattle.id]))
        
        self.assertEqual(response.status_code, 404)

    def test_add_cattle_view_get(self):
        """Test para GET del formulario de añadir ganado"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:add_cattle'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cattle/cattle_form.html')
        self.assertIsInstance(response.context['form'], CattleForm)

    def test_add_cattle_view_post_success(self):
        """Test para añadir ganado exitosamente"""
        self.client.login(username='farmer', password='testpass123')
        
        data = {
            'ear_tag_id': 'NEW001',
            'name': 'New Cow',
            'breed': 'Jersey',
            'gender': 'male',
            'date_of_birth': '2021-03-15',
            'weight': 300.25,
            'status': 'active'
        }
        response = self.client.post(reverse('cattle:add_cattle'), data)
        
        # Debería redireccionar al detalle del nuevo animal
        new_cattle = Cattle.objects.get(ear_tag_id='NEW001')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cattle:cattle_detail', args=[new_cattle.id]))
        
        # Verificar que el animal fue creado con el owner correcto
        self.assertEqual(new_cattle.owner, self.user)

    def test_edit_cattle_view_get_owner(self):
        """Test para GET del formulario de edición (propietario)"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:edit_cattle', args=[self.cattle.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cattle/cattle_form.html')
        self.assertIsInstance(response.context['form'], CattleForm)

    def test_edit_cattle_view_get_not_owner(self):
        """Test para GET del formulario de edición (no propietario) - debe dar 404"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:edit_cattle', args=[self.other_cattle.id]))
        
        self.assertEqual(response.status_code, 404)

    def test_edit_cattle_view_post_success(self):
        """Test para editar ganado exitosamente"""
        self.client.login(username='farmer', password='testpass123')
        
        data = {
            'ear_tag_id': 'FARMER001',
            'name': 'Updated Cow Name',
            'breed': 'Angus',
            'gender': 'female',
            'date_of_birth': '2020-01-01',
            'weight': 480.00,  # Peso actualizado
            'status': 'active'
        }
        response = self.client.post(reverse('cattle:edit_cattle', args=[self.cattle.id]), data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cattle:cattle_detail', args=[self.cattle.id]))
        
        # Verificar que los datos fueron actualizados
        updated_cattle = Cattle.objects.get(id=self.cattle.id)
        self.assertEqual(updated_cattle.name, 'Updated Cow Name')
        self.assertEqual(updated_cattle.weight, 480.00)

    def test_delete_cattle_view_get_owner(self):
        """Test para GET de confirmación de eliminación (propietario)"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:delete_cattle', args=[self.cattle.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cattle/cattle_confirm_delete.html')
        self.assertEqual(response.context['cattle'], self.cattle)

    def test_delete_cattle_view_get_not_owner(self):
        """Test para GET de confirmación de eliminación (no propietario) - debe dar 404"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:delete_cattle', args=[self.other_cattle.id]))
        
        self.assertEqual(response.status_code, 404)

    def test_delete_cattle_view_post_success(self):
        """Test para eliminar ganado exitosamente"""
        self.client.login(username='farmer', password='testpass123')
        
        response = self.client.post(reverse('cattle:delete_cattle', args=[self.cattle.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cattle:cattle_list'))
        
        # Verificar que el animal fue eliminado
        self.assertFalse(Cattle.objects.filter(id=self.cattle.id).exists())

    def test_health_records_view(self):
        """Test para listado de registros de salud"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:health_records', args=[self.cattle.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cattle/health_records.html')
        self.assertEqual(response.context['cattle'], self.cattle)
        self.assertEqual(len(response.context['records']), 1)

    def test_add_health_record_view_get(self):
        """Test para GET del formulario de añadir registro de salud"""
        self.client.login(username='farmer', password='testpass123')
        response = self.client.get(reverse('cattle:add_health_record', args=[self.cattle.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cattle/health_record_form.html')
        self.assertIsInstance(response.context['form'], HealthRecordForm)

    def test_add_health_record_view_post_success(self):
        """Test para añadir registro de salud exitosamente"""
        self.client.login(username='farmer', password='testpass123')
        
        data = {
            'record_date': date.today(),
            'diagnosis': 'New diagnosis',
            'treatment': 'New treatment',
            'medications': 'Antibiotics',
            'vaccination': True,
            'vaccination_date': date.today(),
            'next_checkup_date': date.today() + timedelta(days=30)
        }
        response = self.client.post(reverse('cattle:add_health_record', args=[self.cattle.id]), data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cattle:health_records', args=[self.cattle.id]))
        
        # Verificar que el registro fue creado con los datos correctos
        new_record = HealthRecord.objects.filter(cattle=self.cattle).latest('id')
        self.assertEqual(new_record.diagnosis, 'New diagnosis')
        self.assertEqual(new_record.veterinarian, self.user)