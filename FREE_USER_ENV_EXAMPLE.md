# 🔧 Configuración de Variables de Entorno para Free User System

## 📋 Variables Requeridas

Añadir estas variables a tu archivo `.env`:

```bash
# ============================================
# CONFIGURACIÓN BÁSICA DEL BOT
# ============================================
BOT_TOKEN=tu_token_de_telegram_aqui

# ============================================
# CONFIGURACIÓN DE ADMINISTRADORES
# ============================================
# IDs de usuarios administradores (separados por comas)
ADMIN_USER_IDS=123456789,987654321,111222333

# Tiempo de espera para validaciones administrativas (en minutos)
WAIT_TIME_MINUTES=15

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================
DATABASE_URL=postgresql+asyncpg://username:password@localhost/dbname
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_ECHO=true
CREATE_TABLES=true
USE_SQLITE=true

# ============================================
# CONFIGURACIÓN DE CARACTERÍSTICAS
# ============================================
# Habilitar analytics
ENABLE_ANALYTICS=false

# Habilitar tareas en segundo plano
ENABLE_BACKGROUND_TASKS=true

# Habilitar sistema emocional
ENABLE_EMOTIONAL_SYSTEM=true

# ============================================
# CONFIGURACIÓN DE LOGGING
# ============================================
LOG_LEVEL=INFO
```

## 🎯 Variables Específicas para Free User System

### **ADMIN_USER_IDS** (Requerida)
- **Formato**: Lista de IDs separados por comas
- **Ejemplo**: `123456789,987654321,111222333`
- **Uso**: Define qué usuarios tienen permisos de administrador
- **Cómo obtener tu ID**: 
  1. Envía un mensaje a @userinfobot en Telegram
  2. O usa el comando `/start` en tu bot y revisa los logs

### **WAIT_TIME_MINUTES** (Opcional)
- **Formato**: Número entero
- **Ejemplo**: `15`
- **Por defecto**: `15`
- **Uso**: Tiempo de espera para validaciones administrativas

## 📱 Cómo obtener IDs de Telegram

### Método 1: Bot @userinfobot
1. Busca `@userinfobot` en Telegram
2. Envía `/start`
3. El bot te dará tu ID de usuario

### Método 2: Logs del bot
1. Ejecuta tu bot
2. Envía `/start` desde tu cuenta de admin
3. Revisa los logs del bot para ver tu user_id

### Método 3: Bot @raw_data_bot
1. Busca `@raw_data_bot` en Telegram  
2. Envía cualquier mensaje
3. Te mostrará los datos raw incluyendo tu ID

## ⚙️ Configuración de Ejemplo Completa

```bash
# Ejemplo de configuración real
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz

# Administradores (IDs reales de ejemplo)
ADMIN_USER_IDS=12345678,87654321,55555555

# Base de datos local para desarrollo
DATABASE_URL=sqlite+aiosqlite:///./diana_bot.db
CREATE_TABLES=true
USE_SQLITE=true

# Configuración de desarrollo
LOG_LEVEL=DEBUG
ENABLE_ANALYTICS=false
ENABLE_BACKGROUND_TASKS=true
ENABLE_EMOTIONAL_SYSTEM=true
```

## 🔍 Verificación de Configuración

Para verificar que las variables están correctamente configuradas:

1. **Ejecutar el bot**
2. **Usar comando de admin**: Un usuario configurado en `ADMIN_USER_IDS` debe poder usar `/admin`
3. **Probar notificaciones**: Un usuario Free debe poder activar notificaciones con "Me Interesa"
4. **Revisar logs**: Los logs deben mostrar la carga correcta de la configuración

## 🚨 Problemas Comunes

### ❌ "No tienes permisos de administrador"
- **Causa**: Tu ID no está en `ADMIN_USER_IDS`
- **Solución**: Verificar que tu ID real esté en la variable

### ❌ "ADMIN_USER_IDS format should be comma-separated integers"
- **Causa**: Formato incorrecto en la variable
- **Solución**: Usar solo números separados por comas, sin espacios extra

### ❌ Bot no responde a comandos de admin
- **Causa**: Variables de entorno no cargadas
- **Solución**: Verificar que el archivo `.env` esté en la raíz del proyecto

## ✅ Validación Exitosa

Si todo está configurado correctamente, verás en los logs:

```
[INFO] Configuration loaded config_keys=['bot', 'db', 'admin', ...]
[INFO] Admin user IDs loaded: [123456789, 987654321, 111222333]
[STARTUP] ✅ Sistema de menús Free User integrado correctamente
[STARTUP] 🎭 Sistema completo Free User configurado exitosamente
```

## 🔒 Seguridad

- ✅ **Nunca commits** el archivo `.env` al repositorio
- ✅ **Usa `.env.example`** para documentar variables requeridas
- ✅ **Restringe permisos** del archivo `.env` (`chmod 600 .env`)
- ✅ **Rota tokens** periódicamente si se comprometen