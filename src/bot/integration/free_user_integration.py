"""
Integración del sistema de menús Free User con el bot principal
Conecta los nuevos menús con el comando /start y el sistema existente
"""

from aiogram import Router, types, F
from aiogram.filters import Command

from src.bot.handlers.free_user_handler import free_menu_system, free_user_router
from src.utils.sexy_logger import log

# Router principal para la integración
integration_router = Router()

class FreeUserIntegration:
    """
    Clase para integrar el sistema de menús Free User con el bot principal
    """
    
    def __init__(self, user_service=None):
        self.user_service = user_service
    
    async def get_user_role(self, user_id: int) -> str:
        """Determinar el rol del usuario"""
        try:
            if self.user_service:
                user_data = await self.user_service.get_user_info(user_id)
                if user_data:
                    if user_data.get('is_admin', False):
                        return 'admin'
                    elif user_data.get('is_vip', False):
                        return 'vip'
                    else:
                        return 'free'
            
            # Fallback: verificar si es admin hardcodeado
            admin_ids = [123456789]  # TODO: Obtener de configuración
            if user_id in admin_ids:
                return 'admin'
            
            return 'free'  # Por defecto, usuarios nuevos son Free
            
        except Exception as e:
            log.error(f"Error obteniendo rol de usuario {user_id}", error=e)
            return 'free'
    
    async def handle_start_command(self, message: types.Message):
        """
        Handler para comando /start que redirige al menú apropiado según el rol
        """
        user_id = message.from_user.id
        username = message.from_user.username or "Usuario"
        full_name = message.from_user.full_name or "Usuario"
        
        try:
            # Obtener rol del usuario
            user_role = await self.get_user_role(user_id)
            
            # Log del acceso
            log.user_action(
                f"Comando /start ejecutado - Rol: {user_role}",
                user_id=user_id,
                action="start_command",
                details={"username": username, "role": user_role}
            )
            
            if user_role == 'free':
                # Mostrar menú Free User
                await self.show_free_user_welcome(message)
                
            elif user_role == 'vip':
                # TODO: Integrar con menú VIP cuando esté implementado
                await self.show_vip_welcome(message)
                
            elif user_role == 'admin':
                # TODO: Integrar con menú Admin cuando esté implementado
                await self.show_admin_welcome(message)
                
        except Exception as e:
            log.error(f"Error en comando /start para usuario {user_id}", error=e)
            await message.reply(
                "❌ Error interno. Por favor intenta de nuevo en unos momentos."
            )
    
    async def show_free_user_welcome(self, message: types.Message):
        """Mostrar bienvenida y menú para usuario Free"""
        
        # Mensaje de bienvenida personalizado
        welcome_text = f"""
🎭 **¡Bienvenido al Bot de Miss Packs!** 🎭

¡Hola! Soy Diana, tu asistente virtual. 

🌟 **Has entrado al mundo exclusivo de Miss Packs**, donde encontrarás:

✨ **Lo mejor de Miss Packs:**
• 🎀 Información sobre la creadora
• 👑 Detalles del Canal Premium VIP
• 💌 Contenido personalizado exclusivo
• 🎁 Regalos diarios gratuitos
• 🎮 Juegos interactivos y trivias
• 🌐 Enlaces a todas las redes sociales

🎯 **Como nuevo usuario**, tienes acceso inmediato a contenido gratuito y la oportunidad de conocer todo lo que Miss Packs tiene para ofrecerte.

💫 **¡Explora el menú de abajo y descubre un mundo de contenido exclusivo!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        # Enviar mensaje de bienvenida
        await message.answer(welcome_text, parse_mode="Markdown")
        
        # Mostrar menú principal Free User
        await free_menu_system.show_main_menu(message, edit_message=False)
    
    async def show_vip_welcome(self, message: types.Message):
        """Mostrar bienvenida para usuario VIP (placeholder)"""
        vip_text = """
👑 **¡BIENVENIDO USUARIO VIP!** 👑

🎭 ¡Hola! Veo que eres un miembro VIP especial.

💎 **Acceso VIP activado** - Tienes acceso a todo el contenido premium.

🔧 **Menú VIP en desarrollo** - Próximamente tendrás tu menú exclusivo con:
• Contenido VIP sin restricciones
• Chat directo prioritario
• Funciones exclusivas
• Y mucho más...

Por ahora, puedes usar el menú estándar:
        """
        
        await message.answer(vip_text, parse_mode="Markdown")
        # Mostrar menú Free como fallback temporal
        await free_menu_system.show_main_menu(message, edit_message=False)
    
    async def show_admin_welcome(self, message: types.Message):
        """Mostrar bienvenida para administrador (placeholder)"""
        admin_text = """
⚡ **ACCESO DE ADMINISTRADOR** ⚡

🎭 Bienvenido, Admin. Acceso total concedido.

🔧 **Panel administrativo disponible:**
• Usa `/admin` para acceder al panel de control
• Gestión completa de usuarios y sistema
• Configuración de canales y contenido

📊 **Estado del sistema:** Operativo
👥 **Usuarios activos:** En línea

Por ahora también tienes acceso al menú estándar:
        """
        
        await message.answer(admin_text, parse_mode="Markdown")
        # Mostrar menú Free como fallback temporal
        await free_menu_system.show_main_menu(message, edit_message=False)

# Instancia global de integración
integration_system = FreeUserIntegration()

# ============================================
# HANDLERS DE INTEGRACIÓN
# ============================================

@integration_router.message(Command("start"))
async def start_command_integration(message: types.Message):
    """
    Handler principal para /start que integra con el sistema de menús
    """
    await integration_system.handle_start_command(message)

@integration_router.message(Command("menu"))
async def menu_command_integration(message: types.Message):
    """
    Handler para comando /menu que redirige al menú apropiado
    """
    user_id = message.from_user.id
    user_role = await integration_system.get_user_role(user_id)
    
    if user_role == 'free':
        await free_menu_system.show_main_menu(message, edit_message=False)
    else:
        # Para VIP y Admin, mostrar menú Free como fallback temporal
        await free_menu_system.show_main_menu(message, edit_message=False)
    
    log.user_action(
        f"Comando /menu ejecutado - Rol: {user_role}",
        user_id=user_id,
        action="menu_command"
    )

def setup_free_user_integration(dp):
    """
    Función para registrar todos los routers del sistema Free User
    """
    try:
        # Incluir router de integración principal
        dp.include_router(integration_router)
        
        # Incluir router de handlers Free User
        dp.include_router(free_user_router)
        
        log.startup("✅ Sistema de menús Free User integrado correctamente")
        
    except Exception as e:
        log.error(f"❌ Error integrando sistema Free User: {e}")
        raise

# ============================================
# FUNCIÓN DE CONFIGURACIÓN PARA EL BOT PRINCIPAL
# ============================================

def configure_free_user_system(dp, user_service=None, admin_service=None):
    """
    Configuración completa del sistema Free User para el bot principal
    
    Args:
        dp: Dispatcher de aiogram
        user_service: Servicio de usuarios (opcional)
        admin_service: Servicio de administración (opcional)
    """
    try:
        # Configurar servicios en el sistema de integración
        integration_system.user_service = user_service
        free_menu_system.admin_service = admin_service
        
        # Registrar todos los routers
        setup_free_user_integration(dp)
        
        log.startup("🎭 Sistema completo Free User configurado exitosamente")
        
        # Log de configuración
        log.info("Sistema Free User incluye:")
        log.info("  • Menú principal con 6 opciones")
        log.info("  • Información de Miss Packs, Canal Premium y Contenido Custom")
        log.info("  • Botones 'Me Interesa' con notificación a admin")
        log.info("  • Edición de mensajes (sin spam)")
        log.info("  • Auto-eliminación de mensajes temporales")
        log.info("  • Integración con comando /start")
        
        return True
        
    except Exception as e:
        log.error(f"❌ Error configurando sistema Free User: {e}")
        return False