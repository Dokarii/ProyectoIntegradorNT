#!/usr/bin/env python3
"""
Script de debug para probar el registro de usuarios directamente
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.user_manager_db import UserManagerDB

def test_user_registration():
    """Probar el registro de usuarios directamente"""
    print("🔍 Iniciando prueba de registro de usuarios...")
    
    try:
        # Crear instancia del UserManagerDB
        user_manager = UserManagerDB()
        print("✅ UserManagerDB creado exitosamente")
        
        # Datos de prueba
        user_data = {
            'nombre': 'Juan Pérez',
            'username': 'juanperez',
            'email': 'juan@test.com',
            'password': 'password123',
            'edad': 22,
            'genero': 'masculino',
            'ubicacion': 'Bogotá'
        }
        
        print(f"📝 Intentando registrar usuario: {user_data}")
        
        # Intentar registrar usuario
        success, message, user = user_manager.register_user(user_data)
        
        if success:
            print(f"✅ Usuario registrado exitosamente!")
            print(f"   ID: {user.user_id}")
            print(f"   Nombre: {user.nombre}")
            print(f"   Email: {user.email}")
        else:
            print(f"❌ Error en el registro: {message}")
            
    except Exception as e:
        print(f"💥 Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_registration()