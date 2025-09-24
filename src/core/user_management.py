"""
Módulo de Gestión de Usuarios
============================

Este módulo proporciona funcionalidades para el registro, validación y gestión
de usuarios de la plataforma de monitoreo emocional.

Autor: Equipo de Desarrollo
Fecha: 2024
Versión: 1.0
"""

import json
import csv
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class EmotionalProfile:
    """Clase para representar el perfil emocional de un usuario."""
    
    stress_level: int = 5  # Escala 1-10
    anxiety_level: int = 5  # Escala 1-10
    mood_stability: int = 5  # Escala 1-10
    social_support: int = 5  # Escala 1-10
    coping_skills: int = 5  # Escala 1-10
    risk_factors: List[str] = None
    protective_factors: List[str] = None
    
    def __post_init__(self):
        """Inicializa listas vacías si no se proporcionan."""
        if self.risk_factors is None:
            self.risk_factors = []
        if self.protective_factors is None:
            self.protective_factors = []
    
    def calculate_risk_score(self) -> float:
        """
        Calcula un puntaje de riesgo basado en el perfil emocional.
        
        Returns:
            float: Puntaje de riesgo (0-100, donde 100 es mayor riesgo)
        """
        # Factores de riesgo (valores altos indican mayor riesgo)
        risk_score = (self.stress_level + self.anxiety_level) * 5
        
        # Factores protectores (valores altos reducen el riesgo)
        protective_score = (self.mood_stability + self.social_support + 
                          self.coping_skills) * 3.33
        
        # Ajuste por factores adicionales
        risk_adjustment = len(self.risk_factors) * 5
        protective_adjustment = len(self.protective_factors) * 3
        
        final_score = max(0, min(100, risk_score + risk_adjustment - 
                                protective_score - protective_adjustment))
        
        return round(final_score, 2)


@dataclass
class User:
    """Clase para representar un usuario del sistema."""
    
    user_id: str
    username: str
    email: str
    age: int
    gender: str
    location: str
    registration_date: str
    emotional_profile: EmotionalProfile
    is_active: bool = True
    consent_given: bool = False
    
    def to_dict(self) -> Dict:
        """Convierte el usuario a diccionario para serialización."""
        user_dict = asdict(self)
        user_dict['emotional_profile'] = asdict(self.emotional_profile)
        return user_dict
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Crea un usuario desde un diccionario."""
        emotional_profile_data = data.pop('emotional_profile')
        emotional_profile = EmotionalProfile(**emotional_profile_data)
        return cls(emotional_profile=emotional_profile, **data)


class UserValidator:
    """Clase para validar datos de usuarios."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida el formato del email.
        
        Args:
            email (str): Email a validar
            
        Returns:
            bool: True si el email es válido
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_age(age: int) -> bool:
        """
        Valida que la edad esté en el rango permitido.
        
        Args:
            age (int): Edad a validar
            
        Returns:
            bool: True si la edad es válida (13-25 años)
        """
        return 13 <= age <= 25
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Valida el formato del nombre de usuario.
        
        Args:
            username (str): Nombre de usuario a validar
            
        Returns:
            bool: True si el username es válido
        """
        # Solo letras, números y guiones bajos, 3-20 caracteres
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None
    
    @classmethod
    def validate_user_data(cls, user_data: Dict) -> Tuple[bool, List[str]]:
        """
        Valida todos los datos de un usuario.
        
        Args:
            user_data (Dict): Datos del usuario a validar
            
        Returns:
            Tuple[bool, List[str]]: (es_válido, lista_de_errores)
        """
        errors = []
        
        # Validar campos requeridos
        required_fields = ['username', 'email', 'age', 'gender', 'location']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                errors.append(f"El campo '{field}' es requerido")
        
        # Validaciones específicas
        if 'email' in user_data and not cls.validate_email(user_data['email']):
            errors.append("El formato del email no es válido")
        
        if 'age' in user_data and not cls.validate_age(user_data['age']):
            errors.append("La edad debe estar entre 13 y 25 años")
        
        if 'username' in user_data and not cls.validate_username(user_data['username']):
            errors.append("El username debe tener 3-20 caracteres (letras, números, _)")
        
        return len(errors) == 0, errors


class UserManager:
    """Clase principal para gestionar usuarios del sistema."""
    
    def __init__(self, data_path: str = "data/users/"):
        """
        Inicializa el gestor de usuarios.
        
        Args:
            data_path (str): Ruta donde se almacenan los datos de usuarios
        """
        self.data_path = data_path
        self.users: Dict[str, User] = {}
        self.validator = UserValidator()
    
    def generate_user_id(self, username: str, email: str) -> str:
        """
        Genera un ID único para el usuario.
        
        Args:
            username (str): Nombre de usuario
            email (str): Email del usuario
            
        Returns:
            str: ID único del usuario
        """
        data = f"{username}_{email}_{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def register_user(self, user_data: Dict) -> Tuple[bool, str, Optional[User]]:
        """
        Registra un nuevo usuario en el sistema.
        
        Args:
            user_data (Dict): Datos del usuario a registrar
            
        Returns:
            Tuple[bool, str, Optional[User]]: (éxito, mensaje, usuario_creado)
        """
        # Validar datos
        is_valid, errors = self.validator.validate_user_data(user_data)
        if not is_valid:
            return False, f"Errores de validación: {', '.join(errors)}", None
        
        # Verificar si el usuario ya existe
        if self.user_exists(user_data['username'], user_data['email']):
            return False, "El usuario ya existe", None
        
        # Crear perfil emocional inicial
        emotional_profile = EmotionalProfile()
        
        # Crear usuario
        user_id = self.generate_user_id(user_data['username'], user_data['email'])
        user = User(
            user_id=user_id,
            username=user_data['username'],
            email=user_data['email'],
            age=user_data['age'],
            gender=user_data['gender'],
            location=user_data['location'],
            registration_date=datetime.now().isoformat(),
            emotional_profile=emotional_profile,
            consent_given=user_data.get('consent_given', False)
        )
        
        # Almacenar usuario
        self.users[user_id] = user
        
        # Guardar en archivo
        self.save_user_to_file(user)
        
        return True, f"Usuario {user.username} registrado exitosamente", user
    
    def user_exists(self, username: str, email: str) -> bool:
        """
        Verifica si un usuario ya existe.
        
        Args:
            username (str): Nombre de usuario
            email (str): Email del usuario
            
        Returns:
            bool: True si el usuario existe
        """
        for user in self.users.values():
            if user.username == username or user.email == email:
                return True
        return False
    
    def save_user_to_file(self, user: User) -> None:
        """
        Guarda un usuario en archivo JSON.
        
        Args:
            user (User): Usuario a guardar
        """
        import os
        os.makedirs(self.data_path, exist_ok=True)
        
        filename = f"{self.data_path}user_{user.user_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(user.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_user_from_file(self, user_id: str) -> Optional[User]:
        """
        Carga un usuario desde archivo JSON.
        
        Args:
            user_id (str): ID del usuario a cargar
            
        Returns:
            Optional[User]: Usuario cargado o None si no existe
        """
        filename = f"{self.data_path}user_{user_id}.json"
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return User.from_dict(data)
        except FileNotFoundError:
            return None
    
    def export_users_to_csv(self, filename: str = None) -> str:
        """
        Exporta todos los usuarios a un archivo CSV.
        
        Args:
            filename (str): Nombre del archivo CSV (opcional)
            
        Returns:
            str: Ruta del archivo creado
        """
        if filename is None:
            filename = f"{self.data_path}users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'user_id', 'username', 'email', 'age', 'gender', 'location',
                'registration_date', 'is_active', 'consent_given', 'risk_score'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for user in self.users.values():
                row = {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'age': user.age,
                    'gender': user.gender,
                    'location': user.location,
                    'registration_date': user.registration_date,
                    'is_active': user.is_active,
                    'consent_given': user.consent_given,
                    'risk_score': user.emotional_profile.calculate_risk_score()
                }
                writer.writerow(row)
        
        return filename
    
    def get_user_statistics(self) -> Dict:
        """
        Obtiene estadísticas generales de los usuarios.
        
        Returns:
            Dict: Estadísticas de usuarios
        """
        if not self.users:
            return {"total_users": 0}
        
        ages = [user.age for user in self.users.values()]
        risk_scores = [user.emotional_profile.calculate_risk_score() 
                      for user in self.users.values()]
        
        stats = {
            "total_users": len(self.users),
            "active_users": sum(1 for user in self.users.values() if user.is_active),
            "average_age": sum(ages) / len(ages),
            "age_range": {"min": min(ages), "max": max(ages)},
            "average_risk_score": sum(risk_scores) / len(risk_scores),
            "high_risk_users": sum(1 for score in risk_scores if score > 70),
            "gender_distribution": self._get_gender_distribution(),
            "consent_rate": sum(1 for user in self.users.values() 
                              if user.consent_given) / len(self.users) * 100
        }
        
        return stats
    
    def _get_gender_distribution(self) -> Dict[str, int]:
        """Obtiene la distribución por género."""
        distribution = {}
        for user in self.users.values():
            gender = user.gender
            distribution[gender] = distribution.get(gender, 0) + 1
        return distribution


def simulate_user_registration(num_users: int = 10) -> List[User]:
    """
    Simula el registro de usuarios para pruebas.
    
    Args:
        num_users (int): Número de usuarios a simular
        
    Returns:
        List[User]: Lista de usuarios creados
    """
    import random
    
    user_manager = UserManager()
    created_users = []
    
    # Datos de ejemplo
    names = ["Ana", "Carlos", "María", "José", "Laura", "Diego", "Sofia", "Miguel", 
             "Valentina", "Andrés", "Camila", "Santiago", "Isabella", "Mateo", "Lucía"]
    
    locations = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", 
                "Bucaramanga", "Pereira", "Manizales", "Ibagué", "Villavicencio"]
    
    genders = ["Masculino", "Femenino", "No binario", "Prefiero no decir"]
    
    for i in range(num_users):
        name = random.choice(names)
        user_data = {
            "username": f"{name.lower()}{random.randint(100, 999)}",
            "email": f"{name.lower()}{random.randint(10, 99)}@email.com",
            "age": random.randint(13, 25),
            "gender": random.choice(genders),
            "location": random.choice(locations),
            "consent_given": random.choice([True, False])
        }
        
        success, message, user = user_manager.register_user(user_data)
        if success and user:
            created_users.append(user)
            print(f"✓ Usuario creado: {user.username} (ID: {user.user_id})")
        else:
            print(f"✗ Error creando usuario: {message}")
    
    # Mostrar estadísticas
    stats = user_manager.get_user_statistics()
    print(f"\n📊 Estadísticas de usuarios creados:")
    print(f"Total de usuarios: {stats['total_users']}")
    print(f"Edad promedio: {stats['average_age']:.1f} años")
    print(f"Puntaje de riesgo promedio: {stats['average_risk_score']:.1f}")
    print(f"Usuarios de alto riesgo: {stats['high_risk_users']}")
    
    # Exportar a CSV
    csv_file = user_manager.export_users_to_csv()
    print(f"📄 Datos exportados a: {csv_file}")
    
    return created_users


if __name__ == "__main__":
    print("🚀 Iniciando simulación de registro de usuarios...")
    simulate_user_registration(15)
    print("✅ Simulación completada!")