#!/usr/bin/env python3
"""
Gestor de usuarios con base de datos MySQL para la Plataforma de Bienestar Emocional.
"""

import uuid
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from .database_manager import DatabaseManager

# Configurar logging
logger = logging.getLogger(__name__)

class User:
    """Clase para representar un usuario."""
    
    def __init__(self, user_id: str, username: str, email: str, age: int, gender: str, location: str, nombre: str = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.age = age
        self.gender = gender
        self.location = location
        self.nombre = nombre or username
        self.created_at = datetime.now()

class UserManagerDB:
    """Gestor de usuarios con almacenamiento en base de datos MySQL."""
    
    def __init__(self):
        """Inicializa el gestor con conexión a base de datos."""
        self.db_manager = DatabaseManager()
        self._ensure_users_table()
    
    def _ensure_users_table(self):
        """Asegura que la tabla de usuarios exista."""
        try:
            # Verificar si la tabla usuarios existe, si no, crearla
            create_table_query = """
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
                INDEX idx_username (username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            self.db_manager.execute_query(create_table_query)
        except Exception as e:
            print(f"Error creando tabla de usuarios: {e}")
    
    def _generate_user_id(self) -> str:
        """
        Genera un ID único para el usuario.
        
        Returns:
            str: ID único del usuario
        """
        return f"user_{uuid.uuid4().hex[:8]}"
    
    def register_user(self, user_data: Dict[str, Any]) -> Tuple[bool, str, Optional[User]]:
        """
        Registra un nuevo usuario en la base de datos.
        
        Args:
            user_data: Diccionario con los datos del usuario
            
        Returns:
            Tuple[bool, str, Optional[User]]: (éxito, mensaje, usuario)
        """
        try:
            # Validar datos requeridos - usar los nombres correctos de los campos
            required_fields = ['username', 'email', 'edad', 'genero', 'ubicacion']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    return False, f"Campo requerido faltante: {field}", None
            
            # Verificar si el email ya existe
            if self._email_exists(user_data['email']):
                return False, "El email ya está registrado", None
            
            # Verificar si el username ya existe
            if self._username_exists(user_data['username']):
                return False, "El nombre de usuario ya está registrado", None
            
            # Generar ID único
            user_id = self._generate_user_id()
            
            # Insertar usuario en la base de datos
            insert_query = """
            INSERT INTO usuarios (user_id, nombre, username, email, password_hash, edad, genero, ubicacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Generar hash de contraseña
            password = user_data.get('password', 'default123')
            password_hash = self._hash_password(password)
            
            params = (
                user_id,
                user_data.get('nombre', user_data['username']),  # Si no hay nombre, usar username
                user_data['username'],
                user_data['email'],
                password_hash,
                int(user_data['edad']),
                user_data['genero'],
                user_data['ubicacion']
            )
            
            if self.db_manager.execute_query(insert_query, params):
                # Crear objeto User
                user = User(
                    user_id=user_id,
                    username=user_data['username'],
                    email=user_data['email'],
                    age=int(user_data['edad']),
                    gender=user_data['genero'],
                    location=user_data['ubicacion'],
                    nombre=user_data.get('nombre', user_data['username'])
                )
                
                return True, "Usuario registrado exitosamente", user
            else:
                return False, "Error al guardar el usuario en la base de datos", None
                
        except Exception as e:
            print(f"Error registrando usuario: {e}")
            return False, f"Error inesperado: {str(e)}", None
    
    def _email_exists(self, email: str) -> bool:
        """
        Verifica si un email ya está registrado.
        
        Args:
            email: Email a verificar
            
        Returns:
            bool: True si el email existe, False en caso contrario
        """
        try:
            query = "SELECT COUNT(*) as count FROM usuarios WHERE email = %s"
            if self.db_manager.connect():
                cursor = self.db_manager.connection.cursor(dictionary=True)
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                cursor.close()
                return result['count'] > 0 if result else False
        except Exception as e:
            print(f"Error verificando email: {e}")
            return False
        finally:
            self.db_manager.disconnect()
    
    def _username_exists(self, username: str) -> bool:
        """
        Verifica si un username ya está registrado.
        
        Args:
            username: Username a verificar
            
        Returns:
            bool: True si el username existe, False en caso contrario
        """
        try:
            query = "SELECT COUNT(*) as count FROM usuarios WHERE username = %s"
            if self.db_manager.connect():
                cursor = self.db_manager.connection.cursor(dictionary=True)
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                cursor.close()
                return result['count'] > 0 if result else False
        except Exception as e:
            print(f"Error verificando username: {e}")
            return False
        finally:
            self.db_manager.disconnect()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Optional[User]: Usuario si existe, None en caso contrario
        """
        try:
            query = "SELECT * FROM usuarios WHERE user_id = %s AND activo = TRUE"
            if self.db_manager.connect():
                cursor = self.db_manager.connection.cursor(dictionary=True)
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    return User(
                        user_id=result['user_id'],
                        username=result['username'],
                        email=result['email'],
                        age=result['edad'],
                        gender=result['genero'],
                        location=result['ubicacion']
                    )
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
        finally:
            self.db_manager.disconnect()
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Optional[User]: Usuario si existe, None en caso contrario
        """
        try:
            query = "SELECT * FROM usuarios WHERE email = %s AND activo = TRUE"
            if self.db_manager.connect():
                cursor = self.db_manager.connection.cursor(dictionary=True)
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    return User(
                        user_id=result['user_id'],
                        username=result['username'],
                        email=result['email'],
                        age=result['edad'],
                        gender=result['genero'],
                        location=result['ubicacion']
                    )
        except Exception as e:
            print(f"Error obteniendo usuario por email: {e}")
        finally:
            self.db_manager.disconnect()
        
        return None
    
    def get_all_users(self) -> List[User]:
        """
        Obtiene todos los usuarios activos.
        
        Returns:
            List[User]: Lista de usuarios
        """
        users = []
        try:
            query = "SELECT * FROM usuarios WHERE activo = TRUE ORDER BY fecha_registro DESC"
            if self.db_manager.connect():
                cursor = self.db_manager.connection.cursor(dictionary=True)
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                
                for result in results:
                    user = User(
                        user_id=result['user_id'],
                        username=result['username'],
                        email=result['email'],
                        age=result['edad'],
                        gender=result['genero'],
                        location=result['ubicacion']
                    )
                    users.append(user)
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
        finally:
            self.db_manager.disconnect()
        
        return users
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        Actualiza los datos de un usuario.
        
        Args:
            user_id: ID del usuario
            user_data: Datos a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Construir query dinámicamente basado en los campos proporcionados
            allowed_fields = ['nombre', 'username', 'email', 'edad', 'genero', 'ubicacion']
            update_fields = []
            params = []
            
            for field, value in user_data.items():
                if field in allowed_fields and value is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                return False
            
            query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE user_id = %s"
            params.append(user_id)
            
            return self.db_manager.execute_query(query, tuple(params))
            
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        Elimina (desactiva) un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            query = "UPDATE usuarios SET activo = FALSE WHERE user_id = %s"
            return self.db_manager.execute_query(query, (user_id,))
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            return False
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de usuarios.
        
        Returns:
            Dict[str, Any]: Estadísticas de usuarios
        """
        try:
            if self.db_manager.connect():
                cursor = self.db_manager.connection.cursor(dictionary=True)
                
                # Total de usuarios activos
                cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE activo = TRUE")
                total_result = cursor.fetchone()
                total_users = total_result['total'] if total_result else 0
                
                # Usuarios registrados hoy
                cursor.execute("""
                    SELECT COUNT(*) as today 
                    FROM usuarios 
                    WHERE DATE(fecha_registro) = CURDATE() AND activo = TRUE
                """)
                today_result = cursor.fetchone()
                users_today = today_result['today'] if today_result else 0
                
                # Distribución por género
                cursor.execute("""
                    SELECT genero, COUNT(*) as count 
                    FROM usuarios 
                    WHERE activo = TRUE 
                    GROUP BY genero
                """)
                gender_results = cursor.fetchall()
                gender_distribution = {result['genero']: result['count'] for result in gender_results}
                
                cursor.close()
                
                return {
                    'total_users': total_users,
                    'users_today': users_today,
                    'gender_distribution': gender_distribution
                }
        except Exception as e:
            print(f"Error obteniendo estadísticas de usuarios: {e}")
        finally:
            self.db_manager.disconnect()
        
        return {
            'total_users': 0,
            'users_today': 0,
            'gender_distribution': {}
        }
    
    def _hash_password(self, password: str) -> str:
        """
        Genera un hash seguro de la contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.
        
        Args:
            password: Contraseña en texto plano
            password_hash: Hash almacenado
            
        Returns:
            bool: True si la contraseña es correcta
        """
        return self._hash_password(password) == password_hash
    
    def get_user_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """
        Obtiene un usuario por su username o email.
        
        Args:
            username_or_email: Username o email del usuario
            
        Returns:
            Optional[User]: Usuario si existe, None en caso contrario
        """
        try:
            query = """
            SELECT * FROM usuarios 
            WHERE (username = %s OR email = %s) AND activo = TRUE
            """
            if self.db_manager.connect():
                cursor = self.db_manager.connection.cursor(dictionary=True)
                cursor.execute(query, (username_or_email, username_or_email))
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    user = User(
                        user_id=result['user_id'],
                        username=result['username'],
                        email=result['email'],
                        age=result['edad'],
                        gender=result['genero'],
                        location=result['ubicacion'],
                        nombre=result['nombre']
                    )
                    # Agregar el password hash para verificación
                    user.password = result['password_hash']
                    return user
        except Exception as e:
            print(f"Error obteniendo usuario por username/email: {e}")
        finally:
            self.db_manager.disconnect()
        
        return None