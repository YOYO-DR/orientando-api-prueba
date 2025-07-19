# 📅 Formato de Fechas en la API de Citas

## ✅ **Nuevo Formato Implementado**

### **Entrada (Request)**
Las fechas deben enviarse en formato `dd/mm/aaaa hh:mm` (24 horas)

```json
{
  "cliente_id": 15,
  "profesional_asignado_id": 8,
  "producto_id": 3,
  "fecha_hora_inicio": "20/07/2025 14:30",
  "fecha_hora_fin": "20/07/2025 15:30",
  "observaciones": "Primera consulta"
}
```

### **Salida (Response)**
Las fechas se devuelven en el mismo formato `dd/mm/aaaa hh:mm`

```json
{
  "id": 123,
  "cliente": {
    "id": 15,
    "nombres": "Juan",
    "apellidos": "Pérez"
  },
  "producto": {
    "id": 3,
    "nombre": "Consulta Psicológica"
  },
  "profesional_asignado": {
    "id": 8,
    "nombres": "Dr. María",
    "apellidos": "González"
  },
  "fecha_hora_inicio": "20/07/2025 14:30",
  "fecha_hora_fin": "20/07/2025 15:30",
  "observaciones": "Primera consulta",
  "estado_actual": {
    "estado_cita": "AGENDADO"
  }
}
```

### **Listados de Citas**
También se aplica el formato en los listados:

```json
{
  "results": [
    {
      "id": 123,
      "fecha_hora_inicio": "20/07/2025 14:30",
      "fecha_hora_fin": "20/07/2025 15:30",
      "cliente_nombre": "Juan",
      "cliente_apellidos": "Pérez",
      "producto_nombre": "Consulta Psicológica",
      "profesional_nombre": "Dr. María",
      "estado_cita": "AGENDADO"
    }
  ]
}
```

## ❌ **Errores de Validación**

### **Formato Incorrecto**
```json
{
  "fecha_hora_inicio": ["El formato de fecha debe ser dd/mm/aaaa hh:mm (ejemplo: 20/07/2025 14:30)"]
}
```

### **Ejemplos de Formatos Incorrectos**
- ❌ `"2025-07-20 14:30"` (formato yyyy-mm-dd)
- ❌ `"2025-07-20T14:30:00Z"` (formato ISO)
- ❌ `"20-07-2025 14:30"` (guiones en lugar de barras)
- ❌ `"20/07/25 14:30"` (año de 2 dígitos)
- ❌ `"20/07/2025 2:30 PM"` (formato 12 horas)

### **Ejemplos de Formatos Correctos**
- ✅ `"20/07/2025 14:30"` (formato correcto)
- ✅ `"01/01/2025 09:00"` (con ceros)
- ✅ `"31/12/2025 23:59"` (formato 24 horas)

## 🔧 **Características Técnicas**

### **Validación Implementada**
- Formato estricto `dd/mm/aaaa hh:mm`
- Validación de fechas válidas (no acepta 31/02/2025)
- Formato 24 horas obligatorio
- Logging detallado para debugging

### **Compatibilidad**
- **Frontend**: Fácil de formatear desde JavaScript
- **WhatsApp Bot**: Formato natural para usuarios
- **Mobile Apps**: Compatible con pickers de fecha nativos

### **Ejemplo JavaScript**
```javascript
// Convertir Date a formato requerido
const fecha = new Date();
const formatoRequerido = fecha.toLocaleDateString('es-ES', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric'
}) + ' ' + fecha.toLocaleTimeString('es-ES', {
  hour: '2-digit',
  minute: '2-digit',
  hour12: false
});

console.log(formatoRequerido); // "20/07/2025 14:30"
```

### **Ejemplo Python**
```python
from datetime import datetime

# Crear fecha en formato requerido
fecha = datetime.now()
formato_requerido = fecha.strftime('%d/%m/%Y %H:%M')
print(formato_requerido)  # "20/07/2025 14:30"

# Validar formato recibido
try:
    fecha_convertida = datetime.strptime("20/07/2025 14:30", '%d/%m/%Y %H:%M')
    print("Fecha válida:", fecha_convertida)
except ValueError:
    print("Formato de fecha inválido")
```

¡El nuevo formato está completamente implementado y documentado! 🎉
