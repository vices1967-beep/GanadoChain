from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    path('assign-role/', views.AssignRoleView.as_view(), name='assign-role'),
    path('mint-nft/', views.MintNFTView.as_view(), name='mint-nft'),
    path('register-animal/', views.RegisterAnimalView.as_view(), name='register-animal'),
    path('check-role/', views.CheckRoleView.as_view(), name='check-role'),
    path('mint-tokens/', views.MintTokensView.as_view(), name='mint-tokens'),
    path('update-health/', views.UpdateHealthView.as_view(), name='update-health'),
    path('iot-health-data/', views.IoTHealthDataView.as_view(), name='iot-health-data'),
    path('animal-history/<int:animal_id>/', views.AnimalHistoryView.as_view(), name='animal-history'),
    path('create-batch/', views.BatchCreateView.as_view(), name='create-batch'),
]