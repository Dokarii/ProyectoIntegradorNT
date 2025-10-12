#!/usr/bin/env python3
"""
Script para verificar que los usuarios se están guardando en la base de datos MySQL
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.database_manager import DatabaseManager

def test_users_in_database():
    """Verifica si hay usuarios registrados en la base de datos"""
    db = DatabaseManager()
    
    try:
        # Conectar a la base de datos
        if db.connect():
            print("✅ Conexión exitosa a la base de datos")
            
            # Consultar usuarios
            cursor = db.connection.cursor()
            cursor.execute("SELECT * FROM usuarios")
            users = cursor.fetchall()
            cursor.close()
            
            if users:
                print(f"\n📊 Se encontraron {len(users)} usuarios en la base de datos:")
                print("-" * 80)
                for user in users:
                    print(f"ID: {user[0]}")
                    print(f"Nombre: {user[1]}")
                    print(f"Username: {user[2]}")
                    print(f"Email: {user[3]}")
                    print(f"Edad: {user[5]}")
                    print(f"Género: {user[6]}")
                    print(f"Ubicación: {user[7]}")
                    print(f"Fecha registro: {user[8]}")
                    print("-" * 80)
            else:
                print("\n❌ No se encontraron usuarios en la base de datos")
                
        else:
            print("❌ Error al conectar con la base de datos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    test_users_in_database()