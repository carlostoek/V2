from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

class AdminKeyboardFactory:
    """Factory unificada para teclados administrativos."""
    
    @staticmethod
    def main_menu(permissions: set[str]) -> types.InlineKeyboardMarkup:
        """Teclado principal dinámico basado en permisos."""
        builder = InlineKeyboardBuilder()
        
        # Core admin options
        builder.button(text="📊 Dashboard", callback_data="admin:dashboard")
        
        if "manage_tariffs" in permissions:
            builder.button(text="💎 Tarifas VIP", callback_data="admin:tariffs")
            
        if "manage_tokens" in permissions:
            builder.button(text="🔑 Tokens", callback_data="admin:tokens")
            
        if "manage_channels" in permissions:
            builder.button(text="📺 Canales", callback_data="admin:channels")
            
        if "view_stats" in permissions:
            builder.button(text="📈 Estadísticas", callback_data="admin:stats")
            
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def tariffs_menu() -> types.InlineKeyboardMarkup:
        """Teclado para gestión de tarifas VIP."""
        builder = InlineKeyboardBuilder()
        builder.button(text="🆕 Nueva tarifa", callback_data="admin:tariffs:new")
        builder.button(text="📋 Listar tarifas", callback_data="admin:tariffs:list")
        builder.button(text="🔙 Volver", callback_data="admin:main")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def confirmation_buttons(confirm_text: str = "Confirmar", cancel_text: str = "Cancelar") -> types.InlineKeyboardMarkup:
        """Teclado genérico de confirmación."""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"✅ {confirm_text}", callback_data="admin:confirm")
        builder.button(text=f"❌ {cancel_text}", callback_data="admin:cancel")
        return builder.as_markup()
