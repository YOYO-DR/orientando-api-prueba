# 🔄 Ejemplo: Actualizar Cita por ID en JSON

## 📝 Descripción

Nuevo endpoint que permite actualizar citas enviando el ID de la cita en el JSON en lugar de en la URL. Ideal para bots de WhatsApp que no pueden manejar URLs dinámicas.

## 🌐 Endpoint

```
PATCH /api/citas/actualizar-por-id/
PUT /api/citas/actualizar-por-id/
```

## 🔑 Autenticación

```
X-API-Key: tu-api-key-aqui
```

## 📋 Estructura del JSON

### Campos Obligatorios
- `cita_id` - ID de la cita a actualizar

### Campos Opcionales (actualización parcial)
- `cliente_id` - ID del cliente (debe ser tipo CLIENTE)
- `profesional_asignado_id` - ID del profesional (debe ser tipo PROFESIONAL)
- `producto_id` - ID del producto/servicio
- `fecha_hora_inicio` - Formato: "dd/mm/aaaa hh:mm"
- `fecha_hora_fin` - Formato: "dd/mm/aaaa hh:mm"
- `observaciones` - Comentarios adicionales
- `google_calendar_event_id` - ID del evento en Google Calendar
- `google_calendar_url_event` - URL completa del evento en Google Calendar

## ✅ Validaciones Automáticas

1. **Cliente válido**: Verifica que sea tipo CLIENTE con perfil
2. **Profesional válido**: Verifica que sea tipo PROFESIONAL con perfil
3. **Producto válido**: Verifica que el producto existe
4. **Relación producto-profesional**: Valida que el profesional puede atender el producto
5. **Fechas coherentes**: Fecha fin debe ser posterior a fecha inicio

## 🎯 Ejemplo de Uso

### Actualización Parcial (PATCH)
```json
{
  "cita_id": 123,
  "fecha_hora_inicio": "25/12/2024 15:00",
  "fecha_hora_fin": "25/12/2024 16:00",
  "observaciones": "Cita reprogramada por WhatsApp"
}
```

### Actualización Completa (PUT)
```json
{
  "cita_id": 123,
  "cliente_id": 456,
  "profesional_asignado_id": 789,
  "producto_id": 10,
  "fecha_hora_inicio": "25/12/2024 15:00",
  "fecha_hora_fin": "25/12/2024 16:00",
  "observaciones": "Cita confirmada y reprogramada",
  "google_calendar_event_id": "evento_123",
  "google_calendar_url_event": "https://calendar.google.com/calendar/event?eid=abcd1234567890"
}
```

### Respuesta Exitosa
```json
{
  "message": "Cita actualizada exitosamente",
  "cita": {
    "cita_id": 123,
    "cliente_id": 456,
    "cliente_nombre": "Juan Carlos",
    "cliente_apellidos": "Pérez García",
    "producto_nombre": "Consulta Psicológica",
    "profesional_id": 789,
    "profesional_nombre": "Dr. María López",
    "fecha_hora_inicio": "25/12/2024 15:00",
    "fecha_hora_fin": "25/12/2024 16:00",
    "estado_cita": "AGENDADO",
    "google_calendar_event_id": "evento_123",
    "observaciones": "Cita confirmada y reprogramada"
  }
}
```

## ❌ Ejemplos de Errores

### Error: Cita no encontrada
```json
{
  "error": "Cita no encontrada"
}
```

### Error: Cliente inválido
```json
{
  "error": "Datos de cita inválidos",
  "detalles": {
    "cliente_id": ["El usuario debe ser de tipo CLIENTE. Tipo actual: PROFESIONAL"]
  }
}
```

### Error: Relación producto-profesional inexistente
```json
{
  "error": "Datos de cita inválidos",
  "detalles": {
    "profesional_asignado_id": "El profesional Dr. Juan Pérez no está autorizado para atender el producto \"Consulta Nutricional\""
  }
}
```

### Error: Fechas inválidas
```json
{
  "error": "Datos de cita inválidos",
  "detalles": {
    "fecha_hora_fin": "La fecha de fin debe ser posterior a la fecha de inicio"
  }
}
```

## 🚀 Comparación con Método Tradicional

### ❌ Método Tradicional (problemático para bots)
```bash
PATCH /api/citas/123/
```
**Problema**: El bot necesita construir URLs dinámicas

### ✅ Nuevo Método (ideal para bots)
```bash
PATCH /api/citas/actualizar-por-id/
```
**Ventaja**: URL fija, ID va en el JSON

## 💡 Beneficios

1. **URL Fija**: No necesita construir URLs dinámicas
2. **Validaciones Robustas**: Mismas validaciones que crear cita
3. **Actualizaciones Parciales**: Solo envía campos que cambian
4. **Compatibilidad**: No afecta endpoints existentes
5. **Logs Detallados**: Registro completo para debugging

## 🔧 Implementación en Bot WhatsApp

```python
import requests

def actualizar_cita(cita_id, **campos_a_actualizar):
    """Actualizar cita enviando ID en JSON"""
    
    url = "https://tu-api.com/api/citas/actualizar-por-id/"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "tu-api-key"
    }
    
    # Estructura del payload
    payload = {
        "cita_id": cita_id,
        **campos_a_actualizar  # Solo campos que se van a actualizar
    }
    
    response = requests.patch(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.json()}")
        return None

# Ejemplo de uso
resultado = actualizar_cita(
    cita_id=123,
    fecha_hora_inicio="25/12/2024 16:00",
    fecha_hora_fin="25/12/2024 17:00",
    observaciones="Reprogramada por WhatsApp",
    google_calendar_url_event="https://calendar.google.com/calendar/event?eid=xyz123"
)
```

---
✨ **¡Endpoint listo para usar!** La API ahora soporta actualización de citas con ID en JSON, manteniendo todas las validaciones de seguridad.
