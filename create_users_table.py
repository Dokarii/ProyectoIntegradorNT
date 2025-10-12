#!/usr/bin/env python3
"""
Script para crear la tabla de usuarios en la base de datos MySQL
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.database_manager import DatabaseManager

def create_users_table():
    """Crea la tabla de usuarios en la base de datos"""
    db = DatabaseManager()
    
    try:
        # Conectar a la base de datos
        if db.connect():
            print("✅ Conexión exitosa a la base de datos")
            
            # Crear tabla de usuarios
            create_table_query = """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                edad INT,
                genero ENUM('masculino', 'femenino', 'otro') DEFAULT 'otro',
                ubicacion VARCHAR(100),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT TRUE,
                INDEX idx_email (email),
                INDEX idx_username (username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cursor = db.connection.cursor()
            cursor.execute(create_table_query)
            db.connection.commit()
            cursor.close()
            
            print("✅ Tabla 'usuarios' creada exitosamente")
            
            # Verificar que la tabla se creó
            cursor = db.connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'usuarios'")
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                print("✅ Verificación: La tabla 'usuarios' existe en la base de datos")
            else:
                print("❌ Error: La tabla 'usuarios' no se pudo crear")
                
        else:
            print("❌ Error al conectar con la base de datos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    create_users_table()