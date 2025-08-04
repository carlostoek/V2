Sistema completo de asignación de roles y verificación que incluye:

🔧 Componentes Implementados
1. RoleService (src/bot/services/role.py)
Gestión completa de los tres roles: Admin, VIP, Free
Verificación de permisos granulares
Sincronización automática de administradores desde configuración
Gestión de expiraciones VIP
Estadísticas de roles
2. Filtros de Roles (src/bot/filters/role.py)
RoleFilter: Filtro base para cualquier rol
IsAdminFilter: Específico para administradores
IsVIPFilter: Específico para usuarios VIP
IsVIPOrAdminFilter: Para usuarios VIP o administradores
PermissionFilter: Para permisos específicos
3. Middleware de Roles (src/bot/middlewares/role.py)
RoleMiddleware: Sincronización automática y gestión de contexto
RoleCheckMiddleware: Verificación automática de acceso
4. Handlers de Gestión (src/bot/handlers/admin/role_management.py)
Panel completo de gestión de roles para administradores
Búsqueda y modificación de usuarios
Otorgamiento/revocación de estados VIP y Admin
Estadísticas en tiempo real
5. Tareas de Mantenimiento (src/bot/tasks/role_maintenance.py)
Verificación automática de expiraciones VIP cada hora
Sincronización de roles cada 6 horas
🎯 Características del Sistema
Roles y Permisos
Administradores: Acceso completo, gestión de usuarios, canales, tarifas
VIP: Acceso a contenido premium, canales exclusivos, subastas
Free: Acceso básico, canales gratuitos, funcionalidades estándar
Verificación Automática
Sincronización desde ADMIN_USER_IDS en variables de entorno
Verificación automática de expiraciones VIP
Middleware que añade información de rol a todos los handlers
Uso en Handlers

# Filtro por rol
@router.message(Command("admin"), IsAdminFilter())
async def admin_command(message: Message):
    pass

# Filtro por permiso específico
@router.message(Command("manage"), PermissionFilter("can_manage_users"))
async def manage_command(message: Message):
    pass

# Acceso a información de rol en handlers
async def some_handler(message: Message):
    user_role = message.user_role  # 'admin', 'vip', 'free'
    permissions = message.user_permissions  # Dict con permisos
Panel de Administración
Comando /roles para gestión completa
Búsqueda de usuarios por ID
Otorgamiento/revocación de roles
Estadísticas en tiempo real
Listado de usuarios por rol
El sistema mantiene las convenciones del bot existente y se integra perfectamente con la arquitectura actual. ¿Te gustaría que implemente alguna funcionalidad adicional o modifique algún aspecto esp
