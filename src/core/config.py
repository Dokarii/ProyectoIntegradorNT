"""
Configuración de la base de datos para la Plataforma de Bienestar Emocional.
"""

import os
from typing import Dict

class DatabaseConfig:
    """Configuración de la base de datos MySQL."""
    
    # Configuración por defecto para desarrollo local
    DEFAULT_CONFIG = {
        'host': 'localhost',
        'database': 'bienestaremocional',
        'user': 'root',
        'password': '',  # Cambiar por tu contraseña de MySQL
        'port': 3306,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, str]:
        """
        Obtiene la configuración de base de datos.
        Prioriza variables de entorno sobre valores por defecto.
        
        Returns:
            Dict[str, str]: Configuración de base de datos
        """
        return {
            'host': os.getenv('DB_HOST', cls.DEFAULT_CONFIG['host']),
            'database': os.getenv('DB_NAME', cls.DEFAULT_CONFIG['database']),
            'user': os.getenv('DB_USER', cls.DEFAULT_CONFIG['user']),
            'password': os.getenv('DB_PASSWORD', cls.DEFAULT_CONFIG['password']),
            'port': int(os.getenv('DB_PORT', cls.DEFAULT_CONFIG['port'])),
            'charset': cls.DEFAULT_CONFIG['charset'],
            'collation': cls.DEFAULT_CONFIG['collation']
        }
    
    @classmethod
    def get_connection_string(cls) -> str:
        """
        Genera string de conexión para MySQL.
        
        Returns:
            str: String de conexión
        """
        config = cls.get_config()
        return f"mysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

# Configuración para diferentes entornos
ENVIRONMENTS = {
    'development': {
        'host': 'localhost',
        'database': 'bienestaremocional',
        'user': 'root',
        'password': '',
        'debug': True
    },
    'production': {
        'host': os.getenv('PROD_DB_HOST', 'localhost'),
        'database': os.getenv('PROD_DB_NAME', 'bienestaremocional'),
        'user': os.getenv('PROD_DB_USER', 'root'),
        'password': os.getenv('PROD_DB_PASSWORD', ''),
        'debug': False
    }
}

def get_environment_config(env: str = 'development') -> Dict:
    """
    Obtiene configuración según el entorno.
    
    Args:
        env: Entorno (development, production)
        
    Returns:
        Dict: Configuración del entorno
    """
    return ENVIRONMENTS.get(env, ENVIRONMENTS['development'])