"""
Gestor de encuestas que utiliza base de datos MySQL.
Reemplaza el sistema de archivos por almacenamiento en base de datos.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from .database_manager import DatabaseManager
from .config import DatabaseConfig

class Survey:
    """Clase que representa una encuesta."""
    
    def __init__(self, survey_id: str, title: str, description: str, questions: List[Dict]):
        self.survey_id = survey_id
        self.title = title
        self.description = description
        self.questions = questions
        self.created_at = datetime.now()

class SurveyManagerDB:
    """
    Gestor de encuestas que utiliza base de datos MySQL.
    Maneja la creación, almacenamiento y recuperación de encuestas y respuestas.
    """
    
    def __init__(self):
        """Inicializa el gestor con conexión a base de datos."""
        self.db_manager = DatabaseManager()
        self._initialize_default_surveys()
    
    def _initialize_default_surveys(self):
        """Inicializa las encuestas por defecto si no existen."""
        try:
            # Asegurar conexión a la base de datos
            if not self.db_manager.connect():
                print("Error: No se pudo conectar a la base de datos para inicializar encuestas")
                return
                
            # Verificar si ya existen encuestas
            existing_surveys = self.db_manager.get_all_surveys()
            if not existing_surveys:
                self._create_default_surveys()
                
            # Cerrar conexión
            self.db_manager.disconnect()
        except Exception as e:
            print(f"Error inicializando encuestas por defecto: {e}")
    
    def _create_default_surveys(self):
        """Crea las encuestas por defecto en la base de datos."""
        
        # Encuesta de Estado Emocional
        emotional_survey = {
            'survey_id': 'emotional_state',
            'title': 'Evaluación de Estado Emocional',
            'description': 'Evalúa tu estado emocional actual',
            'questions': [
                {
                    'question_id': 'mood_today',
                    'text': '¿Cómo te sientes hoy?',
                    'type': 'scale',
                    'options': ['Muy mal', 'Mal', 'Regular', 'Bien', 'Muy bien'],
                    'scale_min': 1,
                    'scale_max': 5
                },
                {
                    'question_id': 'stress_level',
                    'text': '¿Cuál es tu nivel de estrés?',
                    'type': 'scale',
                    'options': ['Muy bajo', 'Bajo', 'Moderado', 'Alto', 'Muy alto'],
                    'scale_min': 1,
                    'scale_max': 5
                },
                {
                    'question_id': 'energy_level',
                    'text': '¿Cómo está tu nivel de energía?',
                    'type': 'scale',
                    'options': ['Muy bajo', 'Bajo', 'Normal', 'Alto', 'Muy alto'],
                    'scale_min': 1,
                    'scale_max': 5
                }
            ]
        }
        
        # Encuesta de Hábitos
        habits_survey = {
            'survey_id': 'daily_habits',
            'title': 'Evaluación de Hábitos Diarios',
            'description': 'Evalúa tus hábitos diarios de bienestar',
            'questions': [
                {
                    'question_id': 'sleep_hours',
                    'text': '¿Cuántas horas dormiste anoche?',
                    'type': 'number',
                    'min_value': 0,
                    'max_value': 24
                },
                {
                    'question_id': 'exercise',
                    'text': '¿Hiciste ejercicio hoy?',
                    'type': 'multiple_choice',
                    'options': ['No', 'Ejercicio ligero (caminar)', 'Ejercicio moderado', 'Ejercicio intenso']
                },
                {
                    'question_id': 'water_intake',
                    'text': '¿Cuántos vasos de agua tomaste hoy?',
                    'type': 'number',
                    'min_value': 0,
                    'max_value': 20
                },
                {
                    'question_id': 'social_interaction',
                    'text': '¿Tuviste interacciones sociales positivas hoy?',
                    'type': 'scale',
                    'options': ['Ninguna', 'Pocas', 'Algunas', 'Bastantes', 'Muchas'],
                    'scale_min': 1,
                    'scale_max': 5
                }
            ]
        }
        
        # Encuesta de Evaluación de Riesgo
        risk_survey = {
            'survey_id': 'risk_assessment',
            'title': 'Evaluación de Factores de Riesgo',
            'description': 'Identifica factores de riesgo para tu bienestar mental',
            'questions': [
                {
                    'question_id': 'anxiety_frequency',
                    'text': '¿Con qué frecuencia sientes ansiedad?',
                    'type': 'multiple_choice',
                    'options': ['Nunca', 'Raramente', 'A veces', 'Frecuentemente', 'Siempre']
                },
                {
                    'question_id': 'depression_symptoms',
                    'text': '¿Has experimentado síntomas de tristeza persistente?',
                    'type': 'multiple_choice',
                    'options': ['No', 'Ocasionalmente', 'Algunas veces', 'Frecuentemente', 'Constantemente']
                },
                {
                    'question_id': 'support_system',
                    'text': '¿Tienes un sistema de apoyo confiable?',
                    'type': 'scale',
                    'options': ['Ninguno', 'Muy poco', 'Algo', 'Bastante', 'Mucho'],
                    'scale_min': 1,
                    'scale_max': 5
                },
                {
                    'question_id': 'work_stress',
                    'text': '¿Cómo calificarías el estrés relacionado con trabajo/estudios?',
                    'type': 'scale',
                    'options': ['Muy bajo', 'Bajo', 'Moderado', 'Alto', 'Muy alto'],
                    'scale_min': 1,
                    'scale_max': 5
                }
            ]
        }
        
        # Crear las encuestas en la base de datos
        for survey_data in [emotional_survey, habits_survey, risk_survey]:
            self.create_survey(
                survey_data['survey_id'],
                survey_data['title'],
                survey_data['description'],
                survey_data['questions']
            )
    
    def create_survey(self, survey_id: str, title: str, description: str, questions: List[Dict]) -> bool:
        """
        Crea una nueva encuesta en la base de datos.
        
        Args:
            survey_id: ID único de la encuesta
            title: Título de la encuesta
            description: Descripción de la encuesta
            questions: Lista de preguntas
            
        Returns:
            bool: True si se creó exitosamente
        """
        try:
            # Crear la encuesta
            survey_created = self.db_manager.create_survey(survey_id, title, description)
            
            if survey_created:
                # Crear las preguntas
                for i, question in enumerate(questions):
                    # Mapear el tipo de pregunta
                    question_type = question['type']
                    if question_type == 'scale':
                        question_type = 'likert_scale'
                    elif question_type == 'number':
                        question_type = 'open_text'
                    
                    self.db_manager.create_question(
                        question_id=question['question_id'],
                        survey_id=survey_id,
                        text=question['text'],
                        question_type=question_type,
                        category='general',
                        scale_min=question.get('scale_min'),
                        scale_max=question.get('scale_max'),
                        options=question.get('options', []),
                        question_order=i + 1
                    )
                return True
            return False
            
        except Exception as e:
            print(f"Error creando encuesta {survey_id}: {e}")
            return False
    
    def get_available_surveys(self) -> List[Survey]:
        """
        Obtiene todas las encuestas disponibles.
        
        Returns:
            List[Survey]: Lista de encuestas disponibles
        """
        try:
            # Asegurar conexión a la base de datos
            if not self.db_manager.connect():
                print("Error: No se pudo conectar a la base de datos")
                return []
                
            surveys_data = self.db_manager.get_all_surveys()
            surveys = []
            
            for survey_data in surveys_data:
                questions = self.db_manager.get_survey_questions(survey_data['survey_id'])
                
                # Procesar preguntas
                processed_questions = []
                for question in questions:
                    # Manejar opciones correctamente
                    options = question.get('options', [])
                    if isinstance(options, str):
                        try:
                            options = json.loads(options)
                        except:
                            options = []
                    elif not isinstance(options, list):
                        options = []
                    
                    question_dict = {
                        'question_id': question['question_id'],
                        'text': question['text'],
                        'type': question['question_type'],
                        'options': options
                    }
                    
                    # Agregar metadata si existe
                    if question.get('metadata'):
                        try:
                            metadata = json.loads(question['metadata']) if isinstance(question['metadata'], str) else question['metadata']
                            question_dict.update(metadata)
                        except:
                            pass
                    
                    processed_questions.append(question_dict)
                
                survey = Survey(
                    survey_id=survey_data['survey_id'],
                    title=survey_data['title'],
                    description=survey_data['description'],
                    questions=processed_questions
                )
                surveys.append(survey)
            
            # Cerrar conexión
            self.db_manager.disconnect()
            return surveys
            
        except Exception as e:
            print(f"Error obteniendo encuestas: {e}")
            return []
    
    def get_survey(self, survey_id: str) -> Optional[Survey]:
        """
        Obtiene una encuesta específica por ID.
        
        Args:
            survey_id: ID de la encuesta
            
        Returns:
            Optional[Survey]: La encuesta o None si no existe
        """
        try:
            # Asegurar conexión a la base de datos
            if not self.db_manager.connect():
                print("Error: No se pudo conectar a la base de datos para obtener encuesta")
                return None
                
            survey_data = self.db_manager.get_survey(survey_id)
            if not survey_data:
                self.db_manager.disconnect()
                return None
            
            questions = self.db_manager.get_survey_questions(survey_id)
            
            # Procesar preguntas
            processed_questions = []
            for question in questions:
                # Manejar opciones correctamente
                options = question.get('options', [])
                if isinstance(options, str):
                    try:
                        options = json.loads(options)
                    except:
                        options = []
                elif not isinstance(options, list):
                    options = []
                
                question_dict = {
                    'question_id': question['question_id'],
                    'text': question['text'],
                    'type': question['question_type'],
                    'options': options
                }
                
                # Agregar metadata si existe
                if question.get('metadata'):
                    try:
                        metadata = json.loads(question['metadata']) if isinstance(question['metadata'], str) else question['metadata']
                        question_dict.update(metadata)
                    except:
                        pass
                
                processed_questions.append(question_dict)
            
            # Cerrar conexión
            self.db_manager.disconnect()
            
            return Survey(
                survey_id=survey_data['survey_id'],
                title=survey_data['title'],
                description=survey_data['description'],
                questions=processed_questions
            )
            
        except Exception as e:
            print(f"Error obteniendo encuesta {survey_id}: {e}")
            return None
    
    def save_response(self, user_id: str, survey_id: str, responses: Dict[str, Any]) -> bool:
        """
        Guarda las respuestas de un usuario a una encuesta.
        
        Args:
            user_id: ID del usuario
            survey_id: ID de la encuesta
            responses: Diccionario con las respuestas
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Asegurar conexión a la base de datos
            if not self.db_manager.connect():
                print("Error: No se pudo conectar a la base de datos para guardar respuesta")
                return False
            
            # Generar un ID único para la respuesta
            import uuid
            response_id = f"resp_{uuid.uuid4().hex[:12]}"
            
            # Crear la respuesta de encuesta con la firma correcta
            response_created = self.db_manager.create_survey_response(
                response_id=response_id,
                user_id=user_id,
                survey_id=survey_id,
                duration_minutes=0.0
            )
            
            if not response_created:
                self.db_manager.disconnect()
                return False
            
            # Guardar cada respuesta individual
            for question_id, answer in responses.items():
                # Intentar derivar un valor numérico si aplica
                answer_numeric = None
                try:
                    if isinstance(answer, str) and answer.isdigit():
                        answer_numeric = int(answer)
                    elif isinstance(answer, (int, float)):
                        answer_numeric = int(answer)
                except Exception:
                    answer_numeric = None
                
                self.db_manager.create_question_answer(
                    response_id=response_id,
                    question_id=question_id,
                    answer_value=str(answer),
                    answer_numeric=answer_numeric
                )
            
            # Cerrar conexión
            self.db_manager.disconnect()
            return True
            
        except Exception as e:
            print(f"Error guardando respuesta: {e}")
            try:
                self.db_manager.disconnect()
            except Exception:
                pass
            return False
    
    def get_user_responses(self, user_id: str, survey_id: Optional[str] = None) -> List[Dict]:
        """
        Obtiene las respuestas de un usuario.
        
        Args:
            user_id: ID del usuario
            survey_id: ID de la encuesta (opcional)
            
        Returns:
            List[Dict]: Lista de respuestas del usuario
        """
        try:
            # Nota: DatabaseManager.get_user_responses solo acepta user_id
            return self.db_manager.get_user_responses(user_id)
        except Exception as e:
            print(f"Error obteniendo respuestas del usuario: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del sistema.
        
        Returns:
            Dict[str, Any]: Estadísticas del sistema
        """
        try:
            stats = self.db_manager.get_statistics()
            return {
                'total_users': stats.get('total_users', 0),
                'total_surveys': stats.get('total_surveys', 0),
                'total_responses': stats.get('total_responses', 0),
                'responses_today': stats.get('responses_today', 0)
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                'total_users': 0,
                'total_surveys': 0,
                'total_responses': 0,
                'responses_today': 0
            }
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.db_manager:
            self.db_manager.close()