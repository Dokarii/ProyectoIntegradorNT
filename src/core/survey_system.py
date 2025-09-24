"""
Sistema de Encuestas Emocionales
===============================

Este módulo proporciona funcionalidades para crear, administrar y procesar
encuestas sobre el estado emocional y bienestar de los usuarios.

Autor: Equipo de Desarrollo
Fecha: 2024
Versión: 1.0
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class QuestionType(Enum):
    """Tipos de preguntas disponibles en las encuestas."""
    LIKERT_SCALE = "likert_scale"  # Escala 1-5 o 1-7
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"
    OPEN_TEXT = "open_text"
    RATING_SCALE = "rating_scale"  # Escala 1-10
    YES_NO = "yes_no"


@dataclass
class Question:
    """Clase para representar una pregunta de encuesta."""
    
    question_id: str
    text: str
    question_type: QuestionType
    options: List[str] = None
    scale_min: int = 1
    scale_max: int = 5
    required: bool = True
    category: str = "general"
    
    def __post_init__(self):
        """Inicializa opciones vacías si no se proporcionan."""
        if self.options is None:
            self.options = []
    
    def validate_answer(self, answer: Any) -> Tuple[bool, str]:
        """
        Valida una respuesta para esta pregunta.
        
        Args:
            answer: Respuesta a validar
            
        Returns:
            Tuple[bool, str]: (es_válida, mensaje_error)
        """
        if self.required and (answer is None or answer == ""):
            return False, "Esta pregunta es obligatoria"
        
        if answer is None or answer == "":
            return True, ""  # Pregunta opcional sin respuesta
        
        if self.question_type == QuestionType.LIKERT_SCALE:
            if not isinstance(answer, int) or not (self.scale_min <= answer <= self.scale_max):
                return False, f"La respuesta debe ser un número entre {self.scale_min} y {self.scale_max}"
        
        elif self.question_type == QuestionType.RATING_SCALE:
            if not isinstance(answer, int) or not (self.scale_min <= answer <= self.scale_max):
                return False, f"La calificación debe ser entre {self.scale_min} y {self.scale_max}"
        
        elif self.question_type == QuestionType.MULTIPLE_CHOICE:
            if answer not in self.options:
                return False, "Debe seleccionar una opción válida"
        
        elif self.question_type == QuestionType.CHECKBOX:
            if not isinstance(answer, list):
                return False, "Debe seleccionar al menos una opción"
            for item in answer:
                if item not in self.options:
                    return False, f"'{item}' no es una opción válida"
        
        elif self.question_type == QuestionType.YES_NO:
            if answer not in ["Sí", "No", "Si", "si", "sí", "no", True, False]:
                return False, "Debe responder Sí o No"
        
        elif self.question_type == QuestionType.OPEN_TEXT:
            if isinstance(answer, str) and len(answer.strip()) > 1000:
                return False, "La respuesta no puede exceder 1000 caracteres"
        
        return True, ""


@dataclass
class SurveyResponse:
    """Clase para representar la respuesta de un usuario a una encuesta."""
    
    response_id: str
    user_id: str
    survey_id: str
    answers: Dict[str, Any]
    completion_time: str
    duration_minutes: float
    is_complete: bool = True
    
    def calculate_scores(self, survey: 'Survey') -> Dict[str, float]:
        """
        Calcula puntajes por categoría basado en las respuestas.
        
        Args:
            survey: La encuesta correspondiente
            
        Returns:
            Dict[str, float]: Puntajes por categoría
        """
        category_scores = {}
        category_counts = {}
        
        for question in survey.questions:
            if question.question_id in self.answers:
                answer = self.answers[question.question_id]
                category = question.category
                
                # Solo procesar respuestas numéricas para puntajes
                if isinstance(answer, int):
                    if category not in category_scores:
                        category_scores[category] = 0
                        category_counts[category] = 0
                    
                    # Normalizar a escala 0-100
                    normalized_score = ((answer - question.scale_min) / 
                                      (question.scale_max - question.scale_min)) * 100
                    
                    category_scores[category] += normalized_score
                    category_counts[category] += 1
        
        # Calcular promedios
        for category in category_scores:
            if category_counts[category] > 0:
                category_scores[category] = category_scores[category] / category_counts[category]
        
        return category_scores


@dataclass
class Survey:
    """Clase para representar una encuesta completa."""
    
    survey_id: str
    title: str
    description: str
    questions: List[Question]
    created_date: str
    is_active: bool = True
    estimated_duration: int = 10  # minutos
    
    def add_question(self, question: Question) -> None:
        """Añade una pregunta a la encuesta."""
        self.questions.append(question)
    
    def validate_responses(self, answers: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida todas las respuestas de una encuesta.
        
        Args:
            answers: Diccionario con las respuestas
            
        Returns:
            Tuple[bool, List[str]]: (son_válidas, lista_errores)
        """
        errors = []
        
        for question in self.questions:
            answer = answers.get(question.question_id)
            is_valid, error_msg = question.validate_answer(answer)
            
            if not is_valid:
                errors.append(f"Pregunta '{question.text[:50]}...': {error_msg}")
        
        return len(errors) == 0, errors
    
    def get_questions_by_category(self) -> Dict[str, List[Question]]:
        """Agrupa las preguntas por categoría."""
        categories = {}
        for question in self.questions:
            if question.category not in categories:
                categories[question.category] = []
            categories[question.category].append(question)
        return categories


class SurveyManager:
    """Clase principal para gestionar encuestas y respuestas."""
    
    def __init__(self, data_path: str = "data/surveys/"):
        """
        Inicializa el gestor de encuestas.
        
        Args:
            data_path: Ruta donde se almacenan los datos de encuestas
        """
        self.data_path = data_path
        self.surveys: Dict[str, Survey] = {}
        self.responses: Dict[str, SurveyResponse] = {}
        self._create_default_surveys()
    
    def _create_default_surveys(self) -> None:
        """Crea encuestas predeterminadas del sistema."""
        # Encuesta de Estado Emocional Básico
        emotional_survey = self.create_emotional_state_survey()
        self.surveys[emotional_survey.survey_id] = emotional_survey
        
        # Encuesta de Hábitos y Bienestar
        habits_survey = self.create_habits_survey()
        self.surveys[habits_survey.survey_id] = habits_survey
        
        # Encuesta de Evaluación de Riesgo
        risk_survey = self.create_risk_assessment_survey()
        self.surveys[risk_survey.survey_id] = risk_survey
    
    def create_emotional_state_survey(self) -> Survey:
        """Crea la encuesta de estado emocional básico."""
        survey_id = str(uuid.uuid4())[:8]
        survey = Survey(
            survey_id=survey_id,
            title="Evaluación de Estado Emocional",
            description="Encuesta para evaluar tu estado emocional actual y bienestar general.",
            questions=[],
            created_date=datetime.now().isoformat(),
            estimated_duration=5
        )
        
        # Preguntas sobre estado emocional
        questions = [
            Question(
                question_id="mood_current",
                text="¿Cómo describirías tu estado de ánimo en este momento?",
                question_type=QuestionType.LIKERT_SCALE,
                scale_min=1,
                scale_max=5,
                category="estado_emocional"
            ),
            Question(
                question_id="stress_level",
                text="En una escala del 1 al 10, ¿qué tan estresado/a te sientes?",
                question_type=QuestionType.RATING_SCALE,
                scale_min=1,
                scale_max=10,
                category="estres"
            ),
            Question(
                question_id="anxiety_level",
                text="¿Con qué frecuencia has sentido ansiedad en la última semana?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Nunca", "Raramente", "A veces", "Frecuentemente", "Siempre"],
                category="ansiedad"
            ),
            Question(
                question_id="sleep_quality",
                text="¿Cómo calificarías la calidad de tu sueño en la última semana?",
                question_type=QuestionType.LIKERT_SCALE,
                scale_min=1,
                scale_max=5,
                category="bienestar_fisico"
            ),
            Question(
                question_id="social_support",
                text="¿Sientes que tienes suficiente apoyo de familiares y amigos?",
                question_type=QuestionType.YES_NO,
                category="apoyo_social"
            ),
            Question(
                question_id="emotional_concerns",
                text="¿Hay algo específico que te preocupe emocionalmente en este momento?",
                question_type=QuestionType.OPEN_TEXT,
                required=False,
                category="preocupaciones"
            )
        ]
        
        for question in questions:
            survey.add_question(question)
        
        return survey
    
    def create_habits_survey(self) -> Survey:
        """Crea la encuesta de hábitos y bienestar."""
        survey_id = str(uuid.uuid4())[:8]
        survey = Survey(
            survey_id=survey_id,
            title="Evaluación de Hábitos y Bienestar",
            description="Encuesta sobre tus hábitos diarios y su impacto en tu bienestar.",
            questions=[],
            created_date=datetime.now().isoformat(),
            estimated_duration=8
        )
        
        questions = [
            Question(
                question_id="exercise_frequency",
                text="¿Con qué frecuencia realizas actividad física?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Nunca", "1-2 veces por semana", "3-4 veces por semana", 
                        "5-6 veces por semana", "Todos los días"],
                category="actividad_fisica"
            ),
            Question(
                question_id="screen_time",
                text="¿Cuántas horas al día pasas frente a pantallas (celular, computadora, TV)?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Menos de 2 horas", "2-4 horas", "4-6 horas", 
                        "6-8 horas", "Más de 8 horas"],
                category="uso_tecnologia"
            ),
            Question(
                question_id="social_activities",
                text="¿Participas regularmente en actividades sociales o comunitarias?",
                question_type=QuestionType.YES_NO,
                category="participacion_social"
            ),
            Question(
                question_id="healthy_eating",
                text="¿Qué tan saludable consideras tu alimentación?",
                question_type=QuestionType.LIKERT_SCALE,
                scale_min=1,
                scale_max=5,
                category="alimentacion"
            ),
            Question(
                question_id="substance_use",
                text="¿Has consumido alcohol o sustancias en la última semana?",
                question_type=QuestionType.CHECKBOX,
                options=["Alcohol", "Tabaco", "Otras sustancias", "Ninguna"],
                category="consumo_sustancias"
            )
        ]
        
        for question in questions:
            survey.add_question(question)
        
        return survey
    
    def create_risk_assessment_survey(self) -> Survey:
        """Crea la encuesta de evaluación de riesgo."""
        survey_id = str(uuid.uuid4())[:8]
        survey = Survey(
            survey_id=survey_id,
            title="Evaluación de Factores de Riesgo",
            description="Evaluación confidencial para identificar factores de riesgo y necesidades de apoyo.",
            questions=[],
            created_date=datetime.now().isoformat(),
            estimated_duration=10
        )
        
        questions = [
            Question(
                question_id="hopelessness",
                text="¿Has sentido que no vale la pena vivir?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Nunca", "Raramente", "A veces", "Frecuentemente", "Siempre"],
                category="riesgo_alto"
            ),
            Question(
                question_id="self_harm",
                text="¿Has pensado en hacerte daño a ti mismo/a?",
                question_type=QuestionType.YES_NO,
                category="riesgo_alto"
            ),
            Question(
                question_id="isolation",
                text="¿Te sientes aislado/a de otras personas?",
                question_type=QuestionType.LIKERT_SCALE,
                scale_min=1,
                scale_max=5,
                category="aislamiento"
            ),
            Question(
                question_id="family_problems",
                text="¿Tienes problemas significativos en casa o con tu familia?",
                question_type=QuestionType.YES_NO,
                category="problemas_familiares"
            ),
            Question(
                question_id="academic_stress",
                text="¿Qué tan estresado/a te sientes por temas académicos o laborales?",
                question_type=QuestionType.RATING_SCALE,
                scale_min=1,
                scale_max=10,
                category="estres_academico"
            ),
            Question(
                question_id="help_seeking",
                text="¿Estarías dispuesto/a a buscar ayuda profesional si la necesitaras?",
                question_type=QuestionType.YES_NO,
                category="disposicion_ayuda"
            )
        ]
        
        for question in questions:
            survey.add_question(question)
        
        return survey
    
    def submit_response(self, user_id: str, survey_id: str, 
                       answers: Dict[str, Any], start_time: datetime) -> Tuple[bool, str, Optional[SurveyResponse]]:
        """
        Procesa y almacena la respuesta de un usuario a una encuesta.
        
        Args:
            user_id: ID del usuario
            survey_id: ID de la encuesta
            answers: Respuestas del usuario
            start_time: Tiempo de inicio de la encuesta
            
        Returns:
            Tuple[bool, str, Optional[SurveyResponse]]: (éxito, mensaje, respuesta)
        """
        if survey_id not in self.surveys:
            return False, "Encuesta no encontrada", None
        
        survey = self.surveys[survey_id]
        
        # Validar respuestas
        is_valid, errors = survey.validate_responses(answers)
        if not is_valid:
            return False, f"Errores en las respuestas: {'; '.join(errors)}", None
        
        # Crear respuesta
        response_id = str(uuid.uuid4())
        completion_time = datetime.now()
        duration = (completion_time - start_time).total_seconds() / 60  # minutos
        
        response = SurveyResponse(
            response_id=response_id,
            user_id=user_id,
            survey_id=survey_id,
            answers=answers,
            completion_time=completion_time.isoformat(),
            duration_minutes=round(duration, 2)
        )
        
        # Almacenar respuesta
        self.responses[response_id] = response
        
        # Guardar en archivo
        self.save_response_to_file(response)
        
        return True, "Respuesta guardada exitosamente", response
    
    def save_response_to_file(self, response: SurveyResponse) -> None:
        """Guarda una respuesta en archivo JSON."""
        import os
        os.makedirs(self.data_path, exist_ok=True)
        
        filename = f"{self.data_path}response_{response.response_id}.json"
        response_dict = asdict(response)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response_dict, f, indent=2, ensure_ascii=False)
    
    def get_user_responses(self, user_id: str) -> List[SurveyResponse]:
        """Obtiene todas las respuestas de un usuario."""
        return [response for response in self.responses.values() 
                if response.user_id == user_id]
    
    def analyze_responses(self, survey_id: str) -> Dict[str, Any]:
        """
        Analiza las respuestas de una encuesta específica.
        
        Args:
            survey_id: ID de la encuesta a analizar
            
        Returns:
            Dict: Análisis de las respuestas
        """
        survey_responses = [r for r in self.responses.values() 
                          if r.survey_id == survey_id]
        
        if not survey_responses:
            return {"message": "No hay respuestas para esta encuesta"}
        
        survey = self.surveys[survey_id]
        analysis = {
            "survey_title": survey.title,
            "total_responses": len(survey_responses),
            "average_duration": sum(r.duration_minutes for r in survey_responses) / len(survey_responses),
            "category_scores": {},
            "risk_indicators": []
        }
        
        # Analizar puntajes por categoría
        all_category_scores = {}
        for response in survey_responses:
            scores = response.calculate_scores(survey)
            for category, score in scores.items():
                if category not in all_category_scores:
                    all_category_scores[category] = []
                all_category_scores[category].append(score)
        
        # Calcular promedios por categoría
        for category, scores in all_category_scores.items():
            analysis["category_scores"][category] = {
                "average": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "count": len(scores)
            }
        
        # Identificar indicadores de riesgo
        for response in survey_responses:
            if self._has_risk_indicators(response, survey):
                analysis["risk_indicators"].append({
                    "user_id": response.user_id,
                    "response_id": response.response_id,
                    "completion_time": response.completion_time
                })
        
        return analysis
    
    def _has_risk_indicators(self, response: SurveyResponse, survey: Survey) -> bool:
        """Identifica si una respuesta tiene indicadores de riesgo."""
        risk_questions = ["hopelessness", "self_harm", "isolation"]
        
        for question_id in risk_questions:
            if question_id in response.answers:
                answer = response.answers[question_id]
                
                # Criterios de riesgo específicos
                if question_id == "self_harm" and answer in ["Sí", "Si", True]:
                    return True
                elif question_id == "hopelessness" and answer in ["Frecuentemente", "Siempre"]:
                    return True
                elif question_id == "isolation" and isinstance(answer, int) and answer >= 4:
                    return True
        
        return False


def simulate_survey_responses(num_responses: int = 20) -> None:
    """
    Simula respuestas a encuestas para pruebas.
    
    Args:
        num_responses: Número de respuestas a simular
    """
    import random
    
    survey_manager = SurveyManager()
    
    # IDs de usuarios simulados
    user_ids = [f"user_{i:03d}" for i in range(1, num_responses + 1)]
    
    print("🔄 Simulando respuestas a encuestas...")
    
    for user_id in user_ids:
        # Responder a encuesta emocional
        emotional_survey_id = list(survey_manager.surveys.keys())[0]
        emotional_answers = {
            "mood_current": random.randint(1, 5),
            "stress_level": random.randint(1, 10),
            "anxiety_level": random.choice(["Nunca", "Raramente", "A veces", "Frecuentemente", "Siempre"]),
            "sleep_quality": random.randint(1, 5),
            "social_support": random.choice(["Sí", "No"]),
            "emotional_concerns": "Preocupaciones académicas y futuro laboral" if random.random() > 0.5 else ""
        }
        
        start_time = datetime.now() - timedelta(minutes=random.randint(5, 15))
        success, message, response = survey_manager.submit_response(
            user_id, emotional_survey_id, emotional_answers, start_time
        )
        
        if success:
            print(f"✓ Respuesta emocional guardada para {user_id}")
        
        # Responder a encuesta de hábitos (50% de probabilidad)
        if random.random() > 0.5:
            habits_survey_id = list(survey_manager.surveys.keys())[1]
            habits_answers = {
                "exercise_frequency": random.choice(["Nunca", "1-2 veces por semana", "3-4 veces por semana"]),
                "screen_time": random.choice(["2-4 horas", "4-6 horas", "6-8 horas", "Más de 8 horas"]),
                "social_activities": random.choice(["Sí", "No"]),
                "healthy_eating": random.randint(1, 5),
                "substance_use": random.choice([["Ninguna"], ["Alcohol"], ["Alcohol", "Tabaco"]])
            }
            
            start_time = datetime.now() - timedelta(minutes=random.randint(8, 20))
            survey_manager.submit_response(user_id, habits_survey_id, habits_answers, start_time)
    
    # Mostrar análisis
    print("\n📊 Análisis de respuestas:")
    for survey_id, survey in survey_manager.surveys.items():
        analysis = survey_manager.analyze_responses(survey_id)
        if "total_responses" in analysis:
            print(f"\n{survey.title}:")
            print(f"  - Total respuestas: {analysis['total_responses']}")
            print(f"  - Duración promedio: {analysis['average_duration']:.1f} minutos")
            print(f"  - Indicadores de riesgo: {len(analysis['risk_indicators'])}")
    
    print(f"\n✅ Simulación completada con {len(survey_manager.responses)} respuestas")


if __name__ == "__main__":
    print("🚀 Iniciando sistema de encuestas...")
    simulate_survey_responses(25)
    print("✅ Sistema de encuestas listo!")