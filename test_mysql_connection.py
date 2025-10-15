#!/usr/bin/env python3
"""
Script mejorado para verificar la conexión a MySQL y el estado de la base de datos.
"""

import sys
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('config.env')

def test_mysql_connection():
    """Prueba la conexión básica a MySQL."""
    print("🔌 Probando conexión básica a MySQL...")
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306))
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ Conexión exitosa a MySQL versión: {version[0]}")
            
            cursor.close()
            connection.close()
            return True
        else:
            print("❌ No se pudo establecer conexión")
            return False
            
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_database_exists():
    """Verifica si la base de datos existe."""
    print("\n📊 Verificando existencia de la base de datos...")
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306))
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            db_name = os.getenv('DB_NAME', 'bienestaremocional')
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            result = cursor.fetchone()
            
            if result:
                print(f"✅ Base de datos '{db_name}' existe")
                cursor.close()
                connection.close()
                return True
            else:
                print(f"❌ Base de datos '{db_name}' no existe")
                cursor.close()
                connection.close()
                return False
                
    except Error as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def test_database_connection():
    """Prueba la conexión a la base de datos específica."""
    print("\n🗄️ Probando conexión a la base de datos específica...")
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'bienestaremocional'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306))
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar tablas
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"✅ Conectado a la base de datos")
            print(f"📋 Tablas encontradas: {len(tables)}")
            
            expected_tables = ['usuarios', 'surveys', 'questions', 'survey_responses', 'question_answers']
            missing_tables = []
            
            for table in expected_tables:
                table_exists = any(table in str(t) for t in tables)
                if table_exists:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} (FALTANTE)")
                    missing_tables.append(table)
            
            cursor.close()
            connection.close()
            
            if missing_tables:
                print(f"\n⚠️ Tablas faltantes: {', '.join(missing_tables)}")
                return False
            else:
                print("\n✅ Todas las tablas están presentes")
                return True
                
    except Error as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False

def test_data_integrity():
    """Verifica la integridad de los datos."""
    print("\n🔍 Verificando integridad de datos...")
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'bienestaremocional'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306))
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Contar registros en cada tabla
            tables_to_check = ['usuarios', 'surveys', 'questions', 'survey_responses', 'question_answers']
            
            for table in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   📊 {table}: {count} registros")
                except Error as e:
                    print(f"   ❌ Error en tabla {table}: {e}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Error verificando integridad: {e}")
        return False

def show_configuration():
    """Muestra la configuración actual."""
    print("⚙️ Configuración actual:")
    print(f"   Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"   Base de datos: {os.getenv('DB_NAME', 'bienestaremocional')}")
    print(f"   Usuario: {os.getenv('DB_USER', 'root')}")
    print(f"   Puerto: {os.getenv('DB_PORT', 3306)}")
    print(f"   Contraseña: {'***' if os.getenv('DB_PASSWORD') else '(vacía)'}")

def main():
    """Función principal."""
    print("🔍 Verificador de Conexión MySQL - Plataforma de Bienestar Emocional")
    print("=" * 70)
    
    show_configuration()
    
    # Ejecutar todas las pruebas
    tests = [
        ("Conexión básica a MySQL", test_mysql_connection),
        ("Existencia de base de datos", test_database_exists),
        ("Conexión a base de datos", test_database_connection),
        ("Integridad de datos", test_data_integrity)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print('='*50)
        result = test_func()
        results.append((test_name, result))
    
    # Resumen final
    print(f"\n{'='*70}")
    print("📋 RESUMEN DE PRUEBAS")
    print('='*70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("\n🎉 ¡Todas las pruebas pasaron! La base de datos está lista.")
        return True
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa la configuración.")
        print("\n💡 Sugerencias:")
        print("   1. Verifica que MySQL esté ejecutándose")
        print("   2. Revisa las credenciales en config.env")
        print("   3. Ejecuta init_database.py para crear las tablas")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
