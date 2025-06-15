from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    path('home-data/', HomeDataView.as_view(), name='home_data'),
    
    path('mascotas/create/', MascotaCreateView.as_view(), name='mascotas-create'),
    path('mascotas/list/', MascotaListView.as_view(), name='mascotas-list'),
    path('mascotas/<int:mascota_id>/', MascotaUpdateDeleteView.as_view(), name='mascotas-update-delete'),

    path('citas/create/', CitaCreateView.as_view(), name='citas-create'),
    path('citas/list/', CitaListView.as_view(), name='citas-list'),
    path('citas/detail/<int:id>/', CitaDetailView.as_view(), name='cita-detail'),
    path('citas/<int:id>/', CitaUpdateDeleteView.as_view(), name='citas-update-delete'),
    
    path('content/generate/', ProcesarMensajeIAView.as_view(), name='generate-content'),
]
