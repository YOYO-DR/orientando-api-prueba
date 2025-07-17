# Guía de Autenticación por API Key - OrientandoSAS API

## 🔐 **Configuración de Autenticación por API Key**

La API de OrientandoSAS ahora soporta autenticación por API Key, ideal para chatbots y servicios externos que necesitan acceso programático sin lidiar con tokens JWT que expiran.

## 📋 **Características:**

### ✅ **Ventajas de API Keys:**
- **Sin expiración**: No necesitas renovar tokens
- **Sencillo**: Solo un header en cada request
- **Estadísticas**: Rastrea el uso de cada key
- **Control granular**: Activa/desactiva keys individualmente
- **Seguro**: Claves generadas criptográficamente

## 🚀 **Pasos para Implementar:**

### **1. Crear una API Key**

#### **Opción A: A través de la API REST**
```bash
# Primero autentícate como usuario regular
POST http://localhost:8000/api/v1/api-keys/
Content-Type: application/json
Authorization: Basic <tu-auth-basica>

{
    "name": "Chatbot WhatsApp",
    "description": "API Key para el chatbot de WhatsApp",
    "is_active": true
}
```

#### **Opción B: A través de Django Admin**
1. Ve a http://localhost:8000/admin/
2. Navega a "API Keys"
3. Haz clic en "Agregar API Key"
4. Llena los campos:
   - **Nombre**: `Chatbot WhatsApp`
   - **Descripción**: `API Key para el chatbot de WhatsApp`
   - **Activa**: ✅
5. Guarda y copia la API Key generada

### **2. Usar la API Key en Requests**

```bash
# Usar la API Key en cualquier endpoint
GET http://localhost:8000/api/v1/usuarios/
Authorization: Api-Key tu_api_key_aqui
```

### **3. Ejemplo de Uso en Código**

#### **Python (requests)**
```python
import requests

API_KEY = "tu_api_key_aqui"
BASE_URL = "http://localhost:8000/api/v1"

headers = {
    "Authorization": f"Api-Key {API_KEY}",
    "Content-Type": "application/json"
}

# Obtener todos los usuarios
response = requests.get(f"{BASE_URL}/usuarios/", headers=headers)
usuarios = response.json()

# Crear una nueva cita
nueva_cita = {
    "cliente_id": 1,
    "producto_id": 1,
    "fecha_hora_inicio": "2025-07-20T10:00:00Z",
    "fecha_hora_fin": "2025-07-20T11:00:00Z"
}

response = requests.post(f"{BASE_URL}/citas/", 
                        json=nueva_cita, 
                        headers=headers)
```

#### **JavaScript (fetch)**
```javascript
const API_KEY = 'tu_api_key_aqui';
const BASE_URL = 'http://localhost:8000/api/v1';

const headers = {
    'Authorization': `Api-Key ${API_KEY}`,
    'Content-Type': 'application/json'
};

// Obtener productos agendables por bot
fetch(`${BASE_URL}/productos/agendables_bot/`, {
    headers: headers
})
.then(response => response.json())
.then(productos => console.log(productos));

// Buscar estado de chat por número
fetch(`${BASE_URL}/estados-chat/por_numero/?numero=573001234567`, {
    headers: headers
})
.then(response => response.json())
.then(estado => console.log(estado));
```

#### **cURL**
```bash
# Obtener citas de hoy
curl -H "Authorization: Api-Key tu_api_key_aqui" \
     http://localhost:8000/api/v1/citas/hoy/

# Crear un estado de chat
curl -X POST \
     -H "Authorization: Api-Key tu_api_key_aqui" \
     -H "Content-Type: application/json" \
     -d '{"numero_whatsapp": "573001234567", "estado_conversacion": {"estado": "inicial"}}' \
     http://localhost:8000/api/v1/estados-chat/
```

## 🛠️ **Gestión de API Keys**

### **Endpoints Disponibles:**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/api-keys/` | Listar todas las API Keys |
| `POST` | `/api/v1/api-keys/` | Crear nueva API Key |
| `GET` | `/api/v1/api-keys/{id}/` | Obtener una API Key específica |
| `PUT/PATCH` | `/api/v1/api-keys/{id}/` | Actualizar una API Key |
| `DELETE` | `/api/v1/api-keys/{id}/` | Eliminar una API Key |
| `POST` | `/api/v1/api-keys/{id}/regenerate/` | Regenerar la key |
| `POST` | `/api/v1/api-keys/{id}/toggle_active/` | Activar/desactivar |
| `GET` | `/api/v1/api-keys/stats/` | Estadísticas de uso |

### **Regenerar una API Key:**
```bash
POST http://localhost:8000/api/v1/api-keys/1/regenerate/
Authorization: Basic <tu-auth-basica>
```

### **Ver Estadísticas:**
```bash
GET http://localhost:8000/api/v1/api-keys/stats/
Authorization: Basic <tu-auth-basica>
```

## 🔒 **Seguridad**

### **Buenas Prácticas:**
1. **Nunca hardcodees** la API Key en tu código
2. **Usa variables de entorno** para almacenar keys
3. **Rota las keys** periódicamente
4. **Monitorea el uso** a través de estadísticas
5. **Desactiva keys** que no uses

### **Variables de Entorno (Recomendado):**
```bash
# .env del chatbot
ORIENTANDO_API_KEY=tu_api_key_aqui
ORIENTANDO_API_BASE_URL=http://localhost:8000/api/v1
```

## 📊 **Endpoints Especiales para Chatbots**

### **Endpoints Útiles para Chatbots:**

```bash
# Buscar estado de chat por número WhatsApp
GET /api/v1/estados-chat/por_numero/?numero=573001234567

# Obtener productos agendables por bot
GET /api/v1/productos/agendables_bot/

# Obtener citas de hoy
GET /api/v1/citas/hoy/

# Obtener citas por rango de fechas
GET /api/v1/citas/por_fecha/?fecha_inicio=2025-07-20&fecha_fin=2025-07-21

# Cambiar estado de una cita
POST /api/v1/citas/1/cambiar_estado/
{
    "estado_cita": "Confirmado"
}

# Obtener solo clientes
GET /api/v1/usuarios/clientes/

# Obtener solo profesionales
GET /api/v1/usuarios/profesionales/
```

## 🔍 **Ejemplo Completo para Chatbot**

```python
import os
import requests
from datetime import datetime

class OrientandoAPI:
    def __init__(self):
        self.api_key = os.getenv('ORIENTANDO_API_KEY')
        self.base_url = os.getenv('ORIENTANDO_API_BASE_URL', 'http://localhost:8000/api/v1')
        self.headers = {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def buscar_cliente_por_numero(self, numero_whatsapp):
        """Buscar cliente por número de WhatsApp"""
        response = requests.get(
            f"{self.base_url}/usuarios/",
            params={'search': numero_whatsapp},
            headers=self.headers
        )
        return response.json()
    
    def obtener_productos_agendables(self):
        """Obtener productos que se pueden agendar por bot"""
        response = requests.get(
            f"{self.base_url}/productos/agendables_bot/",
            headers=self.headers
        )
        return response.json()
    
    def crear_cita(self, cliente_id, producto_id, fecha_inicio, fecha_fin):
        """Crear una nueva cita"""
        data = {
            'cliente_id': cliente_id,
            'producto_id': producto_id,
            'fecha_hora_inicio': fecha_inicio,
            'fecha_hora_fin': fecha_fin
        }
        response = requests.post(
            f"{self.base_url}/citas/",
            json=data,
            headers=self.headers
        )
        return response.json()
    
    def actualizar_estado_chat(self, numero_whatsapp, nuevo_estado):
        """Actualizar estado de conversación"""
        # Buscar si existe el estado
        response = requests.get(
            f"{self.base_url}/estados-chat/por_numero/",
            params={'numero': numero_whatsapp},
            headers=self.headers
        )
        
        if response.status_code == 200:
            # Actualizar existente
            estado_chat = response.json()
            response = requests.patch(
                f"{self.base_url}/estados-chat/{estado_chat['id']}/",
                json={'estado_conversacion': nuevo_estado},
                headers=self.headers
            )
        else:
            # Crear nuevo
            response = requests.post(
                f"{self.base_url}/estados-chat/",
                json={
                    'numero_whatsapp': numero_whatsapp,
                    'estado_conversacion': nuevo_estado
                },
                headers=self.headers
            )
        return response.json()

# Uso del cliente
api = OrientandoAPI()

# Buscar cliente
clientes = api.buscar_cliente_por_numero("573001234567")

# Obtener productos disponibles
productos = api.obtener_productos_agendables()

# Crear cita
nueva_cita = api.crear_cita(
    cliente_id=1,
    producto_id=1,
    fecha_inicio="2025-07-20T10:00:00Z",
    fecha_fin="2025-07-20T11:00:00Z"
)
```

## 🎯 **Testing**

Para probar la autenticación, puedes usar la documentación interactiva:

1. Ve a http://localhost:8000/api/docs/
2. Haz clic en "Authorize"
3. En el campo "apiKey", ingresa: `Api-Key tu_api_key_aqui`
4. Prueba cualquier endpoint

¡La autenticación por API Key está lista para usar con tu chatbot! 🤖
