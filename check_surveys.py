import sys
import os
sys.path.append('src')
from core.database_manager import DatabaseManager

print("🔍 Verificando encuestas en la base de datos...")
db = DatabaseManager()
if not db.connect():
    print("❌ Error conectando a la base de datos")
    exit(1)

surveys = db.get_all_surveys()
print(f"📊 Encuestas encontradas: {len(surveys)}")

for survey in surveys:
    print(f"  - {survey['title']} (ID: {survey['survey_id']})")
    questions = db.get_survey_questions(survey['survey_id'])
    print(f"    Preguntas: {len(questions)}")
    for i, question in enumerate(questions[:3], 1):  # Mostrar solo las primeras 3
        print(f"      {i}. {question['text'][:50]}...")
    if len(questions) > 3:
        print(f"      ... y {len(questions) - 3} más")
    print()