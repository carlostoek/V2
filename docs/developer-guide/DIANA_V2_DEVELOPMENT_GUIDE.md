# 🛠️ DIANA V2 - GUÍA DE DESARROLLO

## 🎯 Arquitectura de Desarrollo

### 📁 Estructura de Archivos Principales

```
src/bot/core/
├── diana_master_system.py      # 🎪 Sistema de usuarios (/start)
├── diana_admin_elite.py        # 🏛️ Sistema de administración (/admin)
└── diana_admin_services_integration.py  # 🔗 Integración con servicios

src/infrastructure/telegram/
└── adapter.py                  # 🚀 Registro de sistemas
```

### 🔧 Cómo Agregar Nuevas Funcionalidades

#### Para Sistema de Usuarios (diana_master_system.py):

1. **Nueva sección de menú:**
```python
# Agregar a USER_MENU_STRUCTURE
"nueva_seccion": UserMenuSection(
    key="nueva_seccion",
    icon="🆕",
    title="Nueva Sección",
    diana_description="Lo que Diana dice sobre esta sección...",
    lucien_insight="La perspectiva de Lucien...",
    subsections={"sub1": "Subsección 1"},
    tier_required=UserTier.FREE
)
```

2. **Nuevo callback:**
```python
# Agregar en handle_diana_callbacks()
elif action.startswith("nueva_accion:"):
    await handle_nueva_accion(callback, diana_master)
```

3. **Nueva función handler:**
```python
async def handle_nueva_accion(callback: CallbackQuery, master: DianaMasterInterface):
    """Descripción de la nueva acción"""
    # Tu lógica aquí
    pass
```

#### Para Sistema de Administración (diana_admin_elite.py):

1. **Nueva sección admin:**
```python
# Agregar a ADMIN_MENU_STRUCTURE  
"nueva_admin": AdminMenuSection(
    key="nueva_admin",
    title="Nueva Admin",
    icon="🔧",
    subsections={"config": "Configuración"},
    description="Descripción de la nueva sección"
)
```

2. **Nueva acción admin:**
```python
# Agregar a AdminAction enum en diana_admin_callbacks.py
NUEVA_ACCION = "nueva_accion"

# Registrar en CallbackRouter
router.register_action_handler(AdminAction.NUEVA_ACCION, handle_nueva_admin)
```

---

## 🎭 Personalidades Diana/Lucien

### 📝 Pautas de Escritura

#### Diana (Seductora/Misteriosa):
```python
diana_text = "Aquí es donde dejo caer todas las máscaras... donde puedes conocer mi alma desnuda..."
```

**Características:**
- Usa primera persona ("mi", "yo", "me")
- Vulnerable pero calculada
- Crea deseo de intimidad
- Palabras clave: "secretos", "máscaras", "alma", "especial"

#### Lucien (Mayordomo Elegante):
```python
lucien_text = "Diana observa cada cambio en ti con fascinación. Sus ojos nunca mienten sobre lo que ve."
```

**Características:**  
- Habla de Diana en tercera persona
- Perspectiva racional y observadora
- Valida las decisiones del usuario
- Palabras clave: "Diana", "observa", "confirma", "perspicaz"

### 💡 Template de Sección:
```python
section = UserMenuSection(
    # ... otros campos
    diana_description="Lo que Diana dice directamente al usuario...",
    lucien_insight="La perspectiva de Lucien sobre Diana y la situación...",
)
```

---

## 💰 Sistema de Conversión VIP

### 🎯 Flujo Completo

1. **Usuario FREE explora** → Ve contenido con "hooks" de conversión
2. **Diana seduce** → "¿Estás listo para conocer mi verdadero yo?"
3. **Usuario muestra interés** → Presiona "Me Interesa el Diván VIP"
4. **Sistema notifica admin** → Alert automático con datos del usuario
5. **Admin convierte** → Contacto personal y cierre de venta

### 🔔 Implementar Notificación Admin

```python
async def nueva_accion_interes(callback: CallbackQuery, master: DianaMasterInterface):
    # 1. Mostrar confirmación al usuario
    text = """<b>💎 Interés Registrado</b>
    
<b>🎭 Diana:</b> <i>"Mensaje personalizado..."</i>
<b>🎩 Lucien:</b> <i>"Confirmación elegante..."</i>"""
    
    # 2. Notificar al admin
    await send_admin_interest_notification(master, user_id, "nuevo_interes")
```

### 📊 Datos de Usuario en Notificación

La notificación incluye automáticamente:
- ID del usuario
- Nivel y puntos actuales
- Status VIP (FREE/VIP)
- Nivel de intimidad calculado
- Racha de días consecutivos
- Tipo de interés específico

---

## 🔧 Testing y Debugging

### 🧪 Comandos de Prueba

```bash
# Probar sistema de usuarios
/start

# Probar sistema admin  
/admin

# Callbacks de usuario
diana:refresh
diana:section:vip_info
diana:package:intimate_conversations
diana:interest:vip_channel

# Callbacks admin
admin:section:vip
admin:vip_generate_token
admin:system_health
```

### 🔍 Debugging

1. **Logs estructurados:**
```python
master.logger.info("Nueva acción ejecutada", 
                  user_id=user_id, 
                  action="nueva_accion",
                  resultado="exitoso")
```

2. **Verificar servicios:**
```python
if not master.services.get('admin'):
    master.logger.warning("Admin service no disponible")
    return
```

3. **Error handling:**
```python
try:
    result = await master.services['admin'].some_method()
except Exception as e:
    master.logger.error("Error en nueva acción", error=str(e))
    await callback.answer("Error temporal, intenta de nuevo")
    return
```

---

## 🚀 Deployment

### 📦 Registro de Sistemas

En `src/infrastructure/telegram/adapter.py`:

```python
def setup_diana_systems(self):
    # Registrar sistema de usuarios
    self.diana_master_system = register_diana_master_system(self.dp, self._services)
    
    # Registrar sistema admin
    self.diana_admin_elite = register_diana_admin_elite(self.dp, self._services)
```

### ✅ Checklist Pre-Deploy

- [ ] Verificar imports no rotos
- [ ] Probar ambos comandos (`/start`, `/admin`)
- [ ] Verificar callbacks principales
- [ ] Testear notificaciones admin
- [ ] Confirmar servicios conectados
- [ ] Revisar logs de errores

### 🔄 Sintaxis Check

```bash
python -m py_compile src/bot/core/diana_master_system.py
python -m py_compile src/bot/core/diana_admin_elite.py
python -m py_compile src/infrastructure/telegram/adapter.py
```

---

## 📚 Referencias Técnicas

### 🎪 Diana Master System

**Callbacks disponibles:**
- `diana:refresh` - Actualizar interfaz principal
- `diana:section:{key}` - Navegar a sección específica  
- `diana:package:{key}` - Ver detalle de paquete
- `diana:interest:{type}` - Registrar interés (notifica admin)

**Estructuras de datos:**
- `USER_MENU_STRUCTURE` - Definición de menús de usuario
- `CONTENT_PACKAGES` - Paquetes de contenido premium
- `UserTier` - FREE, VIP, PREMIUM
- `UserMood` - Estados emocionales del usuario

### 🏛️ Diana Admin Elite

**Callbacks disponibles:**
- `admin:main` - Panel principal
- `admin:section:{key}` - Sección administrativa
- `admin:subsection:{section}:{sub}` - Subsección específica
- `admin:{action}` - Acciones directas (vip_config, system_health, etc.)

**Componentes principales:**
- `ADMIN_MENU_STRUCTURE` - Estructura de menú administrativo
- `EliteUIBuilder` - Constructor de interfaces avanzadas
- `CallbackRouter` - Router tipo-safe para callbacks
- `AnalyticsEngine` - Sistema de métricas

---

## 🆘 Solución de Problemas Comunes

### ❌ "Sistema no disponible"
**Causa:** Sistema no inicializado  
**Solución:** Verificar que `register_diana_*_system()` se ejecute correctamente

### ❌ "Sección no encontrada"  
**Causa:** Callback para sección inexistente
**Solución:** Verificar que la sección exista en `USER_MENU_STRUCTURE` o `ADMIN_MENU_STRUCTURE`

### ❌ "Handler no encontrado"
**Causa:** Callback no registrado en el router
**Solución:** Agregar el handler en `handle_diana_callbacks()` o registrar en `CallbackRouter`

### ❌ Notificaciones admin no llegan
**Causa:** Servicio admin no configurado
**Solución:** Verificar que `admin_service` tenga método `send_admin_notification()`

---

*Guía mantenida por el equipo Diana V2*  
*Última actualización: Agosto 2025*