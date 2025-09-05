from unittest.mock import patch, MagicMock

def mock_web3():
    """Mock para Web3 - importado dentro de funciones"""
    # Web3 se importa DENTRO de las funciones, no en el módulo
    return patch('core.views.HealthCheckView.get.Web3', MagicMock())  # ← Ruta específica

def mock_psutil():
    """Mock para psutil"""
    return patch.multiple('core.views.psutil',
        virtual_memory=MagicMock(return_value=MagicMock(percent=50.0)),
        cpu_percent=MagicMock(return_value=25.0),
        disk_usage=MagicMock(return_value=MagicMock(percent=60.0)),
        net_connections=MagicMock(return_value=[])
    )

def mock_database():
    """Mock para base de datos"""
    return patch('django.db.connection.cursor', MagicMock())

def mock_apps_get_model():
    """Mock para apps.get_model - maneja el parámetro require_ready"""
    mock_model = MagicMock()
    mock_model.objects.count.return_value = 100
    mock_model.objects.filter.return_value.count.return_value = 80
    
    def side_effect(model_name, require_ready=False):  # ← AÑADIR require_ready
        return mock_model
    
    return patch('django.apps.apps.get_model', side_effect=side_effect)