# 🔍 INSTRUCCIONES PARA CLAUDE CODE - REVISIÓN INTERACTIVA DIANA BOT V2

## 🎯 **OBJETIVO PRINCIPAL**
Realizar una revisión sistemática e interactiva de cada módulo del bot Diana V2, probando funcionalidades, verificando conexiones y completando lo que falte para tener una **BASE SÓLIDA 100% FUNCIONAL**.

## 📋 **METODOLOGÍA DE REVISIÓN**

### **PARA CADA MÓDULO SIGUE ESTE PROCESO:**

1. **📂 INSPECCIONAR CÓDIGO** - Revisar archivos del módulo
2. **🔍 ANALIZAR FUNCIONALIDAD** - Entender qué hace y cómo
3. **🧪 PROBAR FUNCIONAMIENTO** - Ejecutar tests o crear pruebas rápidas  
4. **🔗 VERIFICAR CONEXIONES** - Comprobar integración con otros módulos
5. **✅ DETERMINAR ESTADO** - Completo ✅ | Parcial ⚠️ | Faltante ❌
6. **🛠️ COMPLETAR SI ES NECESARIO** - Desarrollar lo que falte
7. **📊 REPORTAR RESULTADO** - Estado final del módulo

## 🗂️ **MÓDULOS A REVISAR (EN ESTE ORDEN)**

### **1. ADMINISTRACIÓN DE CANALES** 🔐
**Archivos a revisar:**
- `src/modules/channel/service.py` 
- `src/modules/channel/events.py`
- `src/bot/database/models/channel.py`
- `src/bot/handlers/user/token_redemption.py`

**Funcionalidades a probar:**
- ✅ Crear canal VIP/Free
- ✅ Procesar solicitudes de ingreso  
- ✅ Validar accesos por nivel/VIP
- ✅ Gestionar membresías y expiración
- ✅ Canje de tokens VIP

**Criterios de completitud:**
- Servicio inicializa correctamente ✅
- Métodos principales ejecutan sin error ✅
- Eventos se publican/manejan correctamente ✅
- Base de datos se actualiza ✅
- Handlers UI responden ✅

### **2. GAMIFICACIÓN** 🎮
**Archivos a revisar:**
- `src/modules/gamification/service.py`
- `src/modules/shop/service.py`
- `src/modules/trivia/service.py` 
- `src/modules/daily_rewards/service.py`
- `src/bot/handlers/gamification/`
- `src/bot/handlers/user/shop.py`

**Funcionalidades a probar:**
- ✅ Sistema de besitos (ganar/gastar)
- ✅ Niveles (progresión automática)
- ✅ Tienda (comprar ítems)
- ✅ Trivias diarias
- ✅ Regalos diarios
- ✅ Misiones y logros

**Comandos a verificar:**
- `/tienda`, `/trivia`, `/regalo`, `/misiones`, `/profile`

### **3. NARRATIVA** 📖  
**Archivos a revisar:**
- `src/modules/narrative/service.py`
- `src/modules/narrative/diana_integration.py`
- `src/bot/handlers/narrative/`

**Funcionalidades a probar:**
- ✅ Fragmentos narrativos
- ✅ Sistema de pistas (LorePieces)
- ✅ Mochila narrativa
- ✅ Desbloqueo por nivel
- ⚠️ Historia lineal básica (COMPLETAR)

**Comando a verificar:**
- `/mochila`

### **4. INTEGRACIÓN DIANA** 🛡️
**Archivos a revisar:**
- `src/modules/narrative/diana_integration.py`
- Conexión con servicio Diana externo

**Funcionalidades a probar:**
- ✅ Validación de usuarios
- ✅ Recompensas por validación
- ✅ Integración con gamificación

### **5. HANDLERS Y UI** 📱
**Archivos a revisar:**
- `src/bot/handlers/user/` 
- `src/bot/handlers/admin/`
- `src/infrastructure/telegram/handlers.py`
- `main.py`

**Funcionalidades a probar:**
- ✅ Comando `/start` 
- ✅ Comando `/admin`
- ✅ Todos los callbacks del panel admin
- ✅ Menús y navegación
- ✅ Auto-limpieza de mensajes

### **6. PANEL ADMINISTRATIVO** ⚙️
**Archivos a revisar:**
- `src/bot/handlers/admin/menu_system.py`
- `src/bot/services/admin.py` 

**Funcionalidades a probar:**
- ✅ 7 secciones principales
- ✅ 27+ subsecciones
- ✅ Navegación sin spam
- ✅ Callbacks funcionando
- ✅ Integración con servicios

## 🧪 **FORMATO DE PRUEBAS**

### **Para cada funcionalidad usa este template:**

```python
# TEST: [Nombre de la funcionalidad]
print("🧪 PROBANDO: [Funcionalidad]")

try:
    # Código de prueba aquí
    result = await service.metodo_a_probar()
    print("✅ ÉXITO:", result)
    return True
except Exception as e:
    print("❌ ERROR:", str(e))
    return False
```

### **Para verificar conexiones entre módulos:**

```python
# CONEXIÓN: [Módulo A] → [Módulo B]  
print("🔗 VERIFICANDO CONEXIÓN: [A] → [B]")

# Verificar que A puede llamar a B
# Verificar que eventos se propagan
# Verificar que datos se comparten correctamente
```

## 📊 **FORMATO DE REPORTE**

**Para cada módulo reporta:**

```
## 📋 MÓDULO: [Nombre]
**Estado**: ✅ Completo | ⚠️ Parcial | ❌ Faltante

### Funcionalidades Probadas:
- ✅ [Funcionalidad 1] - Funcionando correctamente
- ⚠️ [Funcionalidad 2] - Funciona pero necesita mejoras  
- ❌ [Funcionalidad 3] - No implementada o con errores

### Conexiones Verificadas:
- ✅ [Conexión A] - Correcta
- ❌ [Conexión B] - Falla o faltante

### Acciones Tomadas:
- [Lista de correcciones/desarrollos realizados]

### Siguiente Paso:
- [Qué hacer después con este módulo]
```

## 🎯 **CRITERIOS DE "BASE COMPLETA"**

### **Un módulo está COMPLETO cuando:**
1. **Código ejecuta sin errores críticos** ✅
2. **Funcionalidades principales operativas** ✅
3. **Conexiones con otros módulos funcionando** ✅
4. **Handlers UI responden correctamente** ✅
5. **Base de datos se actualiza** ✅

### **La BASE está TERMINADA cuando:**
1. **Todos los módulos son ✅ Completos**
2. **Flujo end-to-end funciona**: Usuario nuevo → Reacciona → Sube nivel → Ve narrativa → Solicita VIP
3. **11+ comandos funcionando sin errores**
4. **Panel admin operativo**

## 🚀 **FLUJO FINAL DE INTEGRACIÓN**

**Al terminar todos los módulos, probar flujo completo:**

1. **Usuario Nuevo**: `/start` → Registro exitoso
2. **Gamificación**: Reaccionar → Besitos → Nivel up  
3. **Narrativa**: Nuevo nivel → Fragmento desbloqueado
4. **Mochila**: `/mochila` → Ver progreso
5. **VIP**: Solicitar acceso → Proceso completo
6. **Admin**: `/admin` → Panel funcional

## 🤝 **COLABORACIÓN INTERACTIVA CON EL USUARIO**

### **INSTRUCCIÓN CRÍTICA: SIEMPRE INVOLUCRA AL USUARIO EN LAS PRUEBAS**

**Para CADA funcionalidad que vayas a revisar:**

1. **🔍 PRIMERO**: Analiza el código y entiende la funcionalidad
2. **📋 SEGUNDO**: Explica al usuario qué vas a probar
3. **🎯 TERCERO**: Da instrucciones específicas de prueba
4. **⏳ CUARTO**: Espera los resultados del usuario
5. **📊 QUINTO**: Analiza los resultados juntos

### **FORMATO DE INSTRUCCIONES DE PRUEBA:**

```
🧪 **PROBANDO**: [Nombre de la funcionalidad]

👤 **INSTRUCCIONES PARA EL USUARIO**:
1. Ejecuta el bot: `python main.py`
2. En Telegram, envía: `/admin`
3. Presiona el botón: 📊 **[Nombre específico del botón]**
4. Navega a: [Ruta específica del menú]
5. Realiza la acción: [Acción específica]
6. Observa si: [Qué debería pasar]

⏳ **Espero tu reporte**: ¿Funcionó correctamente? ¿Qué mensajes viste? ¿Hubo errores?
```

### **EJEMPLOS DE INSTRUCCIONES INTERACTIVAS:**

#### **Para Panel Administrativo:**
```
🧪 **PROBANDO**: Navegación del Panel Admin

👤 **INSTRUCCIONES**:
1. Ejecuta: `python main.py`
2. En Telegram: `/admin` 
3. ¿Ves el menú principal con 7 opciones?
4. Presiona: 👥 **Gestión de Usuarios**
5. ¿Se abre el submenú de usuarios?
6. Presiona: 📊 **Estadísticas**
7. ¿Te muestra datos de usuarios?

⏳ **Dime**: ¿Qué viste en cada paso? ¿Algún error o comportamiento extraño?
```

#### **Para Comandos de Usuario:**
```
🧪 **PROBANDO**: Sistema de Tienda

👤 **INSTRUCCIONES**:
1. En Telegram (como usuario normal): `/tienda`
2. ¿Ves la tienda con categorías y productos?
3. Presiona cualquier botón de producto
4. ¿Te muestra detalles y precio en besitos?
5. Si tienes besitos, intenta comprar algo

⏳ **Reporta**: ¿Funcionó la compra? ¿Se descontaron los besitos?
```

#### **Para Flujos Complejos:**
```
🧪 **PROBANDO**: Flujo VIP Completo

👤 **INSTRUCCIONES PASO A PASO**:
1. `/start` como usuario nuevo
2. Reacciona a mensajes hasta subir de nivel
3. `/admin` → 👑 **Gestión VIP** → ➕ **Crear Token**
4. Copia el token generado
5. Como usuario: `/start [token_copiado]`
6. ¿Te dio acceso VIP automáticamente?

⏳ **Necesito saber**: ¿Cada paso funcionó? ¿En cuál se rompió el flujo?
```

## ⚡ **INSTRUCCIONES ESPECÍFICAS**

1. **🤝 COLABORA SIEMPRE**: Nunca asumas que algo funciona sin que el usuario lo pruebe
2. **📋 SÉ ESPECÍFICO**: Di exactamente qué botón presionar, qué texto debería aparecer
3. **⏳ ESPERA FEEDBACK**: No continúes hasta obtener respuesta del usuario
4. **🔍 ANALIZA JUNTOS**: Si algo falla, diagnostica con el usuario en tiempo real
5. **🛠️ CORRIGE INMEDIATAMENTE**: Si hay problemas, arregla antes de continuar
6. **📊 DOCUMENTA TODO**: Registra qué funcionó y qué no según las pruebas reales

## 🎯 **RESULTADO ESPERADO**

Al final de esta revisión tendremos:
- ✅ **Base sólida 100% funcional**
- ✅ **Documentación clara de lo que funciona**  
- ✅ **Lista de expansiones futuras**
- ✅ **Bot listo para producción como base**

**¡Empecemos con el Módulo 1: Administración de Canales!**
