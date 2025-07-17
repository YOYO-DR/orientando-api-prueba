# 📋 Ejemplos de Uso de la API OrientandoSAS

## 🔑 Autenticación con API Key

Todos los ejemplos usan autenticación por API Key. Asegúrate de:
1. Crear una API Key en el admin Django o via API
2. Incluir el header `X-API-Key` en todas las peticiones

## 🌐 Frontend JavaScript

### **Vanilla JavaScript**
```javascript
// Configuración base
const API_BASE_URL = 'https://tu-api.com/api';
const API_KEY = 'tu-api-key-aqui';

// Función helper para peticiones
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY,
            ...options.headers
        },
        ...options
    };
    
    const response = await fetch(url, config);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

// Ejemplos de uso
// Obtener todas las citas
const citas = await apiRequest('/citas/');

// Crear una nueva cita
const nuevaCita = await apiRequest('/citas/', {
    method: 'POST',
    body: JSON.stringify({
        cliente_id: 1,
        producto_id: 1,
        fecha_hora_inicio: '2025-07-20T10:00:00Z',
        fecha_hora_fin: '2025-07-20T11:00:00Z'
    })
});

// Obtener cita específica
const cita = await apiRequest('/citas/1/');

// Actualizar cita
const citaActualizada = await apiRequest('/citas/1/', {
    method: 'PATCH',
    body: JSON.stringify({
        observaciones: 'Cita confirmada por el cliente'
    })
});
```

### **React con Axios**
```jsx
import axios from 'axios';
import { useState, useEffect } from 'react';

// Configuración de Axios
const api = axios.create({
    baseURL: 'https://tu-api.com/api',
    headers: {
        'X-API-Key': 'tu-api-key-aqui'
    }
});

// Componente React
function CitasList() {
    const [citas, setCitas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCitas = async () => {
            try {
                const response = await api.get('/citas/');
                setCitas(response.data.results || response.data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchCitas();
    }, []);

    const crearCita = async (dataCita) => {
        try {
            const response = await api.post('/citas/', dataCita);
            setCitas([...citas, response.data]);
            return response.data;
        } catch (err) {
            console.error('Error creando cita:', err);
            throw err;
        }
    };

    if (loading) return <div>Cargando citas...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <h2>Lista de Citas</h2>
            {citas.map(cita => (
                <div key={cita.id}>
                    <h3>Cita #{cita.id}</h3>
                    <p>Cliente: {cita.cliente_nombre} {cita.cliente_apellidos}</p>
                    <p>Producto: {cita.producto_nombre}</p>
                    <p>Fecha: {new Date(cita.fecha_hora_inicio).toLocaleString()}</p>
                </div>
            ))}
        </div>
    );
}
```

## 🔄 n8n Workflows

### **Obtener Citas (HTTP Request Node)**
```json
{
  "method": "GET",
  "url": "https://tu-api.com/api/citas/",
  "headers": {
    "Content-Type": "application/json",
    "X-API-Key": "tu-api-key-aqui"
  },
  "options": {}
}
```

### **Crear Cliente y Cita (Workflow Completo)**
```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "nueva-cita"
      }
    },
    {
      "name": "Crear Usuario",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://tu-api.com/api/usuarios/",
        "headers": {
          "X-API-Key": "tu-api-key-aqui"
        },
        "body": {
          "nombres": "{{ $webhook.body.nombres }}",
          "apellidos": "{{ $webhook.body.apellidos }}",
          "tipo_documento": "CC",
          "numero_documento": "{{ $webhook.body.documento }}",
          "email": "{{ $webhook.body.email }}",
          "celular": "{{ $webhook.body.celular }}",
          "tipo": "CLIENTE"
        }
      }
    },
    {
      "name": "Crear Cliente",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://tu-api.com/api/clientes/",
        "headers": {
          "X-API-Key": "tu-api-key-aqui"
        },
        "body": {
          "usuario_id": "{{ $('Crear Usuario').first().json.id }}",
          "edad": "{{ $webhook.body.edad }}",
          "barrio": "{{ $webhook.body.barrio }}",
          "direccion": "{{ $webhook.body.direccion }}"
        }
      }
    },
    {
      "name": "Crear Cita",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://tu-api.com/api/citas/",
        "headers": {
          "X-API-Key": "tu-api-key-aqui"
        },
        "body": {
          "cliente_id": "{{ $('Crear Usuario').first().json.id }}",
          "producto_id": "{{ $webhook.body.producto_id }}",
          "fecha_hora_inicio": "{{ $webhook.body.fecha_hora_inicio }}",
          "fecha_hora_fin": "{{ $webhook.body.fecha_hora_fin }}",
          "observaciones": "Cita creada desde n8n"
        }
      }
    }
  ]
}
```

### **Enviar Recordatorio de Cita (Scheduled Trigger)**
```json
{
  "name": "Recordatorio Citas",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "value": 1}]
        }
      }
    },
    {
      "name": "Obtener Citas del Día",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "https://tu-api.com/api/citas/",
        "headers": {
          "X-API-Key": "tu-api-key-aqui"
        },
        "qs": {
          "fecha_hora_inicio__date": "{{ new Date().toISOString().split('T')[0] }}"
        }
      }
    },
    {
      "name": "Enviar WhatsApp",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://api.whatsapp.com/send",
        "body": {
          "phone": "{{ $json.cliente.celular }}",
          "message": "Recordatorio: Tienes una cita hoy a las {{ $json.fecha_hora_inicio }}"
        }
      }
    }
  ]
}
```

## 📱 React Native

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

class OrientandoAPI {
    constructor() {
        this.baseURL = 'https://tu-api.com/api';
        this.apiKey = 'tu-api-key-aqui';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey,
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Error en la petición');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Métodos específicos
    async obtenerCitas() {
        return this.request('/citas/');
    }

    async crearCita(data) {
        return this.request('/citas/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async obtenerProfesionales() {
        return this.request('/profesionales/');
    }
}

// Uso en componente
export default function CitasScreen() {
    const [citas, setCitas] = useState([]);
    const api = new OrientandoAPI();

    useEffect(() => {
        const cargarCitas = async () => {
            try {
                const data = await api.obtenerCitas();
                setCitas(data.results || data);
            } catch (error) {
                Alert.alert('Error', 'No se pudieron cargar las citas');
            }
        };

        cargarCitas();
    }, []);

    return (
        <View>
            {/* Renderizar citas */}
        </View>
    );
}
```

## 🐍 Python (para scripts o bots)

```python
import requests
import json
from datetime import datetime

class OrientandoAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        })

    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_citas(self, **filters):
        params = {k: v for k, v in filters.items() if v is not None}
        return self.request('GET', '/citas/', params=params)

    def create_cita(self, data):
        return self.request('POST', '/citas/', json=data)

    def get_productos(self):
        return self.request('GET', '/productos/')

# Uso
api = OrientandoAPI('https://tu-api.com/api', 'tu-api-key-aqui')

# Obtener citas de hoy
today = datetime.now().strftime('%Y-%m-%d')
citas_hoy = api.get_citas(fecha_hora_inicio__date=today)

# Crear nueva cita
nueva_cita = api.create_cita({
    'cliente_id': 1,
    'producto_id': 1,
    'fecha_hora_inicio': '2025-07-20T10:00:00Z',
    'fecha_hora_fin': '2025-07-20T11:00:00Z',
    'observaciones': 'Cita creada desde Python'
})

print(f"Cita creada con ID: {nueva_cita['id']}")
```

## 🔧 cURL (para testing)

```bash
# Obtener todas las citas
curl -X GET "https://tu-api.com/api/citas/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key-aqui"

# Crear una nueva cita
curl -X POST "https://tu-api.com/api/citas/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key-aqui" \
  -d '{
    "cliente_id": 1,
    "producto_id": 1,
    "fecha_hora_inicio": "2025-07-20T10:00:00Z",
    "fecha_hora_fin": "2025-07-20T11:00:00Z",
    "observaciones": "Cita creada desde cURL"
  }'

# Obtener cita específica
curl -X GET "https://tu-api.com/api/citas/1/" \
  -H "X-API-Key: tu-api-key-aqui"

# Actualizar cita
curl -X PATCH "https://tu-api.com/api/citas/1/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key-aqui" \
  -d '{"observaciones": "Cita confirmada"}'

# Obtener estadísticas de citas
curl -X GET "https://tu-api.com/api/citas/estadisticas/" \
  -H "X-API-Key: tu-api-key-aqui"
```

## 📊 Endpoints Disponibles

- `GET /api/citas/` - Listar citas
- `POST /api/citas/` - Crear cita
- `GET /api/citas/{id}/` - Obtener cita específica
- `PUT/PATCH /api/citas/{id}/` - Actualizar cita
- `DELETE /api/citas/{id}/` - Eliminar cita
- `GET /api/usuarios/` - Listar usuarios
- `GET /api/clientes/` - Listar clientes
- `GET /api/profesionales/` - Listar profesionales
- `GET /api/productos/` - Listar productos
- `GET /api/api-keys/` - Gestionar API Keys (requiere autenticación admin)

¡Tu API está lista para ser consumida desde cualquier plataforma! 🚀
