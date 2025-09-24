"""
Manejador de Datos
==================

Este módulo proporciona funcionalidades para el manejo eficiente y seguro
de archivos CSV y JSON, incluyendo operaciones de lectura, escritura,
validación y transformación de datos.

Autor: Equipo de Desarrollo
Fecha: 2024
Versión: 1.0
"""

import json
import csv
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import logging
from dataclasses import asdict


class DataValidator:
    """Clase para validar datos antes de procesarlos."""
    
    @staticmethod
    def validate_json_structure(data: Dict, required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Valida que un diccionario tenga los campos requeridos.
        
        Args:
            data: Diccionario a validar
            required_fields: Lista de campos requeridos
            
        Returns:
            Tuple[bool, List[str]]: (es_válido, errores)
        """
        errors = []
        
        if not isinstance(data, dict):
            return False, ["Los datos deben ser un diccionario"]
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo requerido faltante: {field}")
            elif data[field] is None or data[field] == "":
                errors.append(f"Campo vacío: {field}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_csv_headers(headers: List[str], expected_headers: List[str]) -> Tuple[bool, List[str]]:
        """
        Valida que los headers de un CSV sean los esperados.
        
        Args:
            headers: Headers encontrados
            expected_headers: Headers esperados
            
        Returns:
            Tuple[bool, List[str]]: (es_válido, errores)
        """
        errors = []
        
        missing_headers = set(expected_headers) - set(headers)
        if missing_headers:
            errors.append(f"Headers faltantes: {', '.join(missing_headers)}")
        
        extra_headers = set(headers) - set(expected_headers)
        if extra_headers:
            errors.append(f"Headers adicionales: {', '.join(extra_headers)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_data(data: Any) -> Any:
        """
        Sanitiza datos para prevenir problemas de seguridad.
        
        Args:
            data: Datos a sanitizar
            
        Returns:
            Datos sanitizados
        """
        if isinstance(data, str):
            # Remover caracteres potencialmente peligrosos
            dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
            for char in dangerous_chars:
                data = data.replace(char, '')
            return data.strip()
        
        elif isinstance(data, dict):
            return {key: DataValidator.sanitize_data(value) 
                   for key, value in data.items()}
        
        elif isinstance(data, list):
            return [DataValidator.sanitize_data(item) for item in data]
        
        return data


class JSONHandler:
    """Clase para manejar operaciones con archivos JSON."""
    
    def __init__(self, base_path: str = "data/"):
        """
        Inicializa el manejador JSON.
        
        Args:
            base_path: Ruta base para archivos JSON
        """
        self.base_path = Path(base_path)
        self.validator = DataValidator()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura el logging para el manejador."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def save_json(self, data: Any, filename: str, subfolder: str = "") -> bool:
        """
        Guarda datos en un archivo JSON.
        
        Args:
            data: Datos a guardar
            filename: Nombre del archivo
            subfolder: Subcarpeta opcional
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Crear ruta completa
            if subfolder:
                full_path = self.base_path / subfolder
            else:
                full_path = self.base_path
            
            full_path.mkdir(parents=True, exist_ok=True)
            file_path = full_path / filename
            
            # Sanitizar datos
            clean_data = self.validator.sanitize_data(data)
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Archivo JSON guardado: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando JSON {filename}: {str(e)}")
            return False
    
    def load_json(self, filename: str, subfolder: str = "") -> Optional[Any]:
        """
        Carga datos desde un archivo JSON.
        
        Args:
            filename: Nombre del archivo
            subfolder: Subcarpeta opcional
            
        Returns:
            Datos cargados o None si hay error
        """
        try:
            if subfolder:
                file_path = self.base_path / subfolder / filename
            else:
                file_path = self.base_path / filename
            
            if not file_path.exists():
                self.logger.warning(f"Archivo no encontrado: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Archivo JSON cargado: {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error cargando JSON {filename}: {str(e)}")
            return None
    
    def load_multiple_json(self, pattern: str, subfolder: str = "") -> List[Dict]:
        """
        Carga múltiples archivos JSON que coincidan con un patrón.
        
        Args:
            pattern: Patrón de archivos (ej: "user_*.json")
            subfolder: Subcarpeta opcional
            
        Returns:
            Lista de datos cargados
        """
        try:
            if subfolder:
                search_path = self.base_path / subfolder
            else:
                search_path = self.base_path
            
            files = list(search_path.glob(pattern))
            data_list = []
            
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_source_file'] = file_path.name
                    data_list.append(data)
            
            self.logger.info(f"Cargados {len(data_list)} archivos JSON con patrón: {pattern}")
            return data_list
            
        except Exception as e:
            self.logger.error(f"Error cargando múltiples JSON: {str(e)}")
            return []
    
    def merge_json_files(self, filenames: List[str], output_filename: str, 
                        subfolder: str = "") -> bool:
        """
        Combina múltiples archivos JSON en uno solo.
        
        Args:
            filenames: Lista de archivos a combinar
            output_filename: Nombre del archivo de salida
            subfolder: Subcarpeta opcional
            
        Returns:
            bool: True si se combinó exitosamente
        """
        try:
            merged_data = []
            
            for filename in filenames:
                data = self.load_json(filename, subfolder)
                if data:
                    if isinstance(data, list):
                        merged_data.extend(data)
                    else:
                        merged_data.append(data)
            
            return self.save_json(merged_data, output_filename, subfolder)
            
        except Exception as e:
            self.logger.error(f"Error combinando archivos JSON: {str(e)}")
            return False


class CSVHandler:
    """Clase para manejar operaciones con archivos CSV."""
    
    def __init__(self, base_path: str = "data/"):
        """
        Inicializa el manejador CSV.
        
        Args:
            base_path: Ruta base para archivos CSV
        """
        self.base_path = Path(base_path)
        self.validator = DataValidator()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura el logging para el manejador."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def save_csv(self, data: List[Dict], filename: str, subfolder: str = "") -> bool:
        """
        Guarda datos en un archivo CSV.
        
        Args:
            data: Lista de diccionarios a guardar
            filename: Nombre del archivo
            subfolder: Subcarpeta opcional
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            if not data:
                self.logger.warning("No hay datos para guardar en CSV")
                return False
            
            # Crear ruta completa
            if subfolder:
                full_path = self.base_path / subfolder
            else:
                full_path = self.base_path
            
            full_path.mkdir(parents=True, exist_ok=True)
            file_path = full_path / filename
            
            # Obtener headers de todos los diccionarios
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())
            
            fieldnames = sorted(list(all_keys))
            
            # Sanitizar datos
            clean_data = [self.validator.sanitize_data(item) for item in data]
            
            # Guardar archivo
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(clean_data)
            
            self.logger.info(f"Archivo CSV guardado: {file_path} ({len(data)} filas)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando CSV {filename}: {str(e)}")
            return False
    
    def load_csv(self, filename: str, subfolder: str = "") -> Optional[List[Dict]]:
        """
        Carga datos desde un archivo CSV.
        
        Args:
            filename: Nombre del archivo
            subfolder: Subcarpeta opcional
            
        Returns:
            Lista de diccionarios o None si hay error
        """
        try:
            if subfolder:
                file_path = self.base_path / subfolder / filename
            else:
                file_path = self.base_path / filename
            
            if not file_path.exists():
                self.logger.warning(f"Archivo no encontrado: {file_path}")
                return None
            
            data = []
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            self.logger.info(f"Archivo CSV cargado: {file_path} ({len(data)} filas)")
            return data
            
        except Exception as e:
            self.logger.error(f"Error cargando CSV {filename}: {str(e)}")
            return None
    
    def csv_to_pandas(self, filename: str, subfolder: str = "") -> Optional[pd.DataFrame]:
        """
        Carga un CSV directamente como DataFrame de pandas.
        
        Args:
            filename: Nombre del archivo
            subfolder: Subcarpeta opcional
            
        Returns:
            DataFrame o None si hay error
        """
        try:
            if subfolder:
                file_path = self.base_path / subfolder / filename
            else:
                file_path = self.base_path / filename
            
            if not file_path.exists():
                self.logger.warning(f"Archivo no encontrado: {file_path}")
                return None
            
            df = pd.read_csv(file_path, encoding='utf-8')
            self.logger.info(f"CSV cargado como DataFrame: {file_path} ({len(df)} filas)")
            return df
            
        except Exception as e:
            self.logger.error(f"Error cargando CSV como pandas: {str(e)}")
            return None
    
    def pandas_to_csv(self, df: pd.DataFrame, filename: str, subfolder: str = "") -> bool:
        """
        Guarda un DataFrame como archivo CSV.
        
        Args:
            df: DataFrame a guardar
            filename: Nombre del archivo
            subfolder: Subcarpeta opcional
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            if subfolder:
                full_path = self.base_path / subfolder
            else:
                full_path = self.base_path
            
            full_path.mkdir(parents=True, exist_ok=True)
            file_path = full_path / filename
            
            df.to_csv(file_path, index=False, encoding='utf-8')
            self.logger.info(f"DataFrame guardado como CSV: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando DataFrame como CSV: {str(e)}")
            return False


class DataProcessor:
    """Clase para procesar y transformar datos."""
    
    def __init__(self, base_path: str = "data/"):
        """
        Inicializa el procesador de datos.
        
        Args:
            base_path: Ruta base para archivos
        """
        self.json_handler = JSONHandler(base_path)
        self.csv_handler = CSVHandler(base_path)
        self.logger = logging.getLogger(__name__)
    
    def json_to_csv(self, json_filename: str, csv_filename: str, 
                   json_subfolder: str = "", csv_subfolder: str = "") -> bool:
        """
        Convierte un archivo JSON a CSV.
        
        Args:
            json_filename: Nombre del archivo JSON
            csv_filename: Nombre del archivo CSV de salida
            json_subfolder: Subcarpeta del JSON
            csv_subfolder: Subcarpeta del CSV
            
        Returns:
            bool: True si se convirtió exitosamente
        """
        try:
            # Cargar datos JSON
            data = self.json_handler.load_json(json_filename, json_subfolder)
            if not data:
                return False
            
            # Convertir a lista si es necesario
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                self.logger.error("Los datos JSON deben ser una lista o diccionario")
                return False
            
            # Guardar como CSV
            return self.csv_handler.save_csv(data, csv_filename, csv_subfolder)
            
        except Exception as e:
            self.logger.error(f"Error convirtiendo JSON a CSV: {str(e)}")
            return False
    
    def csv_to_json(self, csv_filename: str, json_filename: str,
                   csv_subfolder: str = "", json_subfolder: str = "") -> bool:
        """
        Convierte un archivo CSV a JSON.
        
        Args:
            csv_filename: Nombre del archivo CSV
            json_filename: Nombre del archivo JSON de salida
            csv_subfolder: Subcarpeta del CSV
            json_subfolder: Subcarpeta del JSON
            
        Returns:
            bool: True si se convirtió exitosamente
        """
        try:
            # Cargar datos CSV
            data = self.csv_handler.load_csv(csv_filename, csv_subfolder)
            if not data:
                return False
            
            # Guardar como JSON
            return self.json_handler.save_json(data, json_filename, json_subfolder)
            
        except Exception as e:
            self.logger.error(f"Error convirtiendo CSV a JSON: {str(e)}")
            return False
    
    def aggregate_data(self, data: List[Dict], group_by: str, 
                      aggregations: Dict[str, str]) -> List[Dict]:
        """
        Agrega datos por un campo específico.
        
        Args:
            data: Lista de diccionarios
            group_by: Campo por el cual agrupar
            aggregations: Diccionario de {campo: operación}
            
        Returns:
            Lista de datos agregados
        """
        try:
            df = pd.DataFrame(data)
            
            # Realizar agregaciones
            agg_dict = {}
            for field, operation in aggregations.items():
                if field in df.columns:
                    if operation == 'mean':
                        agg_dict[field] = 'mean'
                    elif operation == 'sum':
                        agg_dict[field] = 'sum'
                    elif operation == 'count':
                        agg_dict[field] = 'count'
                    elif operation == 'min':
                        agg_dict[field] = 'min'
                    elif operation == 'max':
                        agg_dict[field] = 'max'
            
            if not agg_dict:
                return []
            
            # Agrupar y agregar
            grouped = df.groupby(group_by).agg(agg_dict).reset_index()
            
            # Convertir a lista de diccionarios
            return grouped.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"Error agregando datos: {str(e)}")
            return []
    
    def filter_data(self, data: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """
        Filtra datos basado en criterios específicos.
        
        Args:
            data: Lista de diccionarios
            filters: Diccionario de filtros {campo: valor}
            
        Returns:
            Lista de datos filtrados
        """
        try:
            filtered_data = []
            
            for item in data:
                include_item = True
                
                for field, value in filters.items():
                    if field not in item:
                        include_item = False
                        break
                    
                    # Diferentes tipos de filtros
                    if isinstance(value, dict):
                        # Filtros complejos como {'>=': 18, '<=': 25}
                        for operator, filter_value in value.items():
                            if operator == '>=' and item[field] < filter_value:
                                include_item = False
                                break
                            elif operator == '<=' and item[field] > filter_value:
                                include_item = False
                                break
                            elif operator == '>' and item[field] <= filter_value:
                                include_item = False
                                break
                            elif operator == '<' and item[field] >= filter_value:
                                include_item = False
                                break
                            elif operator == '!=' and item[field] == filter_value:
                                include_item = False
                                break
                    else:
                        # Filtro simple de igualdad
                        if item[field] != value:
                            include_item = False
                            break
                
                if include_item:
                    filtered_data.append(item)
            
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"Error filtrando datos: {str(e)}")
            return []
    
    def generate_summary_report(self, data: List[Dict], output_filename: str) -> bool:
        """
        Genera un reporte resumen de los datos.
        
        Args:
            data: Lista de diccionarios
            output_filename: Nombre del archivo de reporte
            
        Returns:
            bool: True si se generó exitosamente
        """
        try:
            if not data:
                return False
            
            df = pd.DataFrame(data)
            
            # Generar estadísticas
            summary = {
                "generated_at": datetime.now().isoformat(),
                "total_records": len(df),
                "columns": list(df.columns),
                "numeric_summary": {},
                "categorical_summary": {}
            }
            
            # Estadísticas numéricas
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                summary["numeric_summary"][col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "count": int(df[col].count())
                }
            
            # Estadísticas categóricas
            categorical_columns = df.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                value_counts = df[col].value_counts().to_dict()
                summary["categorical_summary"][col] = {
                    "unique_values": int(df[col].nunique()),
                    "most_common": value_counts,
                    "total_count": int(df[col].count())
                }
            
            # Guardar reporte
            return self.json_handler.save_json(summary, output_filename, "processed")
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {str(e)}")
            return False


def demonstrate_data_handling():
    """Demuestra las funcionalidades del manejador de datos."""
    print("🔄 Demostrando funcionalidades del manejador de datos...")
    
    # Inicializar procesador
    processor = DataProcessor()
    
    # Datos de ejemplo
    sample_data = [
        {
            "user_id": "user_001",
            "age": 19,
            "gender": "Femenino",
            "location": "Bogotá",
            "stress_level": 7,
            "mood_score": 3,
            "registration_date": "2024-01-15"
        },
        {
            "user_id": "user_002",
            "age": 22,
            "gender": "Masculino",
            "location": "Medellín",
            "stress_level": 5,
            "mood_score": 4,
            "registration_date": "2024-01-16"
        },
        {
            "user_id": "user_003",
            "age": 17,
            "gender": "No binario",
            "location": "Cali",
            "stress_level": 8,
            "mood_score": 2,
            "registration_date": "2024-01-17"
        }
    ]
    
    # Guardar como JSON
    print("📄 Guardando datos como JSON...")
    processor.json_handler.save_json(sample_data, "sample_users.json", "processed")
    
    # Guardar como CSV
    print("📊 Guardando datos como CSV...")
    processor.csv_handler.save_csv(sample_data, "sample_users.csv", "processed")
    
    # Cargar y filtrar datos
    print("🔍 Filtrando datos...")
    loaded_data = processor.json_handler.load_json("sample_users.json", "processed")
    if loaded_data:
        # Filtrar usuarios con alto estrés
        high_stress_users = processor.filter_data(
            loaded_data, 
            {"stress_level": {">=": 7}}
        )
        print(f"Usuarios con alto estrés: {len(high_stress_users)}")
        
        # Agregar datos por ubicación
        print("📈 Agregando datos por ubicación...")
        aggregated = processor.aggregate_data(
            loaded_data,
            "location",
            {"stress_level": "mean", "age": "mean", "user_id": "count"}
        )
        print(f"Datos agregados: {aggregated}")
    
    # Generar reporte resumen
    print("📋 Generando reporte resumen...")
    processor.generate_summary_report(sample_data, "data_summary_report.json")
    
    # Convertir entre formatos
    print("🔄 Convirtiendo entre formatos...")
    processor.json_to_csv("sample_users.json", "converted_users.csv", "processed", "processed")
    processor.csv_to_json("sample_users.csv", "converted_users.json", "processed", "processed")
    
    print("✅ Demostración completada!")


if __name__ == "__main__":
    print("🚀 Iniciando manejador de datos...")
    demonstrate_data_handling()
    print("✅ Manejador de datos listo!")