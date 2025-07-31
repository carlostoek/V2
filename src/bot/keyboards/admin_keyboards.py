"""Teclados para la interfaz de administración del bot."""

from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class AdminKeyboardFactory:
    """Factory para crear teclados de administración."""
    
    @staticmethod
    def main_menu():
        """Crea el teclado principal de administración."""
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(
            types.KeyboardButton(text="🏷️ Gestionar Tarifas"),
            types.KeyboardButton(text="📊 Estadísticas"),
            types.KeyboardButton(text="⚙️ Configuración"),
            types.KeyboardButton(text="🔙 Volver")
        )
        keyboard.adjust(2)
        return keyboard.as_markup(resize_keyboard=True)
    
    @staticmethod
    def tariff_management():
        """Crea el teclado para gestión de tarifas."""
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(
            types.KeyboardButton(text="🆕 Nueva Tarifa"),
            types.KeyboardButton(text="🔗 Generar Enlace"),
            types.KeyboardButton(text="📊 Estadísticas"),
            types.KeyboardButton(text="🔙 Volver al Menú")
        )
        keyboard.adjust(2)
        return keyboard.as_markup(resize_keyboard=True)
    
    @staticmethod
    def default_options(options):
        """
        Crea un teclado con opciones predeterminadas.
        
        Args:
            options: Lista de textos para los botones.
            
        Returns:
            Teclado con las opciones proporcionadas.
        """
        keyboard = ReplyKeyboardBuilder()
        for option in options:
            keyboard.add(types.KeyboardButton(text=option))
        keyboard.adjust(1)
        return keyboard.as_markup(resize_keyboard=True)
    
    @staticmethod
    def channel_selector(channels):
        """
        Crea un teclado inline para seleccionar un canal.
        
        Args:
            channels: Lista de diccionarios con id y name de los canales.
            
        Returns:
            Teclado inline con los canales.
        """
        keyboard = InlineKeyboardBuilder()
        for channel in channels:
            keyboard.add(types.InlineKeyboardButton(
                text=channel["name"],
                callback_data=f"select_channel:{channel['id']}"
            ))
        keyboard.adjust(1)
        return keyboard.as_markup()
    
    @staticmethod
    def confirmation_buttons():
        """Crea un teclado inline con botones de confirmación."""
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            types.InlineKeyboardButton(text="✅ Confirmar", callback_data="confirm"),
            types.InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel")
        )
        return keyboard.as_markup()