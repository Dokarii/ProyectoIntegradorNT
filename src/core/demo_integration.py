"""
Demostración de Integración del Sistema
=======================================

Este script demuestra la integración completa de todos los módulos
desarrollados para la plataforma de monitoreo emocional de jóvenes vulnerables.

Autor: Equipo de Desarrollo
Fecha: 2024
Versión: 1.0
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.user_management import UserManager, simulate_user_registration
from core.survey_system import SurveyManager, simulate_survey_responses
from core.data_handler import DataProcessor


def create_sample_users(user_manager: UserManager, num_users: int = 10) -> list:
    """
    Crea usuarios de muestra para la demostración.
    
    Args:
        user_manager: Instancia del gestor de usuarios
        num_users: Número de usuarios a crear
        
    Returns:
        Lista de IDs de usuarios creados
    """
    print(f"👥 Creando {num_users} usuarios de muestra...")
    
    sample_names = [
        "Ana García", "Carlos Rodríguez", "María López", "Juan Martínez",
        "Sofia Hernández", "Diego Pérez", "Valentina Torres", "Andrés Gómez",
        "Camila Ruiz", "Santiago Vargas", "Isabella Castro", "Mateo Jiménez"
    ]
    
    locations = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Bucaramanga"]
    genders = ["Masculino", "Femenino", "No binario", "Prefiero no decir"]
    
    created_users = []
    
    for i in range(num_users):
        # Generar datos de usuario más simples para evitar errores de validación
        username = f"user_{i:03d}"
        email = f"user{i:03d}@plataforma.com"
        location = random.choice(locations)
        gender = random.choice(genders)
        
        # Crear perfil emocional inicial
        stress_level = random.randint(1, 10)
        anxiety_level = random.randint(1, 10)
        depression_indicators = random.randint(0, 5)
        
        # Preparar datos del usuario
        name = random.choice(sample_names)
        age = random.randint(14, 25)  # Rango de jóvenes vulnerables
        user_data = {
            'username': username,
            'email': email,
            'age': age,
            'gender': gender,
            'location': location,
            'consent_given': True
        }
        
        # Registrar usuario
        success, message, user = user_manager.register_user(user_data)
        user_id = user.user_id if user else None
        
        if user_id:
            created_users.append(user_id)
            print(f"  ✅ Usuario creado: {name} (ID: {user_id})")
            
            # Actualizar perfil emocional después del registro
            if user:
                user.emotional_profile.stress_level = stress_level
                user.emotional_profile.anxiety_level = anxiety_level
                user.emotional_profile.depression_indicators = depression_indicators
                user_manager.save_user_to_file(user)
        else:
            print(f"  ❌ Error creando usuario {name}: {message}")
    
    print(f"✅ {len(created_users)} usuarios creados exitosamente\n")
    return created_users


def generate_survey_responses(survey_manager: SurveyManager, user_ids: list, days_back: int = 30):
    """
    Genera respuestas de encuestas para usuarios simulados.
    
    Args:
        survey_manager: Gestor de encuestas
        user_ids: Lista de IDs de usuarios
        days_back: Número de días hacia atrás para generar respuestas
    """
    print(f"📋 Generando respuestas de encuestas para {len(user_ids)} usuarios...")
    
    # Obtener todas las encuestas disponibles
    surveys = [(name, survey) for name, survey in survey_manager.surveys.items()]
    
    if not surveys:
        print("  ⚠️  No hay encuestas disponibles")
        return 0
    
    total_responses = 0
    
    for user_id in user_ids:
        # Generar respuestas para diferentes días
        for day in range(days_back):
            response_date = datetime.now() - timedelta(days=day)
            
            # No todos los usuarios responden todos los días
            if random.random() < 0.7:  # 70% probabilidad de respuesta por día
                continue
            
            # Seleccionar encuesta aleatoria
            survey_type, survey = random.choice(surveys)
            
            # Generar respuestas realistas basadas en el perfil del usuario
            responses = {}
            
            for question in survey.questions:
                if question.question_type.value == "likert_scale":
                    # Respuestas Likert (1-5)
                    if "estrés" in question.text.lower() or "ansiedad" in question.text.lower():
                        # Usuarios vulnerables tienden a reportar más estrés
                        responses[question.question_id] = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
                    else:
                        responses[question.question_id] = random.randint(1, 5)
                
                elif question.question_type.value == "rating_scale":
                    # Ratings (1-10)
                    if "bienestar" in question.text.lower() or "felicidad" in question.text.lower():
                        # Usuarios vulnerables pueden tener bienestar más bajo
                        responses[question.question_id] = random.choices(range(1, 11), weights=[15, 15, 15, 15, 10, 10, 8, 5, 4, 3])[0]
                    else:
                        responses[question.question_id] = random.randint(1, 10)
                
                elif question.question_type.value == "multiple_choice":
                    responses[question.question_id] = random.choice(question.options)
                
                elif question.question_type.value == "yes_no":
                    responses[question.question_id] = random.choice(["Sí", "No"])
                
                elif question.question_type.value == "checkbox":
                    # Seleccionar algunas opciones aleatoriamente
                    selected = random.sample(question.options, random.randint(1, min(3, len(question.options))))
                    responses[question.question_id] = selected
                
                elif question.question_type.value == "open_text":
                    sample_responses = [
                        "Me siento bien en general",
                        "He tenido algunos días difíciles",
                        "Estoy trabajando en mejorar mi bienestar",
                        "Necesito más apoyo emocional",
                        "Las cosas están mejorando poco a poco"
                    ]
                    responses[question.question_id] = random.choice(sample_responses)
            
            # Enviar respuesta
            success, message, response = survey_manager.submit_response(
                user_id=user_id,
                survey_id=survey.survey_id,
                answers=responses,
                start_time=response_date
            )
            
            if success:
                total_responses += 1
            else:
                print(f"  ❌ Error al enviar respuesta: {message}")
    
    print(f"✅ {total_responses} respuestas de encuestas generadas")
    return total_responses


def analyze_data_and_generate_reports(data_processor: DataProcessor, user_manager: UserManager, survey_manager: SurveyManager):
    """
    Analiza los datos generados y crea reportes.
    
    Args:
        data_processor: Procesador de datos
        user_manager: Gestor de usuarios
        survey_manager: Gestor de encuestas
    """
    print("📊 Analizando datos y generando reportes...")
    
    # Cargar datos de usuarios
    users_data = data_processor.json_handler.load_json("users.json", "users")
    if users_data:
        print(f"  📄 Usuarios cargados: {len(users_data)}")
        
        # Convertir a CSV para análisis
        users_list = list(users_data.values()) if isinstance(users_data, dict) else users_data
        data_processor.csv_handler.save_csv(users_list, "users_analysis.csv", "processed")
        
        # Generar estadísticas de usuarios
        user_stats = user_manager.get_user_statistics()
        print(f"  📈 Estadísticas de usuarios: {user_stats}")
    
    # Cargar y analizar respuestas de encuestas
    survey_responses = data_processor.json_handler.load_multiple_json("survey_response_*.json", "surveys")
    if survey_responses:
        print(f"  📋 Respuestas de encuestas cargadas: {len(survey_responses)}")
        
        # Guardar todas las respuestas en un CSV
        data_processor.csv_handler.save_csv(survey_responses, "survey_responses_analysis.csv", "processed")
        
        # Análizar patrones de riesgo
        high_risk_responses = data_processor.filter_data(
            survey_responses,
            {"risk_score": {">=": 7}}
        )
        
        print(f"  ⚠️  Respuestas de alto riesgo identificadas: {len(high_risk_responses)}")
        
        if high_risk_responses:
            data_processor.json_handler.save_json(
                high_risk_responses, 
                "high_risk_alerts.json", 
                "processed"
            )
    
    # Generar reporte resumen
    if users_data and survey_responses:
        combined_data = []
        
        # Combinar datos de usuarios con sus respuestas
        for response in survey_responses:
            user_id = response.get("user_id")
            if user_id in users_data:
                combined_record = {
                    **users_data[user_id],
                    **response
                }
                combined_data.append(combined_record)
        
        if combined_data:
            data_processor.generate_summary_report(combined_data, "platform_summary_report.json")
            print("  📋 Reporte resumen generado")
    
    print("✅ Análisis de datos completado\n")


def demonstrate_risk_detection(survey_manager: SurveyManager):
    """
    Demuestra el sistema de detección de riesgo.
    
    Args:
        survey_manager: Gestor de encuestas
    """
    print("🚨 Demostrando sistema de detección de riesgo...")
    
    # Obtener todas las encuestas disponibles
    available_surveys = list(survey_manager.surveys.keys())
    
    if not available_surveys:
        print("  ⚠️  No hay encuestas disponibles para analizar")
        return
    
    # Analizar cada encuesta
    for survey_id in available_surveys:
        print(f"\n  📊 Analizando encuesta: {survey_id}")
        risk_analysis = survey_manager.analyze_responses(survey_id)
        
        if risk_analysis and "message" not in risk_analysis:
            print(f"    - Total de respuestas: {risk_analysis.get('total_responses', 0)}")
            print(f"    - Duración promedio: {risk_analysis.get('average_duration', 0):.1f} minutos")
            
            # Mostrar indicadores de riesgo si existen
            risk_indicators = risk_analysis.get("risk_indicators", [])
            if risk_indicators:
                print(f"    ⚠️  Indicadores de riesgo detectados: {len(risk_indicators)}")
            else:
                print("    ✅ No se detectaron indicadores de riesgo críticos")
        else:
            print(f"    📝 {risk_analysis.get('message', 'Sin datos para analizar')}")
    
    print("\n✅ Detección de riesgo completada\n")


def main():
    """Función principal que ejecuta la demostración completa."""
    print("🚀 DEMOSTRACIÓN INTEGRAL DEL SISTEMA")
    print("=" * 50)
    print("Plataforma de Monitoreo Emocional para Jóvenes Vulnerables")
    print("=" * 50)
    print()
    
    # Inicializar componentes
    print("🔧 Inicializando componentes del sistema...")
    user_manager = UserManager()
    survey_manager = SurveyManager()
    data_processor = DataProcessor()
    print("✅ Componentes inicializados\n")
    
    # 1. Crear usuarios de muestra
    user_ids = create_sample_users(user_manager, 15)
    
    # 2. Generar respuestas de encuestas
    generate_survey_responses(survey_manager, user_ids, 30)
    
    # 3. Analizar datos y generar reportes
    analyze_data_and_generate_reports(data_processor, user_manager, survey_manager)
    
    # 4. Demostrar detección de riesgo
    demonstrate_risk_detection(survey_manager)
    
    # 5. Mostrar resumen final
    print("📈 RESUMEN FINAL DE LA DEMOSTRACIÓN")
    print("-" * 40)
    
    # Estadísticas finales
    final_stats = user_manager.get_user_statistics()
    print(f"👥 Total de usuarios registrados: {final_stats.get('total_users', 0)}")
    print(f"📊 Edad promedio: {final_stats.get('average_age', 0):.1f} años")
    print(f"📍 Ubicaciones representadas: {len(final_stats.get('locations', []))}")
    print(f"⚖️  Distribución de género: {final_stats.get('gender_distribution', {})}")
    
    # Verificar archivos generados
    print("\n📁 Archivos generados:")
    data_files = [
        "data/users/users.json",
        "data/processed/users_analysis.csv",
        "data/processed/survey_responses_analysis.csv",
        "data/processed/platform_summary_report.json"
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (no generado)")
    
    print("\n🎉 ¡Demostración completada exitosamente!")
    print("La plataforma está lista para la primera entrega.")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()