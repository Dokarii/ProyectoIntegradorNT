"""
Aplicación Web Flask para la Plataforma de Bienestar Emocional
Proporciona una interfaz web para registro de usuarios y encuestas
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import sys
import os
from datetime import datetime
import hashlib
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.user_manager_db import UserManagerDB
from core.survey_manager_db import SurveyManagerDB
from core.data_handler import DataProcessor, JSONHandler
# Las funciones de análisis están en survey_system.py

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiar_en_produccion'

# Inicializar componentes
user_manager = UserManagerDB()  # Usando la nueva versión con base de datos
survey_manager = SurveyManagerDB()  # Usando la nueva versión con base de datos
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
        # Validar que las contraseñas coincidan
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('registro'))
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('registro'))
        
        user_data = {
            'nombre': request.form['username'],  # El formulario HTML usa 'username'
            'username': request.form['username'],
            'email': request.form['email'],
            'password': password,  # Usar la contraseña del formulario
            'edad': int(request.form['age']),  # El formulario HTML usa 'age'
            'genero': request.form['gender'],  # El formulario HTML usa 'gender'
            'ubicacion': request.form['location']  # El formulario HTML usa 'location'
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
    
    # Debug: Verificar qué devuelve survey_manager
    surveys = survey_manager.get_available_surveys()
    print(f"DEBUG: Número de encuestas encontradas: {len(surveys)}")
    for i, survey in enumerate(surveys):
        print(f"DEBUG: Encuesta {i+1}: {survey.title} (ID: {survey.survey_id})")
    
    return render_template('encuestas.html', surveys=surveys, user_id=user_id)

@app.route('/encuesta/<survey_id>')
def mostrar_encuesta(survey_id):
    """Mostrar formulario de encuesta específica"""
    user_id = request.args.get('user_id')
    
    survey = survey_manager.get_survey(survey_id)  # Método actualizado
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
        
        # Enviar respuestas usando el nuevo método
        success = survey_manager.save_response(
            user_id=user_id,
            survey_id=survey_id,
            responses=answers
        )
        
        if success:
            flash('¡Encuesta completada exitosamente!', 'success')
            return redirect(url_for('dashboard'))  # Redirigir al dashboard
        else:
            flash('Error al procesar encuesta', 'error')
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
        # Obtener estadísticas usando el nuevo método
        stats = survey_manager.get_statistics()
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        flash(f'Error cargando dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/stats')
def api_stats():
    """API endpoint para estadísticas en tiempo real"""
    try:
        # Usar las estadísticas de la base de datos
        stats = survey_manager.get_statistics()
        stats['timestamp'] = datetime.now().isoformat()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== RUTAS DE AUTENTICACIÓN =====

@app.route('/login')
def login():
    """Página de inicio de sesión"""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def procesar_login():
    """Procesar el inicio de sesión"""
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña', 'error')
            return redirect(url_for('login'))
        
        # Buscar usuario por username o email
        user = user_manager.get_user_by_username_or_email(username)
        
        if user and user_manager.verify_password(password, user.password):
            # Login exitoso - crear sesión
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['logged_in'] = True
            
            flash(f'¡Bienvenido {user.nombre}!', 'success')
            return redirect(url_for('encuestas', user_id=user.user_id))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            return redirect(url_for('login'))
            
    except Exception as e:
        flash(f'Error en el inicio de sesión: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('index'))

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

if __name__ == '__main__':
    print("🌐 Iniciando servidor web de la Plataforma de Bienestar Emocional...")
    print("📍 Accede a: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)