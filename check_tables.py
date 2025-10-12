#!/usr/bin/env python3
"""
Script para verificar las tablas existentes en la base de datos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.database_manager import DatabaseManager

def check_database_structure():
    """Verificar la estructura de la base de datos"""
    print("🔍 Verificando estructura de la base de datos...")
    
    try:
        # Crear instancia del DatabaseManager
        db_manager = DatabaseManager()
        
        if not db_manager.connect():
            print("❌ No se pudo conectar a la base de datos")
            return
            
        # Obtener lista de tablas
        cursor = db_manager.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"📋 Tablas encontradas en la base de datos:")
        for table in tables:
            table_name = table[0]
            print(f"   - {table_name}")
            
            # Mostrar estructura de cada tabla
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            print(f"     Columnas:")
            for column in columns:
                print(f"       • {column[0]} ({column[1]})")
            print()
        
        cursor.close()
        db_manager.disconnect()
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_structure()