"""
Factory para la creación de teclados en el bot.

Este módulo implementa el patrón Factory para la creación de
diferentes tipos de teclados, facilitando su reutilización y
mantenimiento.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union, Callable

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

class KeyboardType(Enum):
    """Tipos de teclado disponibles en el sistema."""
    INLINE = "inline"
    REPLY = "reply"

class KeyboardFactory:
    """
    Factory para la creación de teclados.
    
    Esta clase facilita la creación de diferentes tipos de teclados
    siguiendo una estructura consistente.
    """
    
    @staticmethod
    def create_inline(
        buttons: List[List[Dict[str, str]]],
        width: Optional[int] = None,
        **kwargs
    ) -> types.InlineKeyboardMarkup:
        """
        Crea un teclado inline a partir de una matriz de botones.
        
        Args:
            buttons: Lista de filas de botones, donde cada botón es un diccionario
                    con 'text' y 'callback_data'.
            width: Número de botones por fila (si se utiliza la lista plana).
            **kwargs: Argumentos adicionales para el teclado.
            
        Returns:
            Un teclado inline configurado.
        """
        builder = InlineKeyboardBuilder()
        
        for row in buttons:
            for button_data in row:
                builder.button(
                    text=button_data['text'],
                    callback_data=button_data['callback_data']
                )
            # Agregar un ajuste manual de ancho después de cada fila
            if width:
                builder.adjust(width)
        
        return builder.as_markup(**kwargs)
    
    @staticmethod
    def create_reply(
        buttons: List[List[Dict[str, str]]],
        width: Optional[int] = None,
        resize_keyboard: bool = True,
        one_time_keyboard: bool = False,
        **kwargs
    ) -> types.ReplyKeyboardMarkup:
        """
        Crea un teclado de respuesta a partir de una matriz de botones.
        
        Args:
            buttons: Lista de filas de botones, donde cada botón es un diccionario
                    con 'text'.
            width: Número de botones por fila (si se utiliza la lista plana).
            resize_keyboard: Si el teclado debe ajustarse al tamaño de los botones.
            one_time_keyboard: Si el teclado debe ocultarse después de usarse.
            **kwargs: Argumentos adicionales para el teclado.
            
        Returns:
            Un teclado de respuesta configurado.
        """
        builder = ReplyKeyboardBuilder()
        
        for row in buttons:
            for button_data in row:
                builder.button(text=button_data['text'])
            # Agregar un ajuste manual de ancho después de cada fila
            if width:
                builder.adjust(width)
        
        return builder.as_markup(
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            **kwargs
        )
    
    @classmethod
    def create(
        cls,
        keyboard_type: KeyboardType,
        buttons: List[List[Dict[str, str]]],
        **kwargs
    ) -> Union[types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup]:
        """
        Crea un teclado del tipo especificado.
        
        Args:
            keyboard_type: Tipo de teclado a crear (INLINE o REPLY).
            buttons: Lista de filas de botones.
            **kwargs: Argumentos adicionales para el teclado.
            
        Returns:
            El teclado creado del tipo especificado.
            
        Raises:
            ValueError: Si el tipo de teclado no es válido.
        """
        if keyboard_type == KeyboardType.INLINE:
            return cls.create_inline(buttons, **kwargs)
        elif keyboard_type == KeyboardType.REPLY:
            return cls.create_reply(buttons, **kwargs)
        else:
            raise ValueError(f"Tipo de teclado no válido: {keyboard_type}")
    
    # Métodos para crear teclados específicos
    
    @classmethod
    def main_menu(cls) -> types.InlineKeyboardMarkup:
        """Crea el teclado del menú principal."""
        buttons = [
            [{"text": "📜 Historia", "callback_data": "main_menu:narrative"}],
            [
                {"text": "🏆 Perfil", "callback_data": "main_menu:profile"},
                {"text": "🎯 Misiones", "callback_data": "main_menu:missions"}
            ],
            [{"text": "🎮 Gamificación", "callback_data": "gamification:main"}],
            [
                {"text": "🎁 Regalo Diario", "callback_data": "gamification:daily_reward"}, 
                {"text": "🛍️ Tienda", "callback_data": "shop:main"}
            ],
            [{"text": "🎒 Mochila", "callback_data": "main_menu:inventory"}],
            [{"text": "❓ Ayuda", "callback_data": "main_menu:help"}]
        ]
        return cls.create_inline(buttons)
    
    @classmethod
    def admin_menu(cls) -> types.InlineKeyboardMarkup:
        """Crea el teclado del menú de administración."""
        buttons = [
            [{"text": "🆓 Administrar Canal Gratuito", "callback_data": "admin:free_channel_menu"}],
            [{"text": "💎 Administrar Canal VIP", "callback_data": "admin:vip_channel_menu"}]
        ]
        return cls.create_inline(buttons)
    
    @classmethod
    def free_channel_admin(cls, configured: bool) -> types.InlineKeyboardMarkup:
        """
        Crea el teclado para administrar el canal gratuito.
        
        Args:
            configured: Si el canal ya está configurado.
        """
        buttons = []
        
        if configured:
            buttons.extend([
                [{"text": "⏰ Configurar Tiempo de Espera", "callback_data": "admin:set_wait_time"}],
                [{"text": "📝 Enviar Contenido al Canal", "callback_data": "admin:send_to_free_channel"}]
            ])
        else:
            buttons.append([{"text": "⚙️ Configurar Canal", "callback_data": "admin:setup_free_channel"}])
        
        buttons.append([{"text": "⬅️ Volver", "callback_data": "admin:main_menu"}])
        
        return cls.create_inline(buttons)
    
    @classmethod
    def wait_time_selection(cls) -> types.InlineKeyboardMarkup:
        """Crea el teclado para seleccionar el tiempo de espera."""
        buttons = [
            [
                {"text": "Inmediato", "callback_data": "admin:set_wait_time_0"},
                {"text": "15 min", "callback_data": "admin:set_wait_time_15"},
                {"text": "1 hora", "callback_data": "admin:set_wait_time_60"}
            ],
            [
                {"text": "12 horas", "callback_data": "admin:set_wait_time_720"},
                {"text": "24 horas", "callback_data": "admin:set_wait_time_1440"}
            ],
            [{"text": "⬅️ Volver", "callback_data": "admin:free_channel_menu"}]
        ]
        return cls.create_inline(buttons)
    
    @classmethod
    def post_confirmation(cls) -> types.InlineKeyboardMarkup:
        """Crea el teclado para confirmar un post."""
        buttons = [
            [{"text": "✅ Enviar Post", "callback_data": "admin:confirm_post"}],
            [{"text": "❌ Cancelar", "callback_data": "admin:cancel_post"}]
        ]
        return cls.create_inline(buttons)
    
    @classmethod
    def vip_admin_menu(cls, tariffs: List[Dict[str, Any]]) -> types.InlineKeyboardMarkup:
        """
        Crea el teclado para administrar el canal VIP.
        
        Args:
            tariffs: Lista de tarifas disponibles.
        """
        buttons = []
        
        for tariff in tariffs:
            text = f"{tariff['name']} - ${tariff['price']} - {tariff['duration_days']} días"
            buttons.append([{"text": text, "callback_data": f"admin:view_tariff_{tariff['id']}"}])
        
        buttons.append([{"text": "➕ Crear Nueva Tarifa", "callback_data": "admin:create_tariff"}])
        buttons.append([{"text": "⬅️ Volver", "callback_data": "admin:main_menu"}])
        
        return cls.create_inline(buttons)
    
    @classmethod
    def tariff_view(cls, tariff_id: int) -> types.InlineKeyboardMarkup:
        """
        Crea el teclado para ver una tarifa.
        
        Args:
            tariff_id: ID de la tarifa a ver.
        """
        buttons = [
            [{"text": "🎟️ Generar Token", "callback_data": f"admin:generate_token_{tariff_id}"}],
            [{"text": "🗑️ Eliminar Tarifa", "callback_data": f"admin:delete_tariff_{tariff_id}"}],
            [{"text": "⬅️ Volver", "callback_data": "admin:vip_channel_menu"}]
        ]
        return cls.create_inline(buttons)
    
    @classmethod
    def narrative_menu(cls) -> types.InlineKeyboardMarkup:
        """Crea el teclado del menú de narrativa."""
        buttons = [
            [{"text": "📖 Continuar Historia", "callback_data": "narrative:continue"}],
            [{"text": "🔍 Explorar Ramas", "callback_data": "narrative:explore"}],
            [{"text": "📜 Ver Fragmentos Desbloqueados", "callback_data": "narrative:fragments"}],
            [{"text": "⬅️ Volver al Menú Principal", "callback_data": "narrative:back_to_main"}]
        ]
        return cls.create_inline(buttons)
    
    @classmethod
    def missions_menu(cls) -> types.InlineKeyboardMarkup:
        """Crea el teclado del menú de misiones."""
        buttons = [
            [{"text": "🎯 Misiones Activas", "callback_data": "missions:active"}],
            [{"text": "✅ Misiones Completadas", "callback_data": "missions:completed"}],
            [{"text": "🔍 Buscar Nuevas Misiones", "callback_data": "missions:find"}],
            [{"text": "⬅️ Volver al Menú Principal", "callback_data": "missions:back_to_main"}]
        ]
        return cls.create_inline(buttons)
    
    @classmethod
    def inventory_menu(cls) -> types.InlineKeyboardMarkup:
        """Crea el teclado del menú de inventario."""
        buttons = [
            [{"text": "🔮 Objetos", "callback_data": "inventory:items"}],
            [{"text": "🏅 Logros", "callback_data": "inventory:achievements"}],
            [{"text": "🎁 Recompensas", "callback_data": "inventory:rewards"}],
            [{"text": "⬅️ Volver al Menú Principal", "callback_data": "inventory:back_to_main"}]
        ]
        return cls.create_inline(buttons)
    
    @classmethod
    def help_menu(cls) -> types.InlineKeyboardMarkup:
        """Crea el teclado del menú de ayuda."""
        buttons = [
            [{"text": "🤔 Cómo Jugar", "callback_data": "help:how_to_play"}],
            [{"text": "📚 Comandos", "callback_data": "help:commands"}],
            [{"text": "❓ Preguntas Frecuentes", "callback_data": "help:faq"}],
            [{"text": "⬅️ Volver al Menú Principal", "callback_data": "help:back_to_main"}]
        ]
        return cls.create_inline(buttons)
    
    @classmethod
    def back_button(cls, callback_data: str) -> types.InlineKeyboardMarkup:
        """
        Crea un teclado con un solo botón para volver.
        
        Args:
            callback_data: Callback data para el botón de volver.
        """
        buttons = [[{"text": "⬅️ Volver", "callback_data": callback_data}]]
        return cls.create_inline(buttons)