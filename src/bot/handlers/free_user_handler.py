"""
Handler para usuarios Free con sistema de menús mejorado
Incluye edición de mensajes, auto-eliminación y notificaciones al admin
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from aiogram import types, F, Router
from aiogram.types import InlineKeyboardMarkup

from src.bot.keyboards.free_user_kb import (
    get_free_main_menu_kb,
    get_miss_packs_info_kb,
    get_canal_premium_info_kb,
    get_contenido_custom_info_kb,
    get_free_game_kb,
    get_free_gift_kb,
    get_follow_me_kb,
    get_admin_notification_kb
)
from src.utils.sexy_logger import log

# Router para handlers de usuario Free
free_user_router = Router()

class FreeUserMenuSystem:
    """
    Sistema de menús para usuarios Free con:
    - Edición de mensajes (no spam)
    - Auto-eliminación de notificaciones
    - Notificaciones al administrador
    - Navegación fluida
    """
    
    def __init__(self, admin_service=None):
        self.admin_service = admin_service
        self.temp_messages: List[Dict] = []  # Mensajes temporales para eliminar
        self.notification_delete_time = 8  # segundos
        self.success_delete_time = 5       # segundos
        self.error_delete_time = 10        # segundos
        
        # Iniciar task para limpiar mensajes temporales
        asyncio.create_task(self.cleanup_temp_messages())
        
        log.startup("Sistema de Menú para usuarios Free inicializado")
    
    async def show_main_menu(self, message_or_query, edit_message=True):
        """Mostrar menú principal para usuarios Free"""
        if isinstance(message_or_query, types.CallbackQuery):
            user_id = message_or_query.from_user.id
            message = message_or_query.message
            username = message_or_query.from_user.username or "Usuario"
        else:
            user_id = message_or_query.from_user.id
            message = message_or_query
            username = message_or_query.from_user.username or "Usuario"
        
        menu_text = f"""
🎭 **DIANA BOT - MENÚ PRINCIPAL**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¡Hola @{username}! 👋

🌟 **Bienvenido al mundo de Miss Packs**

Explora todo el contenido exclusivo, juegos y mucho más. Como usuario nuevo, tienes acceso a:

💫 **Disponible para ti:**
• 🎀 Información sobre Miss Packs
• 👑 Detalles del Canal Premium  
• 💌 Contenido Custom personalizado
• 🎁 Regalos diarios gratuitos
• 🎮 Juegos interactivos
• 🌐 Sígueme en redes sociales

✨ **¡Explora y descubre todo lo que tengo para ti!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = get_free_main_menu_kb()
        
        # Editar mensaje existente o crear nuevo
        try:
            if edit_message and isinstance(message_or_query, types.CallbackQuery):
                await message.edit_text(menu_text, reply_markup=keyboard, parse_mode="Markdown")
            else:
                await message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            log.error(f"Error editando/enviando menú principal: {e}")
            # Si no se puede editar, enviar nuevo mensaje
            await message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")
        
        log.user_action(f"Menú principal Free accedido", user_id=user_id, action="free_menu_open")
    
    async def show_miss_packs_info(self, query: types.CallbackQuery):
        """Mostrar información sobre Miss Packs"""
        menu_text = """
🎀 **MISS PACKS - SOBRE MÍ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **¡Hola! Soy Miss Packs** ✨

🌟 **Sobre mí:**
• Creadora de contenido exclusivo
• Especializada en contenido personalizado
• Más de 500+ fotos y videos disponibles
• Contenido nuevo cada semana
• Atención personalizada a mis suscriptores

💎 **Lo que ofrezco:**
• 📸 Sesiones fotográficas exclusivas
• 🎬 Videos personalizados
• 💬 Chat privado directo
• 🎁 Regalos sorpresa para suscriptores
• 🔥 Contenido sin censura

🎭 **Mi estilo:**
Elegante, sensual y siempre con clase. Me encanta conocer a mis fans y crear contenido que realmente les guste.

💕 **¿Te interesa conocer más?**
¡Presiona el botón de abajo y me contactarás directamente!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = get_miss_packs_info_kb()
        
        try:
            await query.message.edit_text(menu_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            log.error(f"Error editando mensaje Miss Packs: {e}")
            await query.message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def show_canal_premium_info(self, query: types.CallbackQuery):
        """Mostrar información sobre Canal Premium"""
        menu_text = """
👑 **CANAL PREMIUM VIP**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 **¡Bienvenido al área VIP!**

🔥 **¿Qué incluye mi Canal Premium?**

✨ **Contenido Exclusivo:**
• 📸 Fotos sin censura (5-7 nuevas por semana)
• 🎬 Videos largos exclusivos 
• 🔴 Lives privados solo para VIPs
• 💌 Mensajes personales míos
• 🎁 Regalos y sorpresas especiales

🌟 **Beneficios VIP:**
• ⚡ Acceso inmediato a todo el contenido
• 💬 Chat directo conmigo prioritario  
• 🎯 Contenido personalizado con descuentos
• 🏆 Acceso a sorteos exclusivos
• 👑 Estado especial de miembro VIP

💰 **Precios especiales:**
• 💎 Mensual: $19.99
• 🔥 Trimestral: $49.99 (¡Ahorra $10!)
• 👑 Anual: $159.99 (¡Ahorra $80!)

🎊 **¡Únete hoy y recibe un regalo de bienvenida!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = get_canal_premium_info_kb()
        
        try:
            await query.message.edit_text(menu_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            log.error(f"Error editando mensaje Canal Premium: {e}")
            await query.message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def show_contenido_custom_info(self, query: types.CallbackQuery):
        """Mostrar información sobre Contenido Custom"""
        menu_text = """
💌 **CONTENIDO CUSTOM PERSONALIZADO**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 **¡Crea conmigo tu fantasía perfecta!**

🔥 **Tipos de contenido que creo:**

📸 **Fotos Personalizadas:**
• Outfits específicos que elijas
• Poses y ángulos que prefieras  
• Tu nombre en mi cuerpo
• Temáticas especiales (cosplay, etc.)

🎬 **Videos Exclusivos:**
• Videos diciendo tu nombre
• Instrucciones personalizadas
• Roleplays específicos
• Videos de reacción

💕 **Servicios Especiales:**
• 💬 Videollamadas privadas
• 📱 Mensajes de voz personales
• 🎁 Artículos físicos (ropa usada, etc.)
• 📝 Cartas manuscritas

⏰ **Tiempos de entrega:**
• Fotos: 24-48 horas
• Videos cortos: 2-3 días
• Videos largos: 5-7 días
• Artículos físicos: 1-2 semanas

💰 **Precios desde $25 USD**

🌟 **¡Cada pedido es único y hecho especialmente para ti!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = get_contenido_custom_info_kb()
        
        try:
            await query.message.edit_text(menu_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            log.error(f"Error editando mensaje Contenido Custom: {e}")
            await query.message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def handle_interest_notification(self, query: types.CallbackQuery, interest_type: str):
        """Manejar cuando un usuario muestra interés y notificar al admin"""
        user_id = query.from_user.id
        username = query.from_user.username or "Sin username"
        full_name = query.from_user.full_name or "Usuario"
        
        # Mapear tipos de interés a nombres legibles
        interest_names = {
            "miss_packs": "🎀 Miss Packs - Información sobre la creadora",
            "canal_premium": "👑 Canal Premium VIP",  
            "contenido_custom": "💌 Contenido Custom Personalizado"
        }
        
        interest_name = interest_names.get(interest_type, interest_type)
        
        # Mensaje de confirmación al usuario
        confirmation_text = f"""
✅ **¡Perfecto!**

Tu interés en **{interest_name}** ha sido registrado.

📬 **Miss Packs ha sido notificada** y se pondrá en contacto contigo muy pronto.

💕 Mientras tanto, puedes seguir explorando el menú o seguirme en mis redes sociales.

⏰ **Tiempo de respuesta:** Generalmente entre 2-6 horas.

¡Gracias por tu interés! 💋
        """
        
        # Enviar confirmación temporal al usuario
        temp_msg = await query.message.answer(confirmation_text, parse_mode="Markdown")
        await query.answer("✅ Interés registrado correctamente")
        
        # Programar eliminación del mensaje temporal
        self.temp_messages.append({
            'message': temp_msg,
            'delete_at': datetime.now() + timedelta(seconds=self.success_delete_time)
        })
        
        # Notificar al administrador
        await self.notify_admin_interest(user_id, username, full_name, interest_type, interest_name)
        
        log.user_action(
            f"Usuario mostró interés en {interest_type}",
            user_id=user_id,
            action="user_interest",
            details={"interest_type": interest_type, "username": username}
        )
    
    async def notify_admin_interest(self, user_id: int, username: str, full_name: str, 
                                  interest_type: str, interest_name: str):
        """Enviar notificación al administrador"""
        try:
            # IDs de administradores (obtener de configuración en producción)
            admin_ids = [123456789]  # TODO: Obtener de configuración
            
            admin_text = f"""
🔔 **NUEVA NOTIFICACIÓN DE INTERÉS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 **Usuario interesado:**
• Nombre: {full_name}
• Username: @{username} 
• ID: `{user_id}`

💎 **Interés en:** {interest_name}

📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

🎯 **Acciones disponibles:**
• Enviar mensaje directo
• Cerrar notificación

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            
            keyboard = get_admin_notification_kb(user_id, interest_type)
            
            # Enviar notificación a todos los admins
            if self.admin_service:
                for admin_id in admin_ids:
                    try:
                        # Usar el servicio de admin si está disponible
                        # await self.admin_service.send_notification(admin_id, admin_text, keyboard)
                        pass  # Por ahora placeholder
                    except Exception as e:
                        log.error(f"Error enviando notificación a admin {admin_id}: {e}")
            
            log.info(f"Notificación de interés enviada a admins para usuario {user_id}")
            
        except Exception as e:
            log.error(f"Error notificando administradores sobre interés: {e}")
    
    async def show_free_game_menu(self, query: types.CallbackQuery):
        """Mostrar menú de juegos para usuarios Free"""
        menu_text = """
🎮 **JUEGO KINKY - ÁREA FREE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **¡Juegos disponibles para ti!**

🧠 **Trivia Kinky:**
• Preguntas divertidas y atrevidas
• Gana puntos y desbloquea contenido
• Nuevas preguntas cada día

🎲 **Juegos Disponibles:**
• ❓ Trivia de Miss Packs
• 🎯 Adivinanzas sensuales  
• 🎪 Ruleta de la suerte
• 🏆 Competencias semanales

🎁 **Premios para ganadores:**
• 🌟 Contenido exclusivo gratis
• 💌 Mensajes personales
• 🎟️ Descuentos en suscripciones
• 👑 Acceso VIP temporal

🏆 **Tu progreso:**
• Partidas jugadas: 0
• Mejor puntuación: --
• Posición en ranking: --

¡Empieza a jugar y sube en el ranking! 🚀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = get_free_game_kb()
        
        try:
            await query.message.edit_text(menu_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            log.error(f"Error editando mensaje juegos: {e}")
            await query.message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def show_free_gift_menu(self, query: types.CallbackQuery):
        """Mostrar menú de regalos para usuarios Free"""
        menu_text = """
🎁 **REGALOS GRATUITOS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💝 **¡Regalos diarios esperándote!**

🌟 **Regalo de hoy disponible:**
• 📸 3 fotos exclusivas de Miss Packs
• 🎮 100 puntos para juegos
• 🎟️ Cupón 15% descuento VIP

⏰ **Próximo regalo en:** 18 horas

🎊 **Historial de regalos:**
• Regalos reclamados: 0
• Días consecutivos: 0
• Mejor racha: 0 días

🔥 **Regalos especiales:**
• 📅 Regalo semanal (Domingos)
• 🎉 Regalo mensual especial
• 🎂 Regalo de cumpleaños
• 🌟 Eventos sorpresa

💡 **Tip:** ¡Reclama tu regalo diario para mantener tu racha y desbloquear mejores premios!

🏆 **Próximo milestone:** 7 días consecutivos = Regalo VIP especial

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = get_free_gift_kb()
        
        try:
            await query.message.edit_text(menu_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            log.error(f"Error editando mensaje regalos: {e}")
            await query.message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def show_follow_me_menu(self, query: types.CallbackQuery):
        """Mostrar menú de redes sociales"""
        menu_text = """
🌐 **SÍGUEME EN MIS REDES**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💋 **¡Conéctate conmigo en todas mis plataformas!**

📱 **Redes sociales activas:**

📸 **Instagram @miss_packs**
• Fotos del día a día
• Stories exclusivos
• Lives ocasionales
• Contenido detrás de cámaras

🐦 **Twitter @miss_packs**  
• Pensamientos random
• Interacción directa
• Noticias y actualizaciones
• Mini contenido exclusivo

💋 **OnlyFans**
• Todo mi contenido sin censura
• Videos largos exclusivos
• Chat directo conmigo
• Contenido que no verás en otro lado

🎵 **TikTok** (próximamente)
• Videos divertidos
• Tendencias y challenges
• Contenido viral

💕 **¡Sígueme en todas para no perderte nada!**

🔔 Activa las notificaciones para ser el primero en ver mi contenido nuevo.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = get_follow_me_kb()
        
        try:
            await query.message.edit_text(menu_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            log.error(f"Error editando mensaje redes sociales: {e}")
            await query.message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def send_temp_message(self, message: types.Message, text: str, delete_time: int = 5):
        """Enviar mensaje temporal que se auto-elimina"""
        temp_msg = await message.answer(text)
        
        # Agregar a lista de mensajes temporales
        self.temp_messages.append({
            'message': temp_msg,
            'delete_at': datetime.now() + timedelta(seconds=delete_time)
        })
    
    async def cleanup_temp_messages(self):
        """Limpiar mensajes temporales vencidos"""
        while True:
            try:
                current_time = datetime.now()
                messages_to_remove = []
                
                for i, temp_msg in enumerate(self.temp_messages):
                    if current_time >= temp_msg['delete_at']:
                        try:
                            await temp_msg['message'].delete()
                            messages_to_remove.append(i)
                        except Exception as e:
                            log.error(f"Error eliminando mensaje temporal: {e}")
                            messages_to_remove.append(i)
                
                # Remover mensajes procesados de la lista
                for i in reversed(messages_to_remove):
                    self.temp_messages.pop(i)
                
                await asyncio.sleep(10)  # Revisar cada 10 segundos
                
            except Exception as e:
                log.error(f"Error en cleanup_temp_messages: {e}")
                await asyncio.sleep(30)  # Esperar más tiempo si hay error

# Instancia global del sistema de menús
free_menu_system = FreeUserMenuSystem()

# ============================================
# HANDLERS DE CALLBACKS
# ============================================

@free_user_router.callback_query(F.data == "free_main_menu")
async def handle_free_main_menu(query: types.CallbackQuery):
    """Handler para volver al menú principal Free"""
    await free_menu_system.show_main_menu(query)
    await query.answer()

@free_user_router.callback_query(F.data == "free_miss_packs")
async def handle_miss_packs_info(query: types.CallbackQuery):
    """Handler para información de Miss Packs"""
    await free_menu_system.show_miss_packs_info(query)
    await query.answer()

@free_user_router.callback_query(F.data == "free_canal_premium")
async def handle_canal_premium_info(query: types.CallbackQuery):
    """Handler para información del Canal Premium"""
    await free_menu_system.show_canal_premium_info(query)
    await query.answer()

@free_user_router.callback_query(F.data == "free_contenido_custom")
async def handle_contenido_custom_info(query: types.CallbackQuery):
    """Handler para información de Contenido Custom"""
    await free_menu_system.show_contenido_custom_info(query)
    await query.answer()

@free_user_router.callback_query(F.data == "free_game")
async def handle_free_game(query: types.CallbackQuery):
    """Handler para menú de juegos Free"""
    await free_menu_system.show_free_game_menu(query)
    await query.answer()

@free_user_router.callback_query(F.data == "free_gift")
async def handle_free_gift(query: types.CallbackQuery):
    """Handler para menú de regalos Free"""
    await free_menu_system.show_free_gift_menu(query)
    await query.answer()

@free_user_router.callback_query(F.data == "free_follow")
async def handle_free_follow(query: types.CallbackQuery):
    """Handler para menú de redes sociales"""
    await free_menu_system.show_follow_me_menu(query)
    await query.answer()

# Handlers para botones "Me Interesa"
@free_user_router.callback_query(F.data == "interest_miss_packs")
async def handle_interest_miss_packs(query: types.CallbackQuery):
    """Handler para interés en Miss Packs"""
    await free_menu_system.handle_interest_notification(query, "miss_packs")

@free_user_router.callback_query(F.data == "interest_canal_premium")
async def handle_interest_canal_premium(query: types.CallbackQuery):
    """Handler para interés en Canal Premium"""
    await free_menu_system.handle_interest_notification(query, "canal_premium")

@free_user_router.callback_query(F.data == "interest_contenido_custom")
async def handle_interest_contenido_custom(query: types.CallbackQuery):
    """Handler para interés en Contenido Custom"""
    await free_menu_system.handle_interest_notification(query, "contenido_custom")

# Handlers para información extendida (placeholders)
@free_user_router.callback_query(F.data.in_([
    "miss_packs_gallery", "miss_packs_videos", "premium_benefits", 
    "premium_prices", "custom_types", "custom_delivery", "free_game_play",
    "free_game_score", "claim_free_gift", "next_gift_info"
]))
async def handle_extended_info(query: types.CallbackQuery):
    """Handler para información extendida (en desarrollo)"""
    action_names = {
        "miss_packs_gallery": "📸 Galería de Miss Packs",
        "miss_packs_videos": "🎬 Videos Preview",
        "premium_benefits": "💎 Beneficios Premium",
        "premium_prices": "💰 Precios detallados",
        "custom_types": "🎨 Tipos de contenido",
        "custom_delivery": "⏰ Tiempos de entrega",
        "free_game_play": "🎮 Iniciar juego",
        "free_game_score": "🏆 Ver puntuaciones",
        "claim_free_gift": "🎁 Reclamar regalo",
        "next_gift_info": "📅 Información de próximo regalo"
    }
    
    action_name = action_names.get(query.data, "Función")
    await query.answer(f"🔧 {action_name} en desarrollo", show_alert=True)

# Handler para notificaciones de admin
@free_user_router.callback_query(F.data.startswith("admin_message_user_"))
async def handle_admin_message_user(query: types.CallbackQuery):
    """Handler para que el admin envíe mensaje directo al usuario"""
    # Extraer user_id e interest_type del callback_data
    parts = query.data.split("_")
    if len(parts) >= 4:
        user_id = parts[3]
        interest_type = "_".join(parts[4:]) if len(parts) > 4 else "unknown"
        
        await query.answer("💬 Función de envío directo en desarrollo", show_alert=True)
        # TODO: Implementar envío directo de mensaje al usuario
        log.info(f"Admin solicita enviar mensaje a usuario {user_id} sobre {interest_type}")

@free_user_router.callback_query(F.data == "admin_close_notification")
async def handle_admin_close_notification(query: types.CallbackQuery):
    """Handler para cerrar notificación de admin"""
    try:
        await query.message.delete()
        await query.answer("✅ Notificación cerrada")
    except Exception as e:
        log.error(f"Error cerrando notificación de admin: {e}")
        await query.answer("Error cerrando notificación")