import factory
from django.contrib.auth import get_user_model
from users.models import UserActivityLog, UserPreference, APIToken, Notification
from users.reputation_models import UserRole, ReputationScore

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    wallet_address = factory.Sequence(lambda n: f'0x{n:040x}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'PRODUCER'

class UserActivityLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserActivityLog
    
    user = factory.SubFactory(UserFactory)
    action = 'LOGIN'
    ip_address = '127.0.0.1'

class UserPreferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserPreference
    
    user = factory.SubFactory(UserFactory)

class APITokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = APIToken
    
    user = factory.SubFactory(UserFactory)
    name = factory.Faker('word')
    token = factory.Faker('sha256')
    token_type = 'READ'

class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification
    
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence')
    message = factory.Faker('text')
    notification_type = 'HEALTH_ALERT'

class UserRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserRole
    
    user = factory.SubFactory(UserFactory)
    role_type = 'PRODUCER_ROLE'

class ReputationScoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReputationScore
    
    user = factory.SubFactory(UserFactory)
    reputation_type = 'PRODUCER'
    score = 85.5