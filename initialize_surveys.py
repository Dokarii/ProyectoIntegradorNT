import sys
import os
sys.path.append('src')
from core.database_manager import DatabaseManager

print("🔄 Inicializando encuestas por defecto...")

# Crear instancia del gestor de base de datos
db = DatabaseManager()
if not db.connect():
    print("❌ Error conectando a la base de datos")
    exit(1)

# Definir las encuestas por defecto
default_surveys = [
    {
        'survey_id': 'estado_emocional',
        'title': 'Estado Emocional',
        'description': 'Evaluación del estado emocional actual',
        'questions': [
            {
                'question_id': 'humor_general',
                'text': '¿Cómo describirías tu estado de ánimo general hoy?',
                'type': 'likert_scale',
                'scale_min': 1,
                'scale_max': 5,
                'options': ['Muy malo', 'Malo', 'Regular', 'Bueno', 'Muy bueno']
            },
            {
                'question_id': 'nivel_estres',
                'text': '¿Cuál es tu nivel de estrés actual?',
                'type': 'likert_scale',
                'scale_min': 1,
                'scale_max': 5,
                'options': ['Muy bajo', 'Bajo', 'Moderado', 'Alto', 'Muy alto']
            },
            {
                'question_id': 'energia_nivel',
                'text': '¿Cómo calificarías tu nivel de energía?',
                'type': 'likert_scale',
                'scale_min': 1,
                'scale_max': 5,
                'options': ['Muy bajo', 'Bajo', 'Normal', 'Alto', 'Muy alto']
            }
        ]
    },
    {
        'survey_id': 'habitos_diarios',
        'title': 'Hábitos Diarios',
        'description': 'Evaluación de hábitos y rutinas diarias',
        'questions': [
            {
                'question_id': 'horas_sueno',
                'text': '¿Cuántas horas dormiste anoche?',
                'type': 'open_text',
                'scale_min': 0,
                'scale_max': 24
            },
            {
                'question_id': 'ejercicio_realizado',
                'text': '¿Realizaste ejercicio físico hoy?',
                'type': 'multiple_choice',
                'options': ['Sí, más de 30 minutos', 'Sí, menos de 30 minutos', 'No, pero planeo hacerlo', 'No']
            },
            {
                'question_id': 'alimentacion_calidad',
                'text': '¿Cómo calificarías la calidad de tu alimentación hoy?',
                'type': 'likert_scale',
                'scale_min': 1,
                'scale_max': 5,
                'options': ['Muy mala', 'Mala', 'Regular', 'Buena', 'Muy buena']
            }
        ]
    },
    {
        'survey_id': 'factores_riesgo',
        'title': 'Evaluación de Factores de Riesgo',
        'description': 'Identificación de factores de riesgo para el bienestar emocional',
        'questions': [
            {
                'question_id': 'apoyo_social',
                'text': '¿Sientes que tienes suficiente apoyo social?',
                'type': 'likert_scale',
                'scale_min': 1,
                'scale_max': 5,
                'options': ['Nada', 'Poco', 'Algo', 'Bastante', 'Mucho']
            },
            {
                'question_id': 'satisfaccion_trabajo',
                'text': '¿Qué tan satisfecho estás con tu trabajo/estudios?',
                'type': 'likert_scale',
                'scale_min': 1,
                'scale_max': 5,
                'options': ['Muy insatisfecho', 'Insatisfecho', 'Neutral', 'Satisfecho', 'Muy satisfecho']
            },
            {
                'question_id': 'preocupaciones_principales',
                'text': '¿Cuáles son tus principales preocupaciones actualmente?',
                'type': 'open_text'
            }
        ]
    }
]

# Crear las encuestas
for survey_data in default_surveys:
    print(f"📝 Creando encuesta: {survey_data['title']}")
    
    # Crear la encuesta
    survey_created = db.create_survey(
        survey_id=survey_data['survey_id'],
        title=survey_data['title'],
        description=survey_data['description'],
        estimated_duration=10
    )
    
    if survey_created:
        print(f"  ✅ Encuesta '{survey_data['title']}' creada")
        
        # Crear las preguntas
        for i, question in enumerate(survey_data['questions']):
            question_created = db.create_question(
                question_id=question['question_id'],
                survey_id=survey_data['survey_id'],
                text=question['text'],
                question_type=question['type'],
                category='general',
                scale_min=question.get('scale_min'),
                scale_max=question.get('scale_max'),
                options=question.get('options', []),
                question_order=i + 1
            )
            
            if question_created:
                print(f"    ✅ Pregunta '{question['question_id']}' creada")
            else:
                print(f"    ❌ Error creando pregunta '{question['question_id']}'")
    else:
        print(f"  ❌ Error creando encuesta '{survey_data['title']}'")

print("\n🎉 Inicialización de encuestas completada")

# Verificar las encuestas creadas
surveys = db.get_all_surveys()
print(f"\n📊 Total de encuestas en la base de datos: {len(surveys)}")
for survey in surveys:
    questions = db.get_survey_questions(survey['survey_id'])
    print(f"  - {survey['title']}: {len(questions)} preguntas")

db.disconnect()