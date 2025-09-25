"""
Aplicación Web Flask para la Plataforma de Bienestar Emocional
Proporciona una interfaz web para registro de usuarios y encuestas
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sys
import os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.user_management import UserManager
from core.survey_system import SurveyManager
from core.data_handler import DataProcessor, JSONHandler
# Las funciones de análisis están en survey_system.py

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Inicializar componentes
user_manager = UserManager()
survey_manager = SurveyManager()
data_processor = DataProcessor()
json_handler = JSONHandler()
# Las funciones de análisis están integradas en survey_manager

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/registro')
def registro():
    """Página de registro de usuarios"""
    return render_template('registro.html')

@app.route('/registro', methods=['POST'])
def procesar_registro():
    """Procesar el registro de un nuevo usuario"""
    try:
        user_data = {
            'username': request.form['username'],
            'email': request.form['email'],
            'age': int(request.form['age']),
            'gender': request.form['gender'],
            'location': request.form['location']
        }
        
        success, message, user = user_manager.register_user(user_data)
        
        if success:
            flash(f'¡Usuario registrado exitosamente! ID: {user.user_id}', 'success')
            return redirect(url_for('encuestas', user_id=user.user_id))
        else:
            flash(f'Error en el registro: {message}', 'error')
            return redirect(url_for('registro'))
            
    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')
        return redirect(url_for('registro'))

@app.route('/encuestas')
def encuestas():
    """Página de encuestas disponibles"""
    user_id = request.args.get('user_id')
    surveys = survey_manager.get_available_surveys()
    return render_template('encuestas.html', surveys=surveys, user_id=user_id)

@app.route('/encuesta/<survey_id>')
def mostrar_encuesta(survey_id):
    """Mostrar formulario de encuesta específica"""
    user_id = request.args.get('user_id')
    
    survey = survey_manager.get_survey_by_id(survey_id)
    if not survey:
        flash('Encuesta no encontrada', 'error')
        return redirect(url_for('encuestas'))
    
    return render_template('formulario_encuesta.html', survey=survey, user_id=user_id)

@app.route('/encuesta/<survey_id>', methods=['POST'])
def procesar_encuesta(survey_id):
    """Procesar respuestas de encuesta"""
    user_id = request.form['user_id']
    
    try:
        # Recopilar respuestas del formulario
        answers = {}
        for key, value in request.form.items():
            if key.startswith('question_'):
                question_id = key.replace('question_', '')
                answers[question_id] = value
        
        # Enviar respuestas
        success, message, response = survey_manager.submit_response(
            user_id=user_id,
            survey_id=survey_id,
            answers=answers,
            start_time=datetime.now()
        )
        
        if success:
            flash('¡Encuesta completada exitosamente!', 'success')
            return redirect(url_for('resultados', response_id=response.response_id))
        else:
            flash(f'Error al procesar encuesta: {message}', 'error')
            return redirect(url_for('encuestas', user_id=user_id))
            
    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')
        return redirect(url_for('encuestas', user_id=user_id))

@app.route('/resultados')
def resultados():
    """Mostrar resultados de encuesta"""
    response_id = request.args.get('response_id')
    return render_template('resultados.html', response_id=response_id)

@app.route('/dashboard')
def dashboard():
    """Dashboard administrativo con estadísticas"""
    try:
        # Obtener estadísticas básicas
        stats = {
            'total_users': len(user_manager.get_all_users()),
            'total_responses': len(survey_manager.get_all_responses()),
            'available_surveys': len(survey_manager.get_available_surveys())
        }
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        flash(f'Error cargando dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/stats')
def api_stats():
    """API endpoint para estadísticas en tiempo real"""
    try:
        stats = {
            'users': len(user_manager.get_all_users()),
            'responses': len(survey_manager.get_all_responses()),
            'surveys': len(survey_manager.get_available_surveys()),
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Iniciando servidor web de la Plataforma de Bienestar Emocional...")
    print("📍 Accede a: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)