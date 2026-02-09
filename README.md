# API de Gestión de Tareas con FastAPI

## Inicio Rápido

### Instalación y Configuración

1. **Clonar el repositorio**
```bash
git clone https://github.com/BenjaminLarger/Talan_Prueba_APIRest-FastAPI.git
cd Talan_Prueba_APIRest-FastAPI
```

2. **Crear y activar entorno virtual**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
```

5. **Ejecutar la aplicación**
```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`

### Acceder a la Documentación de la API
- Swagger UI: http://localhost:8000/docs

## Arquitectura

### Stack Tecnológico
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Base de Datos**: SQLite
- **Autenticación**: JWT (JSON Web Tokens)
- **Hash de Contraseña**: bcrypt vía passlib
- **Validación**: Pydantic

## Flujo de Autenticación

La API utiliza JWT para autenticar a los usuarios. Este es el flujo de autenticación:

### 1. Registro de Usuario
- **Endpoint**: `POST /auth/register`
- **Parámetros**: `username`, `password`
- **Respuesta**: Mensaje de confirmación

### 2. Inicio de Sesión (Login)
- **Endpoint**: `POST /auth/token`
- **Parámetros**: `username`, `password`
- **Respuesta**: Token JWT con tipo `bearer`

### 3. Uso del Token
- Incluir el token en cada solicitud protegida usando el encabezado:
  ```
  Authorization: Bearer <tu_jwt_token>
  ```
- Los tokens expiran después de 30 minutos

### 4. Roles y Permisos
- Usuario: Solo puede ver y gestionar sus propias tareas
- Admin: Puede ver y gestionar todas las tareas, con opción de filtrar por usuario

### 5. Validación
- El servidor verifica y decodifica el JWT para cada solicitud protegida
- Si el token es inválido o ha expirado, se retorna error `401 Unauthorized`
