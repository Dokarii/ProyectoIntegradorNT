"""
Gestor de base de datos MySQL para la Plataforma de Bienestar Emocional.
"""

import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('config.env')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Clase para gestionar todas las operaciones de base de datos MySQL."""
    
    def __init__(self, host: str = None, database: str = None, 
                 user: str = None, password: str = None, port: int = None):
        """
        Inicializa el gestor de base de datos.
        Usa variables de entorno si no se proporcionan parámetros.
        
        Args:
            host: Servidor de base de datos
            database: Nombre de la base de datos
            user: Usuario de MySQL
            password: Contraseña de MySQL
            port: Puerto de MySQL
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.database = database or os.getenv('DB_NAME', 'bienestaremocional')
        self.user = user or os.getenv('DB_USER', 'root')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.port = port or int(os.getenv('DB_PORT', 3306))
        self.connection = None
        
    def connect(self) -> bool:
        """
        Establece conexión con la base de datos.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            
            if self.connection.is_connected():
                logger.info(f"✅ Conectado a MySQL: {self.database}")
                return True
                
        except Error as e:
            logger.error(f"❌ Error conectando a MySQL: {e}")
            return False
            
    def disconnect(self):
        """Cierra la conexión con la base de datos."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("🔌 Desconectado de MySQL")
            
    def get_statistics(self) -> Dict[str, int]:
        """
        Obtiene estadísticas generales del sistema.
        
        Returns:
            Dict[str, int]: Estadísticas del sistema
        """
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            # Contar usuarios únicos
            cursor.execute("SELECT COUNT(DISTINCT user_id) as total_users FROM survey_responses")
            users_result = cursor.fetchone()
            total_users = users_result['total_users'] if users_result else 0
            
            # Contar encuestas
            cursor.execute("SELECT COUNT(*) as total_surveys FROM surveys")
            surveys_result = cursor.fetchone()
            total_surveys = surveys_result['total_surveys'] if surveys_result else 0
            
            # Contar respuestas totales
            cursor.execute("SELECT COUNT(*) as total_responses FROM survey_responses")
            responses_result = cursor.fetchone()
            total_responses = responses_result['total_responses'] if responses_result else 0
            
            # Contar respuestas de hoy
            cursor.execute("""
                SELECT COUNT(*) as responses_today 
                FROM survey_responses 
                WHERE DATE(completion_time) = CURDATE()
            """)
            today_result = cursor.fetchone()
            responses_today = today_result['responses_today'] if today_result else 0
            
            cursor.close()
            
            return {
                'total_users': total_users,
                'total_surveys': total_surveys,
                'total_responses': total_responses,
                'responses_today': responses_today
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_users': 0,
                'total_surveys': 0,
                'total_responses': 0,
                'responses_today': 0
            }
            
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """
        Ejecuta una consulta que no retorna datos (INSERT, UPDATE, DELETE).
        
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
            
        Returns:
            bool: True si la consulta fue exitosa
        """
        try:
            # Verificar y restablecer conexión si es necesario
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    logger.error("❌ No se pudo establecer conexión con la base de datos")
                    return False
                    
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            logger.error(f"❌ Error ejecutando consulta: {e}")
            if self.connection:
                self.connection.rollback()
            return False
            
    def fetch_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Ejecuta una consulta que retorna datos (SELECT).
        
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
            
        Returns:
            List[Dict]: Lista de resultados como diccionarios
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
            
        except Error as e:
            logger.error(f"❌ Error en consulta SELECT: {e}")
            return []
            
    # === OPERACIONES DE USUARIOS ===
    
    def create_user(self, user_id: str, name: str, email: str = None) -> bool:
        """Crea un nuevo usuario."""
        query = """
        INSERT INTO users (id, name, email, registration_date, is_active)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, name, email, datetime.now(), True)
        return self.execute_query(query, params)
        
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Obtiene un usuario por ID."""
        query = "SELECT * FROM users WHERE id = %s"
        results = self.fetch_query(query, (user_id,))
        return results[0] if results else None
        
    def get_all_users(self) -> List[Dict]:
        """Obtiene todos los usuarios."""
        query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY registration_date DESC"
        return self.fetch_query(query)
        
    # === OPERACIONES DE ENCUESTAS ===
    
    def create_survey(self, survey_id: str, title: str, description: str, 
                     estimated_duration: int = 10) -> bool:
        """Crea una nueva encuesta."""
        query = """
        INSERT INTO surveys (survey_id, title, description, created_date, is_active, estimated_duration)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (survey_id, title, description, datetime.now(), True, estimated_duration)
        return self.execute_query(query, params)
        
    def get_survey(self, survey_id: str) -> Optional[Dict]:
        """Obtiene una encuesta por ID."""
        query = "SELECT * FROM surveys WHERE survey_id = %s AND is_active = TRUE"
        results = self.fetch_query(query, (survey_id,))
        return results[0] if results else None
        
    def get_all_surveys(self) -> List[Dict]:
        """Obtiene todas las encuestas activas."""
        query = "SELECT * FROM surveys WHERE is_active = TRUE ORDER BY created_date DESC"
        return self.fetch_query(query)
        
    # === OPERACIONES DE PREGUNTAS ===
    
    def create_question(self, question_id: str, survey_id: str, text: str, 
                       question_type: str, category: str, scale_min: int = None,
                       scale_max: int = None, options: List[str] = None, 
                       question_order: int = 0) -> bool:
        """Crea una nueva pregunta."""
        query = """
        INSERT INTO questions (question_id, survey_id, text, question_type, category, 
                              scale_min, scale_max, options, question_order)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        options_json = json.dumps(options) if options else None
        params = (question_id, survey_id, text, question_type, category, 
                 scale_min, scale_max, options_json, question_order)
        return self.execute_query(query, params)
        
    def get_survey_questions(self, survey_id: str) -> List[Dict]:
        """Obtiene todas las preguntas de una encuesta."""
        query = """
        SELECT * FROM questions 
        WHERE survey_id = %s 
        ORDER BY question_order, question_id
        """
        results = self.fetch_query(query, (survey_id,))
        
        # Convertir options de JSON string a lista
        for result in results:
            if result.get('options'):
                try:
                    result['options'] = json.loads(result['options'])
                except:
                    result['options'] = []
                    
        return results
        
    # === OPERACIONES DE RESPUESTAS ===
    
    def create_survey_response(self, response_id: str, user_id: str, survey_id: str,
                              duration_minutes: float = 0.0) -> bool:
        """Crea una nueva respuesta de encuesta."""
        query = """
        INSERT INTO survey_responses (response_id, user_id, survey_id, completion_time, 
                                    duration_minutes, is_complete)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (response_id, user_id, survey_id, datetime.now(), duration_minutes, True)
        return self.execute_query(query, params)
        
    def create_question_answer(self, response_id: str, question_id: str, 
                              answer_value: str, answer_numeric: int = None) -> bool:
        """Crea una respuesta individual a una pregunta."""
        query = """
        INSERT INTO question_answers (response_id, question_id, answer_value, answer_numeric)
        VALUES (%s, %s, %s, %s)
        """
        params = (response_id, question_id, answer_value, answer_numeric)
        return self.execute_query(query, params)
        
    def get_user_responses(self, user_id: str) -> List[Dict]:
        """Obtiene todas las respuestas de un usuario."""
        query = """
        SELECT sr.*, s.title as survey_title
        FROM survey_responses sr
        JOIN surveys s ON sr.survey_id = s.survey_id
        WHERE sr.user_id = %s
        ORDER BY sr.completion_time DESC
        """
        return self.fetch_query(query, (user_id,))
        
    def get_response_answers(self, response_id: str) -> List[Dict]:
        """Obtiene todas las respuestas individuales de una respuesta de encuesta."""
        query = """
        SELECT qa.*, q.text as question_text, q.category
        FROM question_answers qa
        JOIN questions q ON qa.question_id = q.question_id
        WHERE qa.response_id = %s
        ORDER BY q.question_order
        """
        return self.fetch_query(query, (response_id,))
        
    # === ESTADÍSTICAS ===
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas generales del sistema."""
        stats = {}
        
        # Total usuarios registrados
        query = "SELECT COUNT(*) as count FROM users WHERE is_active = TRUE"
        result = self.fetch_query(query)
        stats['usuarios_registrados'] = result[0]['count'] if result else 0
        
        # Total encuestas completadas
        query = "SELECT COUNT(*) as count FROM survey_responses WHERE is_complete = TRUE"
        result = self.fetch_query(query)
        stats['encuestas_completadas'] = result[0]['count'] if result else 0
        
        # Total encuestas disponibles
        query = "SELECT COUNT(*) as count FROM surveys WHERE is_active = TRUE"
        result = self.fetch_query(query)
        stats['encuestas_disponibles'] = result[0]['count'] if result else 0
        
        return stats
        
    def get_survey_analytics(self, survey_id: str) -> Dict[str, Any]:
        """Obtiene análisis detallado de una encuesta."""
        query = """
        SELECT 
            COUNT(*) as total_responses,
            AVG(duration_minutes) as avg_duration,
            MIN(completion_time) as first_response,
            MAX(completion_time) as last_response
        FROM survey_responses 
        WHERE survey_id = %s AND is_complete = TRUE
        """
        
        result = self.fetch_query(query, (survey_id,))
        return result[0] if result else {}