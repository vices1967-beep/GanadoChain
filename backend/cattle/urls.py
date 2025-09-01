from django.urls import path
from . import views

app_name = 'cattle'

urlpatterns = [
    path('animals/', views.AnimalListCreateView.as_view(), name='animal_list_create'),
    path('animals/<int:pk>/', views.AnimalDetailView.as_view(), name='animal_detail'),
    path('animals/<int:pk>/mint-nft/', views.mint_animal_nft, name='animal_mint_nft'),
    path('animals/<int:pk>/verify-nft/', views.verify_animal_nft, name='animal_verify_nft'),
    path('animals/<int:pk>/nft-info/', views.get_animal_nft_info, name='animal_nft_info'),
    path('batches/', views.BatchListCreateView.as_view(), name='batch_list_create'),
    path('batches/<int:pk>/', views.BatchDetailView.as_view(), name='batch_detail'),
]