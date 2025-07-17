# 🌐 Configuración CORS para OrientandoSAS API

Esta configuración permite que tu API sea consumida desde diferentes frontends y herramientas como n8n sin problemas de CORS.

## ✅ ¿Qué se ha configurado?

### 1. **Django CORS Headers**
- ✅ Instalado `django-cors-headers==4.5.0`
- ✅ Agregado a INSTALLED_APPS
- ✅ Middleware configurado correctamente

### 2. **Configuración por Entorno**

#### **Desarrollo (DEBUG=True):**
```python
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

#### **Producción (DEBUG=False):**
```python
CORS_ALLOWED_ORIGINS = [
    "https://tu-dominio.com",
    "https://www.tu-dominio.com", 
    "https://app.n8n.cloud",
    "http://localhost:3000",  # React/Next.js
    "http://localhost:5173",  # Vite
]
```

### 3. **Headers Configurados**
- ✅ `Authorization` - Para autenticación
- ✅ `X-API-Key` - Para nuestro sistema de API Keys
- ✅ `Content-Type` - Para JSON
- ✅ `Accept` - Para respuestas
- ✅ Y más headers estándar

### 4. **Métodos HTTP Permitidos**
- ✅ GET, POST, PUT, PATCH, DELETE, OPTIONS

### 5. **Nginx CORS Backup**
- ✅ Headers CORS también en Nginx
- ✅ Manejo de preflight requests (OPTIONS)

## 🔧 Para usar desde diferentes plataformas:

### **Frontend JavaScript/React/Vue:**
```javascript
// Ejemplo con fetch
const response = await fetch('https://tu-api.com/api/citas/', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'tu-api-key-aqui'
    },
    credentials: 'include'  // Si necesitas cookies
});
```

### **n8n Workflow:**
```json
{
  "method": "GET",
  "url": "https://tu-api.com/api/citas/",
  "headers": {
    "Content-Type": "application/json",
    "X-API-Key": "tu-api-key-aqui"
  }
}
```

### **cURL para pruebas:**
```bash
curl -X GET "https://tu-api.com/api/citas/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key-aqui"
```

### **Axios (JavaScript):**
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://tu-api.com/api/',
  headers: {
    'X-API-Key': 'tu-api-key-aqui'
  },
  withCredentials: true
});

// Usar la API
const citas = await api.get('citas/');
```

## 🔒 Configuración de Seguridad

### **Para Producción:**
1. **Especificar dominios exactos** en `CORS_ALLOWED_ORIGINS`
2. **Cambiar** `CORS_ALLOW_ALL_ORIGINS = False`
3. **Configurar** tu dominio real

### **Variables de entorno para CORS:**
```env
# En .env.production
CORS_ALLOWED_ORIGINS=https://tu-frontend.com,https://app.n8n.cloud
CORS_ALLOW_CREDENTIALS=true
```

## 🚨 Solución de Problemas Comunes

### **Error: "CORS policy: No 'Access-Control-Allow-Origin'"**
**Solución:** 
- Verifica que tu dominio esté en `CORS_ALLOWED_ORIGINS`
- En desarrollo, usa `CORS_ALLOW_ALL_ORIGINS = True`

### **Error: "CORS policy: Request header field x-api-key is not allowed"**
**Solución:** 
- `X-API-Key` ya está en `CORS_ALLOW_HEADERS`
- Reinicia el servidor Django

### **Error con método OPTIONS**
**Solución:** 
- Nginx maneja automáticamente preflight requests
- Django también los procesa

### **Error desde n8n**
**Solución:**
- Usa `https://app.n8n.cloud` en CORS_ALLOWED_ORIGINS
- O `CORS_ALLOW_ALL_ORIGINS = True` para desarrollo

## 🧪 Probar CORS

### **Test simple con navegador:**
```javascript
// En la consola del navegador
fetch('https://tu-api.com/api/citas/', {
    headers: {'X-API-Key': 'tu-key'}
})
.then(r => r.json())
.then(console.log)
```

### **Test con herramientas:**
- ✅ Postman (no tiene restricciones CORS)
- ✅ Insomnia (no tiene restricciones CORS)
- ✅ curl (no tiene restricciones CORS)
- ⚠️ Navegador (SÍ tiene restricciones CORS)
- ⚠️ n8n (SÍ tiene restricciones CORS)

## 📝 Notas Importantes

1. **CORS solo afecta navegadores y herramientas web**
2. **APIs server-to-server no tienen restricciones CORS**
3. **En desarrollo, `CORS_ALLOW_ALL_ORIGINS = True` es conveniente**
4. **En producción, especifica dominios exactos por seguridad**
5. **X-API-Key funciona perfectamente con CORS configurado**

¡Tu API ya está lista para ser consumida desde cualquier frontend o herramienta! 🎉
