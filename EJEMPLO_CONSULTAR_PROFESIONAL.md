# 🔍 Consultar Profesional por ID de Usuario - Guía Completa

## 📋 Descripción

El endpoint `/api/profesionales/por-id/` permite buscar un profesional específico utilizando el ID del usuario enviado en el cuerpo de la petición JSON, en lugar de especificarlo en la URL. Este diseño es especialmente útil para bots de WhatsApp y otros sistemas automatizados que requieren URLs fijas.

## 🎯 Ventajas

✅ **URL Fija**: No necesitas construir URLs dinámicas
✅ **Bot-Friendly**: Ideal para integraciones con WhatsApp y chatbots
✅ **Datos Completos**: Retorna información en formato flat (sin subobjetos)
✅ **Validación Automática**: Verifica que el usuario sea de tipo PROFESIONAL y tenga registro de profesional
✅ **Consistente**: Usa el ID del usuario como otros endpoints del sistema

## 🔧 Configuración

### URL del Endpoint
```
POST /api/profesionales/por-id/
```

### Headers Requeridos
```
Content-Type: application/json
X-API-Key: tu-api-key-aqui
```

## 📝 Formato de Petición

### Estructura del JSON
```json
{
    "profesional_id": 456
}
```

### Campos Requeridos
- **profesional_id** (integer): ID del usuario (tipo PROFESIONAL) a buscar

## 📤 Ejemplos de Petición

### JavaScript/Fetch
```javascript
const response = await fetch('/api/profesionales/por-id/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'tu-api-key-aqui'
    },
    body: JSON.stringify({
        profesional_id: 456
    })
});

const profesional = await response.json();
console.log(profesional);
```

### cURL
```bash
curl -X POST "https://tu-api.com/api/profesionales/por-id/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key-aqui" \
  -d '{"profesional_id": 456}'
```

### Python (requests)
```python
import requests

url = "https://tu-api.com/api/profesionales/por-id/"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "tu-api-key-aqui"
}
data = {"profesional_id": 456}

response = requests.post(url, headers=headers, json=data)
profesional = response.json()
print(profesional)
```

## 📥 Formato de Respuesta

### Respuesta Exitosa (200 OK)
```json
{
    "profesional_id": 456,
    "nombres": "Dr. Juan Carlos",
    "apellidos": "Pérez García",
    "tipo_documento": "CC",
    "numero_documento": "12345678",
    "email": "dr.juan@email.com",
    "celular": "3009876543",
    "tipo": "Profesional",
    "numero_whatsapp": "573001234567",
    "cargo": "Psicólogo Clínico"
}
```

### Campos de Respuesta

#### Datos del Usuario
- **profesional_id**: ID del usuario (mismo que se envió en la petición)
- **nombres**: Nombres del profesional
- **apellidos**: Apellidos del profesional
- **tipo_documento**: Tipo de documento (CC, TI, NIT)
- **numero_documento**: Número de documento
- **email**: Correo electrónico
- **celular**: Número de celular
- **tipo**: Siempre será "Profesional"

#### Datos del Profesional
- **numero_whatsapp**: Número de WhatsApp del profesional
- **cargo**: Cargo o especialidad del profesional

## ⚠️ Manejo de Errores

### Error 400 - Datos Inválidos
```json
{
    "error": "profesional_id es requerido en el JSON"
}
```

### Error 400 - Usuario No Válido
```json
{
    "error": "Solo se pueden consultar usuarios de tipo PROFESIONAL. Tipo actual: CLIENTE"
}
```

### Error 404 - Usuario No Encontrado
```json
{
    "error": "Usuario no encontrado"
}
```

### Error 404 - Profesional No Encontrado
```json
{
    "error": "No se encontró registro de profesional para este usuario"
}
```

### Error 500 - Error Interno
```json
{
    "error": "Error interno del servidor",
    "detalles": "Descripción técnica del error"
}
```

## 🤖 Integración con Bots

### Para Bots de WhatsApp

```javascript
// Función helper para consultar profesional
async function consultarProfesional(profesionalId) {
    try {
        const response = await fetch('/api/profesionales/por-id/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': process.env.API_KEY
            },
            body: JSON.stringify({
                profesional_id: profesionalId
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error consultando profesional');
        }

        return await response.json();
    } catch (error) {
        console.error('Error:', error.message);
        throw error;
    }
}

// Uso en el bot
const profesional = await consultarProfesional(456);
const mensaje = `📋 **Profesional Encontrado**
👨‍⚕️ **Nombre**: ${profesional.nombres} ${profesional.apellidos}
🏥 **Cargo**: ${profesional.cargo}
📱 **WhatsApp**: ${profesional.numero_whatsapp}
📧 **Email**: ${profesional.email}`;

await enviarMensaje(numeroWhatsApp, mensaje);
```

### Para Integraciones con N8N

```json
{
    "nodes": [
        {
            "name": "Consultar Profesional",
            "type": "n8n-nodes-base.httpRequest",
            "parameters": {
                "method": "POST",
                "url": "https://tu-api.com/api/profesionales/por-id/",
                "headers": {
                    "X-API-Key": "tu-api-key-aqui"
                },
                "body": {
                    "usuario_id": "{{ $webhook.body.usuario_id }}"
                }
            }
        }
    ]
}
```

## 🔄 Comparación con Método Tradicional

### Método Tradicional (GET con ID en URL)
```javascript
// ❌ Requiere URL dinámica
const response = await fetch(`/api/profesionales/${profesionalId}/`);
```

### Nuevo Método (POST con ID de usuario en JSON)
```javascript
// ✅ URL fija, ID en el cuerpo
const response = await fetch('/api/profesionales/por-id/', {
    method: 'POST',
    body: JSON.stringify({ usuario_id: usuarioId })
});
```

## 📊 Logs del Sistema

El sistema registra automáticamente todas las consultas:

```
INFO - === INICIO - Buscando profesional por ID de usuario (desde JSON) ===
INFO - Datos recibidos: {'usuario_id': 456}
INFO - Usuario ID extraído del JSON: 456
INFO - Usuario encontrado - ID: 456, Tipo: Profesional
INFO - Profesional encontrado - ID: 123
INFO - === FIN - Profesional encontrado y retornado en formato flat ===
```

## 🎯 Casos de Uso

1. **Bots de WhatsApp**: Consultar información de profesionales para mostrar al cliente
2. **Aplicaciones Móviles**: Obtener datos completos del profesional para mostrar en la UI
3. **Sistemas de Terceros**: Integrar información de profesionales en otros sistemas
4. **APIs de Consulta**: Proporcionar datos de profesionales a sistemas externos

## ✅ Validaciones Automáticas

- ✅ Verifica que el `usuario_id` sea proporcionado
- ✅ Valida que el usuario exista en la base de datos
- ✅ Confirma que el usuario sea de tipo "PROFESIONAL"
- ✅ Verifica que exista un registro de profesional asociado al usuario
- ✅ Retorna toda la información en formato flat (sin subobjetos)

¡El endpoint está listo para ser usado en cualquier integración! 🚀
