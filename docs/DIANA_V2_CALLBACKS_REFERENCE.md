# 🔄 DIANA V2 - REFERENCIA DE CALLBACKS

## 🎪 Sistema de Usuarios (diana:)

### 🏠 Navegación Principal

| Callback | Descripción | Parámetros |
|----------|-------------|------------|
| `diana:refresh` | Actualiza interfaz principal | - |
| `diana:smart_help` | Sistema de ayuda inteligente | - |

### 📂 Navegación de Secciones

| Callback | Descripción | Resultado |
|----------|-------------|-----------|
| `diana:section:profile` | Mi Reflejo - Perfil personal | Estadísticas, logros, configuración |
| `diana:section:vip_info` | El Diván VIP - Info exclusiva | Beneficios VIP, vista previa, testimonios |
| `diana:section:content_packages` | Tesoros Especiales - Paquetes premium | Lista de paquetes disponibles |

### 📦 Detalles de Paquetes

| Callback | Descripción | Precio | Contenido |
|----------|-------------|--------|-----------|
| `diana:package:intimate_conversations` | Conversaciones Íntimas | $29.99 | Audio personalizado, chat 24/7, confesiones |
| `diana:package:exclusive_photos` | Fotografías Exclusivas | $19.99 | 30+ fotos artísticas, behind-scenes |
| `diana:package:custom_videos` | Videos Personalizados | $49.99 | Video 5-10min personalizado con tu nombre |
| `diana:package:vip_experiences` | Experiencias VIP | $99.99/mes | Acceso completo + chat privado + lives |

### 💖 Registro de Interés (Genera Notificaciones Admin)

| Callback | Descripción | Acción Admin |
|----------|-------------|--------------|
| `diana:interest:vip_channel` | Interés en Diván VIP | 🔔 Notifica admin con datos del usuario |
| `diana:interest:package:intimate_conversations` | Interés en Conversaciones Íntimas | 🔔 Alert de conversión alta |
| `diana:interest:package:exclusive_photos` | Interés en Fotografías | 🔔 Oportunidad de venta |
| `diana:interest:package:custom_videos` | Interés en Videos Personalizados | 🔔 Lead premium |
| `diana:interest:package:vip_experiences` | Interés en Experiencias VIP | 🔔 Conversión VIP completa |

### 🎮 Funcionalidades de Gamificación

| Callback | Descripción | Funcionalidad |
|----------|-------------|---------------|
| `diana:missions_hub` | Centro de Misiones | Misiones disponibles, progreso |
| `diana:daily_gift` | Regalo Diario | Recompensa diaria, racha |
| `diana:trivia_challenge` | Desafío Trivia | Pregunta con recompensa |
| `diana:epic_shop` | Tienda Épica | Tarifas VIP, canjear tokens |

### 📖 Narrativa Interactiva  

| Callback | Descripción | Experiencia |
|----------|-------------|-------------|
| `diana:narrative_hub` | Historia Viva de Diana | Progreso narrativo, decisiones |
| `diana:surprise_me` | Sorpréndeme | Función aleatoria sorpresa |

---

## 🏛️ Sistema de Administración (admin:)

### 🧭 Navegación Jerárquica

| Callback | Descripción | Resultado |
|----------|-------------|-----------|
| `admin:main` | Panel Principal | Dashboard con métricas |
| `admin:back` | Navegar Atrás | Vuelve al nivel anterior |
| `admin:refresh` | Actualizar Panel | Refresca datos actuales |

### 📂 Secciones Administrativas

| Callback | Descripción | Subsecciones |
|----------|-------------|--------------|
| `admin:section:vip` | Gestión VIP | Config, tokens, stats, subscribers, posts |
| `admin:section:gamification` | Gamificación | Stats, users, missions, badges, levels |
| `admin:section:free_channel` | Canal Gratuito | Config, stats, requests, test |
| `admin:section:global_config` | Config Global | Schedulers, signatures, channels |
| `admin:section:auctions` | Subastas | Stats, pending, active, create |
| `admin:section:events` | Eventos/Sorteos | Events list, raffles list |
| `admin:section:trivia` | Trivias | List, create |

### 💎 Acciones VIP

| Callback | Descripción | Función |
|----------|-------------|---------|
| `admin:vip_config` | Configuración VIP | Ajustar mensajes, recordatorios, suscripciones |
| `admin:vip_generate_token` | Generar Token VIP | Crear token de invitación |
| `admin:vip_stats` | Estadísticas VIP | Métricas de suscriptores |
| `admin:vip_subscribers` | Gestión Suscriptores | CRUD de usuarios VIP |
| `admin:vip_post` | Enviar Post VIP | Publicar en canal VIP |

### 🎮 Acciones de Gamificación

| Callback | Descripción | Función |
|----------|-------------|---------|
| `admin:gamif_stats` | Stats Gamificación | Métricas de engagement |
| `admin:gamif_users` | Usuarios Activos | Lista de usuarios gamificados |
| `admin:gamif_missions` | Gestión Misiones | Crear, editar misiones |
| `admin:gamif_badges` | Insignias | Gestionar badges |
| `admin:gamif_levels` | Sistema Niveles | Configurar niveles |
| `admin:gamif_rewards` | Recompensas | Gestionar premios |

### 🔧 Sistema y Utilidades

| Callback | Descripción | Resultado |
|----------|-------------|-----------|
| `admin:system_health` | Salud del Sistema | Estado de servicios |
| `admin:system_logs` | Logs del Sistema | Ver logs recientes |
| `admin:system_config` | Configuración Sistema | Ajustes globales |
| `admin:export` | Exportar Datos | Generar reportes |
| `admin:search` | Búsqueda Avanzada | Buscar en sistema |
| `admin:help` | Ayuda Admin | Guía de uso |

### 🎨 Personalización UI

| Callback | Descripción | Temas |
|----------|-------------|--------|
| `admin:theme:executive` | Tema Ejecutivo | Estilo corporativo |
| `admin:theme:vibrant` | Tema Vibrante | Colores dinámicos |
| `admin:theme:minimal` | Tema Minimal | Diseño limpio |
| `admin:theme:gaming` | Tema Gaming | Estilo gamer |

---

## 🔔 Sistema de Notificaciones Admin

### 📊 Estructura de Notificación

Cuando un usuario muestra interés, el admin recibe:

```
👤 INTERÉS DE USUARIO

🆔 User ID: 12345
📊 Nivel: 5, Puntos: 1250
💎 Estado: FREE
💫 Intimidad: 62%
📈 Racha: 7 días

💎 INTERÉS EN: [Tipo de interés]
🎯 [Mensaje específico del tipo de interés]
```

### 🎯 Tipos de Interés

| Tipo | Mensaje Admin | Prioridad |
|------|---------------|-----------|
| `vip_channel` | "INTERÉS EN DIVÁN VIP - Usuario con alto potencial de conversión" | 🔥 Alta |
| `package:intimate_conversations` | "INTERÉS EN: Conversaciones Íntimas ($29.99) - Oportunidad de conversión alta!" | 🔥 Alta |
| `package:exclusive_photos` | "INTERÉS EN: Fotografías Exclusivas ($19.99) - Lead calificado" | 🟡 Media |
| `package:custom_videos` | "INTERÉS EN: Videos Personalizados ($49.99) - Oportunidad premium" | 🔥 Alta |
| `package:vip_experiences` | "INTERÉS EN: Experiencias VIP ($99.99/mes) - Conversión máxima!" | 🚨 Crítica |

---

## 🎭 Personalidades en Callbacks

### 🌹 Respuestas de Diana

**Tono seductor/vulnerable:**
```
🎭 Diana sonríe con satisfacción:
"He sentido tu llamada... Lucien ya está preparando tu bienvenida especial."

💫 Diana susurra:
"La espera valdrá cada segundo... te lo prometo."
```

### 🎩 Respuestas de Lucien  

**Tono elegante/confirmatorio:**
```
🎩 Lucien confirma:
"Diana ha sido notificada de su interés. Recibirá instrucciones muy pronto."

🎩 Lucien asegura:
"La calidad de esta experiencia superará todas sus expectativas."
```

---

## ⚡ Callbacks de Alto Rendimiento

### 🚀 Optimizados para Velocidad

| Callback | Tiempo Respuesta | Cache |
|----------|------------------|-------|
| `diana:refresh` | <200ms | 5min TTL |
| `admin:main` | <150ms | 2min TTL |
| `admin:system_health` | <300ms | 30sec TTL |

### 🎯 Callbacks Críticos (Sin Cache)

- `diana:interest:*` - Tiempo real para conversiones
- `admin:vip_generate_token` - Tokens únicos
- `admin:system_logs` - Datos en vivo

---

## 🔐 Callbacks con Restricciones

### 👑 Solo VIP

Estos callbacks requieren status VIP:
- `diana:section:exclusive_content` (Galería Privada)
- `diana:section:private_chat` (Chat Privado)

### 🛡️ Solo Admin

Todos los callbacks `admin:*` requieren permisos de administrador validados por `DianaAdminSecurity`.

---

## 🧪 Testing de Callbacks

### 🎪 Pruebas de Usuario

```bash
# Navegación básica
diana:refresh
diana:section:profile

# Flujo de conversión VIP
diana:section:vip_info
diana:interest:vip_channel

# Paquetes premium  
diana:section:content_packages
diana:package:intimate_conversations
diana:interest:package:intimate_conversations
```

### 🏛️ Pruebas Admin

```bash
# Dashboard principal
admin:main
admin:refresh

# Gestión VIP
admin:section:vip
admin:vip_stats
admin:vip_generate_token

# Sistema
admin:system_health
admin:theme:executive
```

---

*Referencia completa de callbacks Diana V2*  
*Última actualización: Agosto 2025*