#!/usr/bin/env python3
"""
Script de inicialización de la base de datos MySQL para la Plataforma de Bienestar Emocional.
Este script crea la base de datos y todas las tablas necesarias.
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('config.env')

def create_database():
    """Crea la base de datos si no existe."""
    try:
        # Conectar sin especificar base de datos
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306))
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Crear base de datos
            db_name = os.getenv('DB_NAME', 'bienestaremocional')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Base de datos '{db_name}' creada o verificada")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Error creando base de datos: {e}")
        return False

def create_tables():
    """Crea todas las tablas necesarias."""
    try:
        # Conectar a la base de datos específica
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'bienestaremocional'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306)),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Tabla de usuarios
            create_usuarios_table = """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                edad INT,
                genero ENUM('masculino', 'femenino', 'otro') DEFAULT 'otro',
                ubicacion VARCHAR(100),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT TRUE,
                INDEX idx_email (email),
                INDEX idx_username (username),
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Tabla de encuestas
            create_surveys_table = """
            CREATE TABLE IF NOT EXISTS surveys (
                id INT AUTO_INCREMENT PRIMARY KEY,
                survey_id VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                estimated_duration INT DEFAULT 10,
                INDEX idx_survey_id (survey_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Tabla de preguntas
            create_questions_table = """
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question_id VARCHAR(50) NOT NULL,
                survey_id VARCHAR(50) NOT NULL,
                text TEXT NOT NULL,
                question_type ENUM('multiple_choice', 'likert_scale', 'open_text', 'number') NOT NULL,
                category VARCHAR(50) DEFAULT 'general',
                scale_min INT,
                scale_max INT,
                options JSON,
                question_order INT DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_question_id (question_id),
                INDEX idx_survey_id (survey_id),
                FOREIGN KEY (survey_id) REFERENCES surveys(survey_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Tabla de respuestas de encuestas
            create_survey_responses_table = """
            CREATE TABLE IF NOT EXISTS survey_responses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                response_id VARCHAR(50) UNIQUE NOT NULL,
                user_id VARCHAR(50) NOT NULL,
                survey_id VARCHAR(50) NOT NULL,
                completion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes FLOAT DEFAULT 0.0,
                is_complete BOOLEAN DEFAULT TRUE,
                INDEX idx_response_id (response_id),
                INDEX idx_user_id (user_id),
                INDEX idx_survey_id (survey_id),
                INDEX idx_completion_time (completion_time),
                FOREIGN KEY (survey_id) REFERENCES surveys(survey_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Tabla de respuestas individuales
            create_question_answers_table = """
            CREATE TABLE IF NOT EXISTS question_answers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                response_id VARCHAR(50) NOT NULL,
                question_id VARCHAR(50) NOT NULL,
                answer_value TEXT,
                answer_numeric INT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_response_id (response_id),
                INDEX idx_question_id (question_id),
                FOREIGN KEY (response_id) REFERENCES survey_responses(response_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Ejecutar creación de tablas
            tables = [
                ("usuarios", create_usuarios_table),
                ("surveys", create_surveys_table),
                ("questions", create_questions_table),
                ("survey_responses", create_survey_responses_table),
                ("question_answers", create_question_answers_table)
            ]
            
            for table_name, create_sql in tables:
                cursor.execute(create_sql)
                print(f"✅ Tabla '{table_name}' creada o verificada")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print("\n🎉 ¡Base de datos inicializada correctamente!")
            return True
            
    except Error as e:
        print(f"❌ Error creando tablas: {e}")
        return False

def verify_connection():
    """Verifica la conexión a la base de datos."""
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
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ Conectado a MySQL versión: {version[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📊 Tablas encontradas: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal."""
    print("🚀 Inicializando base de datos MySQL para Plataforma de Bienestar Emocional")
    print("=" * 70)
    
    # Verificar configuración
    print("📋 Configuración:")
    print(f"   Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"   Base de datos: {os.getenv('DB_NAME', 'bienestaremocional')}")
    print(f"   Usuario: {os.getenv('DB_USER', 'root')}")
    print(f"   Puerto: {os.getenv('DB_PORT', 3306)}")
    print()
    
    # Crear base de datos
    if not create_database():
        print("❌ No se pudo crear la base de datos")
        return False
    
    # Crear tablas
    if not create_tables():
        print("❌ No se pudieron crear las tablas")
        return False
    
    # Verificar conexión final
    print("\n🔍 Verificando conexión final...")
    if verify_connection():
        print("\n✅ ¡Base de datos lista para usar!")
        return True
    else:
        print("\n❌ Error en la verificación final")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
