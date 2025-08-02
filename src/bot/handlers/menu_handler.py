"""
Handler para el sistema de menús de Diana Bot V2
Conecta los menús con los handlers EXISTENTES del bot
"""

from aiogram import types, F, Router
from aiogram.filters import Command

from src.bot.core.menu_system import diana_menu_system, UserRole
from src.utils.sexy_logger import log
from src.core.services.config import CentralConfig

# TODO: Importar handlers existentes cuando estén disponibles
# from src.bot.handlers.user.profile import profile_handler
# from src.bot.handlers.user.shop import shop_handler  
# from src.bot.handlers.user.trivia import trivia_handler
# from src.bot.handlers.user.daily_rewards import daily_rewards_handler
# from src.bot.handlers.user.help import help_handler
# from src.bot.handlers.user.info import info_handler
# from src.bot.handlers.user.start import start_handler
# from src.bot.handlers.narrative.mochila import mochila_handler
# from src.bot.handlers.gamification.misiones import misiones_handler
# from src.bot.handlers.admin.role_management import role_management_handler
# from src.bot.handlers.admin.tariff import tariff_handler

# Router para los handlers de menú
menu_router = Router()

class MenuHandler:
    """Handler para gestionar todos los callbacks y comandos de menú"""
    
    def __init__(self, admin_service=None, gamification_service=None, 
                 narrative_service=None, channel_service=None, user_service=None):
        self.admin_service = admin_service
        self.gamification_service = gamification_service
        self.narrative_service = narrative_service
        self.channel_service = channel_service
        self.user_service = user_service
        self.config = CentralConfig()
    
    async def get_user_role(self, user_id: int) -> UserRole:
        """Obtener el rol real del usuario desde la base de datos"""
        try:
            if self.user_service:
                user_data = await self.user_service.get_user_info(user_id)
                if user_data:
                    if user_data.get('is_admin', False):
                        return UserRole.ADMIN
                    elif user_data.get('is_vip', False):
                        return UserRole.VIP
                    else:
                        return UserRole.FREE
            
            # Verificar si es admin desde configuración
            admin_ids = self.config.get("admin.user_ids", [])
            if user_id in admin_ids:
                return UserRole.ADMIN
            
            return UserRole.FREE
            
        except Exception as e:
            log.error(f"Error obteniendo rol de usuario {user_id}", error=e)
            return UserRole.FREE
    
    async def handle_callback_query(self, query: types.CallbackQuery) -> None:
        """Handler principal para todos los callbacks de menú"""
        
        user_id = query.from_user.id
        callback_data = query.data
        
        log.user_action(
            f"Callback recibido: {callback_data}",
            user_id=user_id,
            action="menu_callback"
        )
        
        try:
            # Obtener rol del usuario
            user_role = await self.get_user_role(user_id)
            
            # Enrutar callbacks de navegación de menú
            if callback_data.startswith("menu_"):
                menu_name = callback_data.replace("menu_", "")
                await diana_menu_system.show_menu(query, menu_name, user_role)
                
            elif callback_data == "main_admin":
                if user_role != UserRole.ADMIN:
                    await query.answer("❌ No tienes permisos de administrador", show_alert=True)
                    return
                await diana_menu_system.show_menu(query, "main_admin", user_role)
                
            elif callback_data == "main_user":
                await diana_menu_system.show_menu(query, "main_user", user_role)
                
            elif callback_data == "admin_panel":
                if user_role != UserRole.ADMIN:
                    await query.answer("❌ No tienes permisos de administrador", show_alert=True)
                    return
                await diana_menu_system.show_menu(query, "main_admin", user_role)
                
            elif callback_data == "close_menu":
                await query.message.delete()
                await query.answer("🔒 Menú cerrado")
                
            elif callback_data == "refresh_admin":
                if user_role != UserRole.ADMIN:
                    await query.answer("❌ No tienes permisos de administrador", show_alert=True)
                    return
                await diana_menu_system.show_menu(query, "main_admin", user_role)
                await query.answer("🔄 Panel actualizado")
                
            else:
                # Callbacks específicos de funcionalidades - CONECTAR CON HANDLERS EXISTENTES
                await self._handle_specific_callback(query, callback_data, user_role)
                
        except Exception as e:
            log.error(f"Error manejando callback {callback_data}", error=e)
            await query.answer("❌ Error procesando acción", show_alert=True)
    
    async def _handle_specific_callback(self, query: types.CallbackQuery, 
                                      callback_data: str, user_role: UserRole) -> None:
        """Manejar callbacks específicos - CONECTAR CON HANDLERS EXISTENTES"""
        
        # ============================================
        # CALLBACKS DE USUARIO - CONECTAR CON HANDLERS EXISTENTES
        # ============================================
        
        if callback_data == "user_profile":
            # Conectar con el handler existente de /profile
            await query.answer("👤 Abriendo perfil...")
            # TODO: Conectar con handler real de /profile
            await query.message.reply("👤 **MI PERFIL**\n━━━━━━━━━━━━━━━━━━━━━\n\n🔄 Conectando con handler de /profile...\n\n⚠️ **Funcionalidad en desarrollo**")
            
        elif callback_data == "shop":
            # Conectar con el handler existente de /tienda
            await query.answer("🛍️ Abriendo tienda...")
            # TODO: Conectar con handler real de /tienda
            await query.message.reply("🛍️ **TIENDA DE BESITOS**\n━━━━━━━━━━━━━━━━━━━━━\n\n🔄 Conectando con handler de /tienda...\n\n⚠️ **Funcionalidad en desarrollo**")
            
        elif callback_data == "user_games":
            # Conectar con el handler existente de /trivia
            await query.answer("🎮 Abriendo trivias...")
            # TODO: Conectar con handler real de /trivia
            await query.message.reply("🎮 **TRIVIAS Y JUEGOS**\n━━━━━━━━━━━━━━━━━━━━━\n\n🔄 Conectando con handler de /trivia...\n\n⚠️ **Funcionalidad en desarrollo**")
            
        elif callback_data == "user_missions":
            # Conectar con el handler existente de /misiones
            await query.answer("🎯 Cargando misiones...")
            # TODO: Conectar con handler real de /misiones
            await query.message.reply("🎯 **MISIONES ACTIVAS**\n━━━━━━━━━━━━━━━━━━━━━\n\n🔄 Conectando con handler de /misiones...\n\n⚠️ **Funcionalidad en desarrollo**")
            
        elif callback_data == "daily_gift":
            # Conectar con el handler existente de /regalo
            await query.answer("🎁 Procesando regalo diario...")
            # TODO: Conectar con handler real de /regalo
            await query.message.reply("🎁 **REGALO DIARIO**\n━━━━━━━━━━━━━━━━━━━━━\n\n🔄 Conectando con handler de /regalo...\n\n⚠️ **Funcionalidad en desarrollo**")
            
        elif callback_data == "user_inventory":
            # Conectar con el handler existente de /mochila
            await query.answer("🎒 Abriendo mochila...")
            # TODO: Conectar con handler real de /mochila
            await query.message.reply("🎒 **MI MOCHILA**\n━━━━━━━━━━━━━━━━━━━━━\n\n🔄 Conectando con handler de /mochila...\n\n⚠️ **Funcionalidad en desarrollo**")
            
        elif callback_data == "vip_section":
            if user_role == UserRole.FREE:
                await query.answer("👑 Contenido exclusivo VIP. ¡Hazte VIP para acceder!", show_alert=True)
                return
            await query.answer("👑 Accediendo a contenido VIP...")
            # TODO: Implementar sección VIP exclusiva
            log.info(f"Usuario VIP {query.from_user.id} accedió a sección VIP desde menú")
        
        # ============================================
        # CALLBACKS DE ADMINISTRACIÓN - CONECTAR CON HANDLERS EXISTENTES
        # ============================================
        
        elif callback_data == "manage_roles":
            if user_role != UserRole.ADMIN:
                await query.answer("❌ Solo administradores", show_alert=True)
                return
            
            await query.answer("🎭 Abriendo gestión de roles...")
            # TODO: Conectar con handler real de /roles
            await query.message.reply("🎭 **GESTIÓN DE ROLES**\n━━━━━━━━━━━━━━━━━━━━━\n\n🔄 Conectando con handler de /roles...\n\n⚠️ **Funcionalidad en desarrollo**")
            
        elif callback_data == "vip_tokens":
            if user_role != UserRole.ADMIN:
                await query.answer("❌ Solo administradores", show_alert=True)
                return
            
            await query.answer("🎟️ Abriendo gestión de tarifas...")
            # TODO: Conectar con handler real de /tarifas
            await query.message.reply("🎟️ **GESTIÓN DE TOKENS VIP**\n━━━━━━━━━━━━━━━━━━━━━\n\n🔄 Conectando con handler de /tarifas...\n\n⚠️ **Funcionalidad en desarrollo**")
        
        # ============================================
        # CALLBACKS NUEVOS - ADMINISTRACIÓN DE CANALES
        # ============================================
        
        elif callback_data == "add_channel":
            await self._handle_add_channel(query, user_role)
            
        elif callback_data == "edit_channels":
            await self._handle_edit_channels(query, user_role)
            
        elif callback_data == "delete_channel":
            await self._handle_delete_channel(query, user_role)
            
        elif callback_data == "channel_status":
            await self._handle_channel_status(query, user_role)
            
        elif callback_data == "channel_members":
            await self._handle_channel_members(query, user_role)
            
        elif callback_data == "quick_actions":
            await self._handle_quick_actions(query, user_role)
        
        # ============================================
        # CALLBACKS EN DESARROLLO
        # ============================================
        
        else:
            # Callback no reconocido o en desarrollo
            await query.answer(f"🔧 Función '{callback_data}' en desarrollo", show_alert=False)
            log.warning(f"Callback no implementado: {callback_data}")
    
    # ============================================
    # HANDLERS NUEVOS - ADMINISTRACIÓN DE CANALES
    # ============================================
    
    async def _handle_add_channel(self, query: types.CallbackQuery, user_role: UserRole):
        """Agregar nuevo canal - NUEVA FUNCIONALIDAD"""
        if user_role != UserRole.ADMIN:
            await query.answer("❌ Solo administradores", show_alert=True)
            return
        
        await query.answer("➕ Iniciando proceso de agregar canal...")
        
        # TODO: Implementar formulario para agregar canal
        # Por ahora, solo enviar instrucciones
        instructions = """
📺 **AGREGAR NUEVO CANAL**
━━━━━━━━━━━━━━━━━━━━━━━━━

Para agregar un canal, necesitas:

1️⃣ **ID del canal** (formato: -100xxxxxxxxx)
2️⃣ **Nombre del canal**
3️⃣ **Tipo** (gratuito o VIP)
4️⃣ **Descripción**

📝 Envía los datos en este formato:
`/add_canal -100123456789 "Mi Canal" vip "Descripción del canal"`

⚠️ **Nota:** Esta funcionalidad está en desarrollo.
        """
        
        await query.message.reply(instructions, parse_mode='HTML')
        log.info(f"Admin {query.from_user.id} solicita agregar canal")
    
    async def _handle_edit_channels(self, query: types.CallbackQuery, user_role: UserRole):
        """Editar canales existentes"""
        if user_role != UserRole.ADMIN:
            await query.answer("❌ Solo administradores", show_alert=True)
            return
        
        await query.answer("📝 Cargando canales para editar...")
        
        try:
            if self.channel_service:
                channels = await self.channel_service.get_all_channels()
                
                if not channels:
                    await query.message.reply("📺 No hay canales configurados para editar.")
                    return
                
                text = "📝 **CANALES DISPONIBLES PARA EDITAR**\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                for i, channel in enumerate(channels, 1):
                    emoji = "🆓" if channel.get('type') == 'free' else "💎"
                    text += f"{i}. {emoji} **{channel.get('name', 'Sin nombre')}**\n"
                    text += f"   ID: `{channel.get('telegram_id', 'N/A')}`\n"
                    text += f"   Tipo: {channel.get('type', 'N/A')}\n\n"
                
                text += "⚠️ **Funcionalidad de edición en desarrollo**"
                await query.message.reply(text, parse_mode='HTML')
            else:
                await query.message.reply("❌ Servicio de canales no disponible")
                
        except Exception as e:
            log.error("Error obteniendo canales para editar", error=e)
            await query.message.reply("❌ Error obteniendo lista de canales")
        
        log.info(f"Admin {query.from_user.id} accediendo a edición de canales")
    
    async def _handle_delete_channel(self, query: types.CallbackQuery, user_role: UserRole):
        """Eliminar canal"""
        if user_role != UserRole.ADMIN:
            await query.answer("❌ Solo administradores", show_alert=True)
            return
        
        await query.answer("🗑️ Cargando canales para eliminar...")
        await query.message.reply("🗑️ **Función de eliminación de canales en desarrollo**\n\n⚠️ Por seguridad, esta función requiere confirmación especial.")
        log.info(f"Admin {query.from_user.id} accediendo a eliminación de canales")
    
    async def _handle_channel_status(self, query: types.CallbackQuery, user_role: UserRole):
        """Ver estado de canales"""
        if user_role != UserRole.ADMIN:
            await query.answer("❌ Solo administradores", show_alert=True)
            return
        
        await query.answer("🔍 Cargando estado de canales...")
        
        try:
            if self.channel_service:
                channels = await self.channel_service.get_all_channels()
                
                text = "🔍 **ESTADO DE CANALES**\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                if not channels:
                    text += "📺 No hay canales configurados\n"
                else:
                    free_count = sum(1 for c in channels if c.get('type') == 'free')
                    vip_count = sum(1 for c in channels if c.get('type') == 'vip')
                    
                    text += f"📊 **Resumen:**\n"
                    text += f"• Total de canales: {len(channels)}\n"
                    text += f"• Canales gratuitos: {free_count}\n" 
                    text += f"• Canales VIP: {vip_count}\n\n"
                    
                    text += f"📺 **Lista detallada:**\n"
                    for channel in channels:
                        emoji = "🆓" if channel.get('type') == 'free' else "💎"
                        status = "✅ Activo" if channel.get('is_active', True) else "❌ Inactivo"
                        text += f"{emoji} **{channel.get('name', 'Sin nombre')}** - {status}\n"
                
                await query.message.reply(text, parse_mode='HTML')
            else:
                await query.message.reply("❌ Servicio de canales no disponible")
                
        except Exception as e:
            log.error("Error obteniendo estado de canales", error=e)
            await query.message.reply("❌ Error obteniendo estado de canales")
        
        log.info(f"Admin {query.from_user.id} consultando estado de canales")
    
    async def _handle_channel_members(self, query: types.CallbackQuery, user_role: UserRole):
        """Gestionar miembros de canales"""
        if user_role != UserRole.ADMIN:
            await query.answer("❌ Solo administradores", show_alert=True)
            return
        
        await query.answer("👥 Cargando gestión de miembros...")
        await query.message.reply("👥 **Gestión de miembros de canales en desarrollo**\n\n📋 Funcionalidades planificadas:\n• Ver miembros por canal\n• Expulsar usuarios\n• Gestionar permisos\n• Estadísticas de membresía")
        log.info(f"Admin {query.from_user.id} accediendo a gestión de miembros")
    
    async def _handle_quick_actions(self, query: types.CallbackQuery, user_role: UserRole):
        """Acciones rápidas de canal"""
        if user_role != UserRole.ADMIN:
            await query.answer("❌ Solo administradores", show_alert=True)
            return
        
        await query.answer("⚡ Cargando acciones rápidas...")
        
        quick_actions_text = """
⚡ **ACCIONES RÁPIDAS DE CANALES**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 **Acciones disponibles:**

1️⃣ **Expulsar usuario**
   `/kick_user <user_id> <channel_id>`

2️⃣ **Añadir usuario VIP**
   `/add_vip <user_id> <channel_id>`

3️⃣ **Ver estadísticas rápidas**
   `/channel_stats <channel_id>`

4️⃣ **Reiniciar canal**
   `/restart_channel <channel_id>`

⚠️ **Nota:** Funciones en desarrollo
        """
        
        await query.message.reply(quick_actions_text, parse_mode='HTML')
        log.info(f"Admin {query.from_user.id} accediendo a acciones rápidas")


# ============================================
# COMANDOS DE MENÚ - CONECTAR CON EXISTENTES + NUEVOS
# ============================================

@menu_router.message(Command("admin"))
async def admin_command_menu(message: types.Message):
    """Comando /admin - conectar con sistema de menús"""
    user_id = message.from_user.id
    config = CentralConfig()
    
    # Obtener rol del usuario desde configuración
    admin_ids = config.get("admin.user_ids", [])
    user_role = UserRole.ADMIN if user_id in admin_ids else UserRole.FREE
    
    if user_role != UserRole.ADMIN:
        await message.reply("❌ No tienes permisos de administrador")
        return
    
    await diana_menu_system.show_menu(message, "main_admin", user_role)

@menu_router.message(Command("menu"))
async def menu_command(message: types.Message):
    """Comando /menu - NUEVO COMANDO PLANIFICADO"""
    user_id = message.from_user.id
    config = CentralConfig()
    
    # Obtener rol del usuario desde configuración
    admin_ids = config.get("admin.user_ids", [])
    user_role = UserRole.ADMIN if user_id in admin_ids else UserRole.FREE
    
    await diana_menu_system.show_menu(message, "main_user", user_role)

@menu_router.message(Command("perfil"))
async def perfil_command(message: types.Message):
    """Comando /perfil - NUEVO COMANDO PLANIFICADO (alias de /profile)"""
    # TODO: Redirigir al handler existente de /profile
    await message.reply(
        "👤 **MI PERFIL**\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔄 Conectando con handler de /profile...\n\n"
        "⚠️ **Funcionalidad en desarrollo**"
    )

@menu_router.message(Command("dailygift"))
async def dailygift_command(message: types.Message):
    """Comando /dailygift - NUEVO COMANDO PLANIFICADO (alias de /regalo)"""
    # TODO: Redirigir al handler existente de /regalo
    await message.reply(
        "🎁 **REGALO DIARIO**\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔄 Conectando con handler de /regalo...\n\n"
        "⚠️ **Funcionalidad en desarrollo**"
    )

@menu_router.message(Command("historia"))
async def historia_command(message: types.Message):
    """Comando /historia - NUEVO COMANDO PLANIFICADO"""
    await message.reply(
        "📖 **NAVEGACIÓN NARRATIVA**\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎭 Bienvenido al sistema narrativo de Diana\n\n"
        "📚 **Opciones disponibles:**\n"
        "• `/mochila` - Ver tus pistas desbloqueadas\n"
        "• `Próximamente:` Continuar historia interactiva\n\n"
        "⚠️ **Función completa en desarrollo**",
        parse_mode='HTML'
    )

@menu_router.message(Command("ruleta"))
async def ruleta_command(message: types.Message):
    """Comando /ruleta - NUEVO COMANDO PLANIFICADO"""
    await message.reply(
        "🎰 **RULETA DE LA FORTUNA**\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎲 ¡Próximamente la ruleta de Diana!\n\n"
        "🎁 **Premios planeados:**\n"
        "• Besitos extra\n"
        "• Pistas narrativas\n" 
        "• Acceso VIP temporal\n"
        "• Artículos exclusivos\n\n"
        "⚠️ **Función en desarrollo**",
        parse_mode='HTML'
    )


# ============================================
# CALLBACK HANDLER PRINCIPAL
# ============================================

@menu_router.callback_query(F.data.regexp(r"^(menu_|main_|close_|refresh_|user_|daily_|shop|admin_panel|vip_section|manage_|add_|edit_|delete_|channel_|quick_)"))
async def menu_callback_handler(query: types.CallbackQuery):
    """Handler para todos los callbacks de menú"""
    # Crear instancia del handler de menú
    menu_handler = MenuHandler()
    await menu_handler.handle_callback_query(query)