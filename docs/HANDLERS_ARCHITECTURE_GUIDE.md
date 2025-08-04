# 🔧 Guía de Arquitectura de Handlers - Diana Bot V2

## 📋 Resumen Ejecutivo

Esta guía documenta la arquitectura de handlers del bot, el problema encontrado con comandos duplicados, y cómo se solucionó. **Lectura obligatoria para cualquier desarrollador que agregue nuevos comandos o handlers.**

---

## 🏗️ Arquitectura Actual del Sistema

### **Punto de Entrada Principal**
```
main.py → TelegramAdapter → sistema de handlers
```

**Archivo principal:** `main.py`
- Inicializa servicios (EventBus, GamificationService, NarrativeService, AdminService)
- Crea `TelegramAdapter` con todas las dependencias
- El adapter se encarga de registrar handlers y iniciar el bot

### **Sistemas de Handlers (CRÍTICO: Solo uno debe estar activo)**

#### ✅ **Sistema Moderno (ACTIVO)**
- **Ubicación:** `src/bot/handlers/`
- **Configuración:** `src/bot/core/handlers.py`
- **Inyección de Dependencias:** `src/bot/core/di.py`
- **Usado por:** `TelegramAdapter` → `setup_modern_handlers()`

#### ❌ **Sistema Legacy (DESACTIVADO)**
- **Ubicación:** `src/infrastructure/telegram/handlers.py`
- **Función:** `setup_handlers()` (comentada)
- **Estado:** Reemplazado por sistema moderno

---

## 🚨 Problema Encontrado: Comandos Duplicados

### **Síntomas del Problema**
- Comando `/admin` no respondía o mostraba menú incorrecto
- Sin errores en logs
- Handler aparentemente no se ejecutaba

### **Causa Raíz Identificada**
1. **Dos sistemas de handlers coexistiendo:**
   - Sistema legacy en `infrastructure/telegram/handlers.py`
   - Sistema moderno en `src/bot/handlers/admin/main.py`

2. **main.py usaba sistema legacy** que tenía el comando admin comentado

3. **Comando admin duplicado:**
   - **Legacy:** `src/infrastructure/telegram/handlers.py:128`
   - **Moderno:** `src/bot/handlers/admin/main.py:10`

### **Solución Implementada**
1. **Conectar sistema moderno** en `TelegramAdapter`
2. **Desactivar sistema legacy** (comentar imports)
3. **Configurar contenedor DI** para servicios
4. **Hardcodear ID admin temporalmente** para debugging

---

## 🎯 Cómo Agregar Nuevos Handlers

### **1. Ubicación Correcta**
```
src/bot/handlers/
├── admin/          # Handlers de administración
├── user/           # Handlers de usuarios
├── gamification/   # Handlers de gamificación
├── narrative/      # Handlers narrativos
└── [nuevo_modulo]/ # Tu nuevo módulo aquí
```

### **2. Estructura de un Handler**
```python
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

# Crear router específico
mi_router = Router()

@mi_router.message(Command("mi_comando"))
async def mi_handler(message: Message):
    """Handler para mi comando."""
    await message.answer("Mi respuesta")

@mi_router.callback_query(F.data == "mi_callback")
async def mi_callback_handler(callback: CallbackQuery):
    """Handler para callbacks."""
    await callback.message.edit_text("Callback procesado")
    await callback.answer()
```

### **3. Registrar en el Sistema**
**Archivo:** `src/bot/handlers/[modulo]/__init__.py`
```python
from .mi_handler import mi_router

def register_mi_handlers(dp, servicios...):
    """Registra handlers del módulo."""
    dp.include_router(mi_router)
```

**Archivo:** `src/bot/core/handlers.py`
```python
from ..handlers.mi_modulo import register_mi_handlers

def setup_handlers(dp: Dispatcher) -> None:
    # ... otros handlers ...
    register_mi_handlers(dp, event_bus, servicios...)
```

---

## 🔍 Debugging de Handlers

### **Logs de Debug Útiles**
```python
# En tu handler
@router.message(Command("test"))
async def test_handler(message: Message):
    print(f"🎯 HANDLER: Comando recibido de user_id: {message.from_user.id}")
    # Tu lógica aquí
```

### **Verificar Registro de Handlers**
```python
# En TelegramAdapter._register_handlers()
print("🔧 TelegramAdapter: Registrando sistema moderno de handlers...")
```

### **Comandos para Verificar Estado**
```bash
# Ver logs en Railway
railway logs

# Verificar handlers registrados
# (agregar endpoint de debug si es necesario)
```

---

## 📁 Mapa de Archivos Críticos

### **Inicio y Configuración**
- `main.py` - Punto de entrada principal
- `src/infrastructure/telegram/adapter.py` - Adaptador de Telegram
- `src/bot/core/handlers.py` - Configuración de handlers modernos

### **Handlers por Módulo**
- `src/bot/handlers/admin/main.py` - Comando `/admin` principal
- `src/bot/handlers/user/start.py` - Comando `/start`
- `src/bot/handlers/[modulo]/` - Otros comandos

### **Filtros y Middleware**
- `src/bot/filters/is_admin.py` - Filtro de administrador
- `src/bot/middlewares/` - Middlewares diversos

### **Inyección de Dependencias**
- `src/bot/core/di.py` - Contenedor simple DI
- `src/bot/core/containers.py` - Sistema DI avanzado (dependency-injector)

---

## ⚠️ Problemas Comunes y Soluciones

### **1. Handler No Responde**
**Posibles causas:**
- Filtro bloqueando (ej: `IsAdminFilter`)
- Handler no registrado en `setup_handlers()`
- Sistema legacy interfiriendo

**Debugging:**
```python
# Agregar handler sin filtros para testing
@router.message(Command("test"))
async def debug_handler(message: Message):
    print(f"🔍 DEBUG: Comando recibido: {message.text}")
```

### **2. Error "coroutine object is not iterable"**
**Causa:** Función async llamada sin `await`
```python
# ❌ ERROR
tariffs = service.get_all_tariffs()

# ✅ CORRECTO  
tariffs = await service.get_all_tariffs()
```

### **3. AttributeError en Objetos SQLAlchemy**
**Causa:** Acceso incorrecto a propiedades
```python
# ❌ ERROR
name = tariff['name']

# ✅ CORRECTO
name = tariff.name
```

### **4. Comandos Duplicados**
**Prevención:**
1. Verificar que el comando no existe: `grep -r "Command(\"mi_comando\")" src/`
2. Solo usar sistema moderno en `src/bot/handlers/`
3. Nunca modificar `src/infrastructure/telegram/handlers.py`

---

## 🛠️ Configuración de Admin IDs

### **Variables de Entorno (Producción)**
```bash
# En Railway/Docker
ADMIN_USER_IDS=1280444712,otro_id,otro_id
```

### **Hardcoding Temporal (Solo Development)**
```python
# src/bot/filters/is_admin.py
if user_id == 1280444712:  # TU ID AQUÍ
    return True
```

---

## 📝 Checklist para Nuevos Handlers

- [ ] ✅ Handler creado en `src/bot/handlers/[modulo]/`
- [ ] ✅ Router incluido en `__init__.py` del módulo
- [ ] ✅ Registrado en `src/bot/core/handlers.py`
- [ ] ✅ Comandos añadidos a `src/bot/config/constants.py` (opcional)
- [ ] ✅ Filtros apropiados aplicados (admin, user, etc.)
- [ ] ✅ Logs de debug agregados durante desarrollo
- [ ] ✅ Probado en development y production
- [ ] ✅ Documentación actualizada

---

## 🎭 Historia de Este Documento

**Fecha:** 04 Agosto 2025  
**Problema:** Comando `/admin` duplicado causando conflictos  
**Desarrollador:** @1280444712  
**Solución:** Migración completa a sistema moderno de handlers  

**Cambios Realizados:**
1. Identificación de comandos duplicados en dos sistemas
2. Migración de `infrastructure/` a `src/bot/handlers/`
3. Configuración de DI container en `TelegramAdapter`
4. Documentación completa para futuros desarrolladores

---

## 🚀 Próximos Pasos Recomendados

1. **Eliminar sistema legacy** completamente (una vez verificado que todo funciona)
2. **Migrar variable ADMIN_USER_IDS** de hardcoding a configuración
3. **Agregar comando `admin` a `COMMANDS`** en `constants.py`
4. **Crear tests** para handlers críticos
5. **Implementar endpoint de debug** para verificar handlers registrados

---

*📚 Documento creado durante resolución de conflicto de handlers. Mantener actualizado al agregar nuevos comandos.*