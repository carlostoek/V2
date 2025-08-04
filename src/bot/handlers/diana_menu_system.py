# 🎭 Sistema de Menús Intuitivos - Diana Bot V2
# Basado en el inventario completo de funcionalidades implementadas

from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.filters import Command
from aiogram import F
import logging

# Importaciones de servicios existentes
from src.modules.admin.service import AdminService
from src.modules.gamification.service import GamificationService
from src.modules.shop.service import ShopService
from src.modules.daily_rewards.service import DailyRewardsService
from src.modules.trivia.service import TriviaService

logger = logging.getLogger(__name__)

class DianaMenuSystem:
    def __init__(self):
        self.router = Router()
        self.admin_service = AdminService()
        self.gamification_service = GamificationService()
        self.shop_service = ShopService()
        self.daily_rewards_service = DailyRewardsService()
        self.trivia_service = TriviaService()
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Registra todos los handlers del sistema de menús"""
        # Comando principal
        self.router.message.register(self.show_main_menu, Command("menu"))
        
        # Callbacks principales
        self.router.callback_query.register(self.handle_main_menu, F.data == "main_menu")
        self.router.callback_query.register(self.handle_vip_menu, F.data == "vip_menu")
        self.router.callback_query.register(self.handle_user_menu, F.data == "user_menu")
        self.router.callback_query.register(self.handle_admin_menu, F.data == "admin_menu")
        
        # Submenús específicos
        self.router.callback_query.register(self.handle_vip_submenu, F.data.startswith("vip:"))
        self.router.callback_query.register(self.handle_user_submenu, F.data.startswith("user:"))
        self.router.callback_query.register(self.handle_admin_submenu, F.data.startswith("admin:"))
        
        # Acciones específicas
        self.router.callback_query.register(self.handle_actions, F.data.startswith("action:"))

    # ==================== MENÚ PRINCIPAL ====================
    
    async def show_main_menu(self, message: Message):
        """Muestra el menú principal con opciones VIP en primer nivel"""
        
        text = "🎭 **Diana Bot V2 - Menú Principal**\n\n"
        text += "¡Hola! Soy Diana, tu asistente virtual. ¿Qué te gustaría hacer hoy?\n\n"
        text += "💎 **VIP:** Acceso completo a funciones premium\n"
        text += "🎮 **Usuario:** Funciones básicas disponibles\n"
        text += "🛠️ **Admin:** Panel de administración"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💎 ACCESO VIP", callback_data="vip_menu"),
                InlineKeyboardButton(text="🎮 Menú Usuario", callback_data="user_menu")
            ],
            [
                InlineKeyboardButton(text="🛠️ Panel Admin", callback_data="admin_menu")
            ],
            [
                InlineKeyboardButton(text="ℹ️ Ayuda", callback_data="action:help"),
                InlineKeyboardButton(text="📊 Mi Perfil", callback_data="action:profile")
            ]
        ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

    # ==================== MENÚ VIP (PRIMER NIVEL) ====================
    
    async def handle_vip_menu(self, callback: CallbackQuery):
        """Menú VIP completo con todas las funciones premium"""
        
        user_id = callback.from_user.id
        
        text = "💎 **ÁREA VIP EXCLUSIVA**\n\n"
        text += "🏆 ¡Bienvenido al área premium! Aquí tienes acceso completo a:\n\n"
        text += "🎯 **Subastas Exclusivas** - Puja por objetos únicos\n"
        text += "🛒 **Tienda Premium** - Productos solo para VIP\n"
        text += "🎁 **Regalos Especiales** - Recompensas mejoradas\n"
        text += "🎮 **Gamificación Plus** - Puntos dobles y misiones especiales\n"
        text += "🧠 **Trivias VIP** - Preguntas exclusivas con grandes premios"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🏆 Subastas VIP", callback_data="vip:auctions"),
                InlineKeyboardButton(text="🛒 Tienda Premium", callback_data="vip:shop")
            ],
            [
                InlineKeyboardButton(text="🎁 Regalos VIP", callback_data="vip:rewards"),
                InlineKeyboardButton(text="🎮 Gamificación+", callback_data="vip:gamification")
            ],
            [
                InlineKeyboardButton(text="🧠 Trivias Exclusivas", callback_data="vip:trivia"),
                InlineKeyboardButton(text="🎫 Mis Tokens", callback_data="vip:tokens")
            ],
            [
                InlineKeyboardButton(text="📖 Narrativa VIP", callback_data="vip:narrative"),
                InlineKeyboardButton(text="⚡ Beneficios", callback_data="vip:benefits")
            ],
            [
                InlineKeyboardButton(text="🔙 Menú Principal", callback_data="main_menu")
            ]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

    # ==================== MENÚ USUARIO ====================
    
    async def handle_user_menu(self, callback: CallbackQuery):
        """Menú principal para usuarios regulares"""
        
        user_id = callback.from_user.id
        
        # Obtener datos del usuario
        try:
            user_points = await self.gamification_service.get_user_points(user_id)
            can_claim_reward = await self.daily_rewards_service.can_claim_daily_reward(user_id)
            can_answer_trivia = await self.trivia_service.can_answer_daily(user_id)
        except Exception as e:
            logger.error(f"Error obteniendo datos de usuario: {e}")
            user_points = {"current_points": 0, "level": 1}
            can_claim_reward = False
            can_answer_trivia = False
        
        # Indicadores visuales
        reward_icon = "🎁✨" if can_claim_reward else "🎁"
        trivia_icon = "🧠✨" if can_answer_trivia else "🧠"
        
        text = "🎮 **Área de Usuario**\n\n"
        text += f"👤 **Tu Perfil:**\n"
        text += f"• 💰 Besitos: {user_points.get('current_points', 0)}\n"
        text += f"• 🌟 Nivel: {user_points.get('level', 1)}\n\n"
        text += "🎯 **Actividades Disponibles:**"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{reward_icon} Regalos Diarios", callback_data="user:daily_rewards"),
                InlineKeyboardButton(text=f"{trivia_icon} Trivias", callback_data="user:trivia")
            ],
            [
                InlineKeyboardButton(text="🛒 Tienda", callback_data="user:shop"),
                InlineKeyboardButton(text="🎯 Mis Misiones", callback_data="user:missions")
            ],
            [
                InlineKeyboardButton(text="🏆 Mis Logros", callback_data="user:achievements"),
                InlineKeyboardButton(text="📖 Mi Historia", callback_data="user:narrative")
            ],
            [
                InlineKeyboardButton(text="📊 Estadísticas", callback_data="user:stats"),
                InlineKeyboardButton(text="🎮 Minijuegos", callback_data="user:games")
            ],
            [
                InlineKeyboardButton(text="💎 ¿Quieres ser VIP?", callback_data="action:become_vip")
            ],
            [
                InlineKeyboardButton(text="🔙 Menú Principal", callback_data="main_menu")
            ]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

    # ==================== MENÚ ADMIN ====================
    
    async def handle_admin_menu(self, callback: CallbackQuery):
        """Menú de administración completo"""
        
        # TODO: Verificar permisos de admin aquí
        
        text = "🛠️ **Panel de Administración**\n\n"
        text += "⚡ **Control Total del Bot**\n\n"
        text += "🎛️ **Configuraciones:** Canales, tiempos, parámetros\n"
        text += "💎 **Gestión VIP:** Tarifas, tokens, suscripciones\n"
        text += "👥 **Usuarios:** Estadísticas, roles, moderación\n"
        text += "📊 **Analytics:** Métricas, reportes, monitoreo"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎛️ Configuraciones", callback_data="admin:settings"),
                InlineKeyboardButton(text="💎 Gestión VIP", callback_data="admin:vip_management")
            ],
            [
                InlineKeyboardButton(text="👥 Usuarios", callback_data="admin:users"),
                InlineKeyboardButton(text="📊 Analytics", callback_data="admin:analytics")
            ],
            [
                InlineKeyboardButton(text="🎮 Gamificación", callback_data="admin:gamification_control"),
                InlineKeyboardButton(text="🛒 Tienda Admin", callback_data="admin:shop_control")
            ],
            [
                InlineKeyboardButton(text="📖 Narrativa", callback_data="admin:narrative_control"),
                InlineKeyboardButton(text="🧠 Trivias Admin", callback_data="admin:trivia_control")
            ],
            [
                InlineKeyboardButton(text="🏆 Subastas", callback_data="admin:auction_control"),
                InlineKeyboardButton(text="⚙️ Sistema", callback_data="admin:system")
            ],
            [
                InlineKeyboardButton(text="🔙 Menú Principal", callback_data="main_menu")
            ]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

    # ==================== SUBMENÚS VIP ====================
    
    async def handle_vip_submenu(self, callback: CallbackQuery):
        """Maneja todos los submenús VIP"""
        
        action = callback.data.split(":")[1]
        user_id = callback.from_user.id
        
        if action == "auctions":
            await self.show_vip_auctions(callback)
        elif action == "shop":
            await self.show_vip_shop(callback)
        elif action == "rewards":
            await self.show_vip_rewards(callback)
        elif action == "gamification":
            await self.show_vip_gamification(callback)
        elif action == "trivia":
            await self.show_vip_trivia(callback)
        elif action == "tokens":
            await self.show_vip_tokens(callback)
        elif action == "narrative":
            await self.show_vip_narrative(callback)
        elif action == "benefits":
            await self.show_vip_benefits(callback)

    async def show_vip_auctions(self, callback: CallbackQuery):
        """Submenú de subastas VIP"""
        
        text = "🏆 **Subastas VIP Exclusivas**\n\n"
        text += "💰 **Subastas Activas:** 3 disponibles\n"
        text += "🔥 **Próximas:** 2 subastas programadas\n"
        text += "🎯 **Mis Pujas:** 1 activa\n\n"
        text += "¡Usa tus besitos para pujar por objetos únicos!"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔥 Ver Subastas Activas", callback_data="action:active_auctions"),
                InlineKeyboardButton(text="📅 Próximas Subastas", callback_data="action:upcoming_auctions")
            ],
            [
                InlineKeyboardButton(text="🎯 Mis Pujas", callback_data="action:my_bids"),
                InlineKeyboardButton(text="🏆 Historial", callback_data="action:auction_history")
            ],
            [
                InlineKeyboardButton(text="❓ Cómo Funciona", callback_data="action:auction_help")
            ],
            [
                InlineKeyboardButton(text="🔙 Área VIP", callback_data="vip_menu")
            ]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

    async def show_vip_shop(self, callback: CallbackQuery):
        """Tienda premium VIP"""
        
        user_id = callback.from_user.id
        
        try:
            # Obtener productos VIP de la tienda
            vip_items = await self.shop_service.get_shop_items(user_id, category=None, vip_only=True)
            categories = await self.shop_service.get_categories()
        except Exception as e:
            logger.error(f"Error obteniendo items VIP: {e}")
            vip_items = []
            categories = []
        
        text = "🛒 **Tienda Premium VIP**\n\n"
        text += "💎 **Productos Exclusivos para Miembros VIP**\n\n"
        text += f"🎯 **Productos disponibles:** {len(vip_items)}\n"
        text += "🏷️ **Categorías:** Narrativa Premium, Gamificación Plus, Especiales VIP"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Narrativa Premium", callback_data="action:shop_narrative_vip"),
                InlineKeyboardButton(text="🎮 Gamificación Plus", callback_data="action:shop_gamification_vip")
            ],
            [
                InlineKeyboardButton(text="⭐ Especiales VIP", callback_data="action:shop_special_vip"),
                InlineKeyboardButton(text="🎁 Cajas Misteriosas", callback_data="action:shop_mystery_vip")
            ],
            [
                InlineKeyboardButton(text="🛒 Ver Todo", callback_data="action:shop_all_vip"),
                InlineKeyboardButton(text="💰 Mis Compras", callback_data="action:my_purchases")
            ],
            [
                InlineKeyboardButton(text="🔙 Área VIP", callback_data="vip_menu")
            ]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

    # ==================== SUBMENÚS USUARIO ====================
    
    async def handle_user_submenu(self, callback: CallbackQuery):
        """Maneja todos los submenús de usuario"""
        
        action = callback.data.split(":")[1]
        user_id = callback.from_user.id
        
        if action == "daily_rewards":
            await self.show_daily_rewards(callback)
        elif action == "trivia":
            await self.show_trivia_menu(callback)
        elif action == "shop":
            await self.show_user_shop(callback)
        elif action == "missions":
            await self.show_user_missions(callback)
        elif action == "achievements":
            await self.show_user_achievements(callback)
        elif action == "narrative":
            await self.show_user_narrative(callback)
        elif action == "stats":
            await self.show_user_stats(callback)
        elif action == "games":
            await self.show_minigames(callback)

    async def show_daily_rewards(self, callback: CallbackQuery):
        """Sistema de regalos diarios"""
        
        user_id = callback.from_user.id
        
        try:
            can_claim = await self.daily_rewards_service.can_claim_daily_reward(user_id)
            user_stats = await self.daily_rewards_service.get_user_daily_stats(user_id)
        except Exception as e:
            logger.error(f"Error obteniendo regalos diarios: {e}")
            can_claim = False
            user_stats = {"streak": 0, "total_claimed": 0}
        
        status_text = "🎁✨ ¡DISPONIBLE!" if can_claim else "⏰ Ya reclamado hoy"
        
        text = "🎁 **Regalos Diarios**\n\n"
        text += f"**Estado:** {status_text}\n"
        text += f"🔥 **Racha actual:** {user_stats.get('streak', 0)} días\n"
        text += f"📈 **Total reclamado:** {user_stats.get('total_claimed', 0)} regalos\n\n"
        text += "💡 **¡Mantén tu racha para conseguir mejores recompensas!**"
        
        keyboard_buttons = []
        
        if can_claim:
            keyboard_buttons.append([
                InlineKeyboardButton(text="🎁 ¡RECLAMAR REGALO!", callback_data="action:claim_daily_reward")
            ])
        
        keyboard_buttons.extend([
            [
                InlineKeyboardButton(text="🔥 Ver Ranking", callback_data="action:daily_leaderboard"),
                InlineKeyboardButton(text="📊 Mis Estadísticas", callback_data="action:daily_stats")
            ],
            [
                InlineKeyboardButton(text="🔙 Menú Usuario", callback_data="user_menu")
            ]
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

    async def show_trivia_menu(self, callback: CallbackQuery):
        """Menú de trivias"""
        
        user_id = callback.from_user.id
        
        try:
            can_answer = await self.trivia_service.can_answer_daily(user_id)
            user_stats = await self.trivia_service.get_user_trivia_stats(user_id)
        except Exception as e:
            logger.error(f"Error obteniendo stats de trivia: {e}")
            can_answer = False
            user_stats = {"correct_answers": 0, "total_questions": 0, "accuracy": 0}
        
        status_text = "🧠✨ ¡DISPONIBLE!" if can_answer else "✅ Completada hoy"
        accuracy = user_stats.get('accuracy', 0)
        
        text = "🧠 **Trivias Diarias**\n\n"
        text += f"**Estado:** {status_text}\n"
        text += f"✅ **Respuestas correctas:** {user_stats.get('correct_answers', 0)}\n"
        text += f"📊 **Precisión:** {accuracy:.1f}%\n"
        text += f"🎯 **Total respondidas:** {user_stats.get('total_questions', 0)}\n\n"
        text += "🏆 **¡Responde correctamente para ganar besitos y subir en el ranking!**"
        
        keyboard_buttons = []
        
        if can_answer:
            keyboard_buttons.append([
                InlineKeyboardButton(text="🧠 ¡RESPONDER TRIVIA!", callback_data="action:start_daily_trivia")
            ])
        
        keyboard_buttons.extend([
            [
                InlineKeyboardButton(text="🏆 Ranking", callback_data="action:trivia_leaderboard"),
                InlineKeyboardButton(text="📈 Mis Stats", callback_data="action:my_trivia_stats")
            ],
            [
                InlineKeyboardButton(text="❓ Trivias Anteriores", callback_data="action:previous_trivia")
            ],
            [
                InlineKeyboardButton(text="🔙 Menú Usuario", callback_data="user_menu")
            ]
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

    # ==================== SUBMENÚS ADMIN ====================
    
    async def handle_admin_submenu(self, callback: CallbackQuery):
        """Maneja todos los submenús de administración"""
        
        action = callback.data.split(":")[1]
        
        if action == "settings":
            await self.show_admin_settings(callback)
        elif action == "vip_management":
            await self.show_vip_management(callback)
        elif action == "users":
            await self.show_user_management(callback)
        elif action == "analytics":
            await self.show_analytics(callback)
        # ... más submenús admin

    async def show_admin_settings(self, callback: CallbackQuery):
        """Configuraciones generales del bot"""
        
        text = "🎛️ **Configuraciones del Sistema**\n\n"
        text += "⚙️ **Configuraciones Disponibles:**\n\n"
        text += "📺 **Canales:** Configurar canales gratuitos y VIP\n"
        text += "⏰ **Tiempos:** Tiempos de espera y cooldowns\n"
        text += "🎮 **Gamificación:** Puntos, niveles y recompensas\n"
        text += "💬 **Mensajes:** Mensajes automáticos y notificaciones\n"
        text += "🔐 **Seguridad:** Permisos y restricciones"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                I
