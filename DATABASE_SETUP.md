# 🗄️ Configuración de Base de Datos MySQL

## 📋 Instrucciones de Instalación

### 1. **Instalar MySQL**
Si no tienes MySQL instalado:
- **Windows**: Descarga desde [mysql.com](https://dev.mysql.com/downloads/mysql/)
- **macOS**: `brew install mysql`
- **Linux**: `sudo apt-get install mysql-server` (Ubuntu/Debian)

### 2. **Instalar Dependencias Python**
```bash
pip install -r requirements.txt
```

### 3. **Configurar Variables de Entorno**
1. Copia `config.env` y renómbralo a `.env`
2. Edita las credenciales según tu configuración:
```env
DB_HOST=localhost
DB_NAME=bienestaremocional
DB_USER=root
DB_PASSWORD=tu_contraseña_aqui
DB_PORT=3306
```

### 4. **Inicializar Base de Datos**
```bash
python init_database.py
```

### 5. **Verificar Conexión**
```bash
python test_mysql_connection.py
```

## 🔧 Solución de Problemas

### Error: "Access denied for user 'root'@'localhost'"
- Verifica que la contraseña en `config.env` sea correcta
- Si no tienes contraseña, deja `DB_PASSWORD=` vacío

### Error: "Can't connect to MySQL server"
- Verifica que MySQL esté ejecutándose: `mysql --version`
- En Windows: Verifica que el servicio MySQL esté iniciado
- En Linux: `sudo systemctl start mysql`

### Error: "Unknown database"
- Ejecuta `python init_database.py` para crear la base de datos

### Error: "Table doesn't exist"
- Ejecuta `python init_database.py` para crear las tablas

## 📊 Estructura de la Base de Datos

### Tablas Principales:
- **usuarios**: Información de usuarios registrados
- **surveys**: Encuestas disponibles
- **questions**: Preguntas de cada encuesta
- **survey_responses**: Respuestas completas de usuarios
- **question_answers**: Respuestas individuales a preguntas

## 🚀 Comandos Útiles

```bash
# Verificar estado de la base de datos
python test_mysql_connection.py

# Reinicializar base de datos (CUIDADO: borra datos)
python init_database.py

# Verificar usuarios registrados
python test_db_connection.py

# Inicializar encuestas por defecto
python initialize_surveys.py
```

## 🔒 Seguridad

- **NUNCA** subas el archivo `.env` a Git
- Usa contraseñas seguras en producción
- Considera usar usuarios específicos para la aplicación (no root)

## 📝 Notas Importantes

- El script `init_database.py` es seguro de ejecutar múltiples veces
- Las tablas se crean con `IF NOT EXISTS` para evitar errores
- La configuración se carga automáticamente desde variables de entorno
