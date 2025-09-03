from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cattle.models import Cattle

User = get_user_model()

class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            user_type='farmer'
        )
        # Crear ganado de prueba
        self.cattle = Cattle.objects.create(
            ear_tag_id='TEST001',
            name='Test Cow',
            breed='Angus',
            gender='female',
            date_of_birth='2020-01-01',
            weight=450.50,
            owner=self.user
        )

    def test_home_view(self):
        """Test para la vista home (pública)"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertContains(response, 'GanadoChain')

    def test_dashboard_view_authenticated(self):
        """Test para dashboard con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')
        self.assertContains(response, 'Dashboard')

    def test_dashboard_view_unauthenticated(self):
        """Test para dashboard redirecciona si no autenticado"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirección a login
        self.assertRedirects(response, f'/users/login/?next={reverse("core:dashboard")}')

    def test_dashboard_context_data(self):
        """Test que verifica los datos de contexto del dashboard"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        # Verificar que el contexto contiene los datos esperados
        self.assertIn('cattle_count', response.context)
        self.assertIn('recent_cattle', response.context)
        self.assertIn('recent_health', response.context)
        
        # Verificar valores específicos
        self.assertEqual(response.context['cattle_count'], 1)
        self.assertEqual(len(response.context['recent_cattle']), 1)