"""Handlers para regalos diarios."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime

from src.modules.daily_rewards.service import DailyRewardsService, DailyReward

daily_rewards_router = Router()

@daily_rewards_router.message(Command("regalo"))
async def cmd_daily_reward(message: Message, daily_rewards_service: DailyRewardsService):
    """Comando principal para regalos diarios."""
    user_id = message.from_user.id
    
    # Obtener estadísticas del usuario
    stats = await daily_rewards_service.get_user_daily_stats(user_id)
    
    if stats["can_claim_today"]:
        # Puede reclamar el regalo
        reward = await daily_rewards_service.get_available_reward(user_id)
        
        if reward:
            # Iconos por rareza
            rarity_icons = {
                "common": "⚪",
                "rare": "🔵", 
                "epic": "🟣",
                "legendary": "🟡"
            }
            
            rarity_icon = rarity_icons.get(reward.rarity, "⚪")
            
            text = (
                "🎁 **Regalo Diario Disponible**\n\n"
                f"{reward.icon} **{reward.name}**\n"
                f"{rarity_icon} *{reward.rarity.title()}*\n\n"
                f"{reward.description}\n\n"
                f"🔥 **Racha consecutiva:** {stats['consecutive_days']} días\n\n"
                "¡Reclama tu regalo para mantener tu racha!"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎁 Reclamar Regalo", callback_data="daily:claim")],
                [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")],
                [InlineKeyboardButton(text="🏆 Ranking Rachas", callback_data="daily:leaderboard")]
            ])
        else:
            text = (
                "🎁 **Sistema de Regalos Diarios**\n\n"
                "No hay regalos disponibles en este momento.\n"
                "Intenta más tarde o contacta soporte."
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")]
            ])
    else:
        # Ya reclamó hoy
        next_claim = stats.get("next_claim_time")
        next_claim_str = ""
        if next_claim:
            hours_remaining = (next_claim - datetime.now()).total_seconds() / 3600
            if hours_remaining > 0:
                next_claim_str = f"⏰ Próximo regalo en: {hours_remaining:.1f} horas\n\n"
        
        text = (
            "🎁 **Regalo Diario**\n\n"
            "Ya has reclamado tu regalo diario de hoy.\n"
            "¡Vuelve mañana para continuar tu racha!\n\n"
            f"{next_claim_str}"
            f"🔥 **Racha actual:** {stats['consecutive_days']} días\n"
            f"📦 **Total reclamados:** {stats['total_claimed']}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")],
            [InlineKeyboardButton(text="🏆 Ranking Rachas", callback_data="daily:leaderboard")],
            [InlineKeyboardButton(text="🎁 Ver Recompensas", callback_data="daily:rewards_info")]
        ])
    
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

@daily_rewards_router.callback_query(F.data == "daily:claim")
async def daily_claim_callback(callback: CallbackQuery, daily_rewards_service: DailyRewardsService):
    """Procesa la reclamación del regalo diario."""
    user_id = callback.from_user.id
    
    # Intentar reclamar el regalo
    result = await daily_rewards_service.claim_daily_reward(user_id)
    
    if result["success"]:
        reward = result["reward"]
        consecutive_days = result["consecutive_days"]
        effects = result["effect"]["effects"]
        
        # Iconos por rareza
        rarity_icons = {
            "common": "⚪",
            "rare": "🔵", 
            "epic": "🟣",
            "legendary": "🟡"
        }
        
        rarity_icon = rarity_icons.get(reward.rarity, "⚪")
        
        text = (
            "🎉 **¡Regalo Reclamado!**\n\n"
            f"{reward.icon} **{reward.name}**\n"
            f"{rarity_icon} *{reward.rarity.title()}*\n\n"
            "**Recompensas obtenidas:**\n"
        )
        
        for effect in effects:
            text += f"• {effect}\n"
        
        text += f"\n🔥 **Racha consecutiva:** {consecutive_days} días"
        
        # Mensajes especiales por racha
        if consecutive_days == 7:
            text += "\n\n🎊 ¡Una semana completa! ¡Increíble dedicación!"
        elif consecutive_days == 30:
            text += "\n\n🏆 ¡Un mes entero! ¡Eres un maestro de la constancia!"
        elif consecutive_days % 10 == 0 and consecutive_days > 0:
            text += f"\n\n✨ ¡{consecutive_days} días consecutivos! ¡Sigue así!"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")],
            [InlineKeyboardButton(text="🏆 Ranking Rachas", callback_data="daily:leaderboard")],
            [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="main_menu")]
        ])
        
        await callback.answer("¡Regalo reclamado exitosamente! 🎉", show_alert=True)
        
    else:
        text = (
            "❌ **Error al Reclamar Regalo**\n\n"
            f"No se pudo reclamar el regalo:\n{result['reason']}\n\n"
            "Intenta nuevamente o contacta soporte si el problema persiste."
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Intentar de Nuevo", callback_data="daily:main")],
            [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")]
        ])
        
        await callback.answer(f"Error: {result['reason']}", show_alert=True)
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

@daily_rewards_router.callback_query(F.data == "daily:stats")
async def daily_stats_callback(callback: CallbackQuery, daily_rewards_service: DailyRewardsService):
    """Muestra las estadísticas de regalos diarios del usuario."""
    user_id = callback.from_user.id
    stats = await daily_rewards_service.get_user_daily_stats(user_id)
    
    text = (
        "📊 **Mis Estadísticas - Regalos Diarios**\n\n"
        f"🔥 **Racha actual:** {stats['consecutive_days']} días\n"
        f"🏆 **Mejor racha:** {stats['best_streak']} días\n"
        f"📦 **Total reclamados:** {stats['total_claimed']}\n\n"
    )
    
    # Estado actual
    if stats["can_claim_today"]:
        text += "✅ **Estado:** Regalo disponible para reclamar\n"
    else:
        text += "⏰ **Estado:** Regalo ya reclamado hoy\n"
        if stats.get("next_claim_time"):
            next_claim = stats["next_claim_time"]
            hours_remaining = (next_claim - datetime.now()).total_seconds() / 3600
            if hours_remaining > 0:
                text += f"⏰ **Próximo regalo:** En {hours_remaining:.1f} horas\n"
    
    # Beneficios por racha
    text += "\n🎯 **Beneficios por racha:**\n"
    
    if stats['consecutive_days'] >= 7:
        text += "• 🎊 Semana completa: +10% probabilidad de raros\n"
    if stats['consecutive_days'] >= 14:
        text += "• 🌟 Dos semanas: +15% probabilidad de épicos\n"
    if stats['consecutive_days'] >= 30:
        text += "• 👑 Un mes: +20% probabilidad de legendarios\n"
    
    if stats['consecutive_days'] < 7:
        text += "• Alcanza 7 días para desbloquear beneficios\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Ver Ranking", callback_data="daily:leaderboard")],
        [InlineKeyboardButton(text="🎁 Ver Recompensas", callback_data="daily:rewards_info")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="daily:main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@daily_rewards_router.callback_query(F.data == "daily:leaderboard")
async def daily_leaderboard_callback(callback: CallbackQuery, daily_rewards_service: DailyRewardsService):
    """Muestra el ranking de rachas consecutivas."""
    leaderboard = await daily_rewards_service.get_streak_leaderboard(limit=10)
    user_id = callback.from_user.id
    
    if not leaderboard:
        text = (
            "🏆 **Ranking de Rachas**\n\n"
            "Aún no hay rachas activas registradas.\n"
            "¡Sé el primero en aparecer en el ranking!"
        )
    else:
        text = "🏆 **Ranking de Rachas Consecutivas**\n\n"
        
        user_position = None
        for i, entry in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            # Marcar si es el usuario actual
            user_marker = " ← TÚ" if entry['user_id'] == user_id else ""
            if entry['user_id'] == user_id:
                user_position = i
            
            text += (
                f"{medal} Usuario {entry['user_id']}{user_marker}\n"
                f"   🔥 {entry['consecutive_days']} días consecutivos\n\n"
            )
        
        # Mostrar posición del usuario si no está en el top 10
        if user_position is None:
            user_stats = await daily_rewards_service.get_user_daily_stats(user_id)
            if user_stats['consecutive_days'] > 0:
                text += f"📍 **Tu posición:** Fuera del top 10 ({user_stats['consecutive_days']} días)\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Mis Estadísticas", callback_data="daily:stats")],
        [InlineKeyboardButton(text="🔄 Recargar Ranking", callback_data="daily:leaderboard")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="daily:main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@daily_rewards_router.callback_query(F.data == "daily:rewards_info")
async def daily_rewards_info_callback(callback: CallbackQuery, daily_rewards_service: DailyRewardsService):
    """Muestra información sobre las recompensas disponibles."""
    rewards = await daily_rewards_service.get_all_rewards()
    
    # Agrupar por rareza
    rewards_by_rarity = {}
    for reward in rewards:
        if reward.rarity not in rewards_by_rarity:
            rewards_by_rarity[reward.rarity] = []
        rewards_by_rarity[reward.rarity].append(reward)
    
    text = "🎁 **Recompensas Disponibles**\n\n"
    
    # Iconos y orden por rareza
    rarity_order = ["common", "rare", "epic", "legendary"]
    rarity_icons = {
        "common": "⚪",
        "rare": "🔵", 
        "epic": "🟣",
        "legendary": "🟡"
    }
    
    for rarity in rarity_order:
        if rarity in rewards_by_rarity:
            text += f"{rarity_icons[rarity]} **{rarity.title()}**\n"
            
            for reward in rewards_by_rarity[rarity][:3]:  # Mostrar máximo 3 por rareza
                requirements = []
                if reward.level_required > 0:
                    requirements.append(f"Nivel {reward.level_required}")
                if reward.vip_only:
                    requirements.append("Solo VIP")
                
                req_text = f" ({', '.join(requirements)})" if requirements else ""
                text += f"• {reward.icon} {reward.name}{req_text}\n"
            
            if len(rewards_by_rarity[rarity]) > 3:
                text += f"  ... y {len(rewards_by_rarity[rarity]) - 3} más\n"
            
            text += "\n"
    
    text += (
        "💡 **Consejos:**\n"
        "• Mantén tu racha para mejores recompensas\n"
        "• Los usuarios VIP tienen recompensas exclusivas\n"
        "• A mayor nivel, mejores probabilidades\n"
        "• Las rachas largas dan bonificaciones especiales"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Mis Estadísticas", callback_data="daily:stats")],
        [InlineKeyboardButton(text="🏆 Ver Ranking", callback_data="daily:leaderboard")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="daily:main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@daily_rewards_router.callback_query(F.data == "daily:main")
async def daily_main_callback(callback: CallbackQuery, daily_rewards_service: DailyRewardsService):
    """Vuelve al menú principal de regalos diarios."""
    user_id = callback.from_user.id
    
    # Obtener estadísticas del usuario
    stats = await daily_rewards_service.get_user_daily_stats(user_id)
    
    if stats["can_claim_today"]:
        # Puede reclamar el regalo
        reward = await daily_rewards_service.get_available_reward(user_id)
        
        if reward:
            # Iconos por rareza
            rarity_icons = {
                "common": "⚪",
                "rare": "🔵", 
                "epic": "🟣",
                "legendary": "🟡"
            }
            
            rarity_icon = rarity_icons.get(reward.rarity, "⚪")
            
            text = (
                "🎁 **Regalo Diario Disponible**\n\n"
                f"{reward.icon} **{reward.name}**\n"
                f"{rarity_icon} *{reward.rarity.title()}*\n\n"
                f"{reward.description}\n\n"
                f"🔥 **Racha consecutiva:** {stats['consecutive_days']} días\n\n"
                "¡Reclama tu regalo para mantener tu racha!"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎁 Reclamar Regalo", callback_data="daily:claim")],
                [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")],
                [InlineKeyboardButton(text="🏆 Ranking Rachas", callback_data="daily:leaderboard")]
            ])
        else:
            text = (
                "🎁 **Sistema de Regalos Diarios**\n\n"
                "No hay regalos disponibles en este momento.\n"
                "Intenta más tarde o contacta soporte."
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")]
            ])
    else:
        # Ya reclamó hoy
        next_claim = stats.get("next_claim_time")
        next_claim_str = ""
        if next_claim:
            hours_remaining = (next_claim - datetime.now()).total_seconds() / 3600
            if hours_remaining > 0:
                next_claim_str = f"⏰ Próximo regalo en: {hours_remaining:.1f} horas\n\n"
        
        text = (
            "🎁 **Regalo Diario**\n\n"
            "Ya has reclamado tu regalo diario de hoy.\n"
            "¡Vuelve mañana para continuar tu racha!\n\n"
            f"{next_claim_str}"
            f"🔥 **Racha actual:** {stats['consecutive_days']} días\n"
            f"📦 **Total reclamados:** {stats['total_claimed']}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")],
            [InlineKeyboardButton(text="🏆 Ranking Rachas", callback_data="daily:leaderboard")],
            [InlineKeyboardButton(text="🎁 Ver Recompensas", callback_data="daily:rewards_info")]
        ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

def register_daily_rewards_handlers(dp, daily_rewards_service: DailyRewardsService):
    """Registra los handlers de regalos diarios."""
    daily_rewards_router.message.register(
        lambda message: cmd_daily_reward(message, daily_rewards_service),
        Command("regalo")
    )
    
    dp.include_router(daily_rewards_router)