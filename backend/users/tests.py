from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from users.forms import CustomUserCreationForm

User = get_user_model()

class UsersViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='existinguser',
            password='testpass123',
            email='existing@example.com',
            user_type='farmer'
        )

    def test_register_view_get(self):
        """Test para GET del formulario de registro"""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_register_view_post_success(self):
        """Test para registro exitoso"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'user_type': 'vet',
            'phone': '+1234567890'
        }
        response = self.client.post(reverse('users:register'), data)
        
        # Debería redireccionar al dashboard después del registro exitoso
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:dashboard'))
        
        # Verificar que el usuario fue creado
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_invalid(self):
        """Test para registro con datos inválidos"""
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'pass',
            'password2': 'pass',
            'user_type': 'invalid_type'
        }
        response = self.client.post(reverse('users:register'), data)
        
        # Debería mostrar el formulario con errores
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')
        self.assertFormError(response, 'form', 'user_type', 'Select a valid choice. invalid_type is not one of the available choices.')

    def test_login_view_get(self):
        """Test para GET del formulario de login"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_login_view_post_success(self):
        """Test para login exitoso"""
        data = {
            'username': 'existinguser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('users:login'), data)
        
        # Debería redireccionar al dashboard después del login exitoso
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_login_view_post_invalid(self):
        """Test para login con credenciales inválidas"""
        data = {
            'username': 'existinguser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('users:login'), data)
        
        # Debería mostrar el formulario con error
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', '__all__', 'Please enter a correct username and password. Note that both fields may be case-sensitive.')

    def test_logout_view(self):
        """Test para logout"""
        # Primero hacer login
        self.client.login(username='existinguser', password='testpass123')
        
        # Verificar que está autenticado
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Hacer logout
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:home'))
        
        # Verificar que ya no está autenticado
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirección a login

    def test_profile_view_get(self):
        """Test para GET del perfil de usuario"""
        self.client.login(username='existinguser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertEqual(response.context['user'], self.user)

    def test_profile_view_post_success(self):
        """Test para actualización exitosa del perfil"""
        self.client.login(username='existinguser', password='testpass123')
        
        data = {
            'username': 'existinguser',
            'email': 'updated@example.com',
            'user_type': 'vet',
            'phone': '+1234567890',
            'address': 'New Address 123'
        }
        response = self.client.post(reverse('users:profile'), data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:profile'))
        
        # Verificar que los datos fueron actualizados
        updated_user = User.objects.get(username='existinguser')
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.user_type, 'vet')