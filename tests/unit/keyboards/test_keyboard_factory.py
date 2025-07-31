"""Tests para la factory de teclados."""

import pytest
from aiogram import types

from src.bot.keyboards.keyboard_factory import KeyboardFactory, KeyboardType

def test_create_inline_keyboard():
    """Verifica la creación de un teclado inline."""
    buttons = [
        [{"text": "Botón 1", "callback_data": "btn1"}],
        [{"text": "Botón 2", "callback_data": "btn2"}]
    ]
    
    keyboard = KeyboardFactory.create_inline(buttons)
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 2
    assert keyboard.inline_keyboard[0][0].text == "Botón 1"
    assert keyboard.inline_keyboard[0][0].callback_data == "btn1"
    assert keyboard.inline_keyboard[1][0].text == "Botón 2"
    assert keyboard.inline_keyboard[1][0].callback_data == "btn2"

def test_create_reply_keyboard():
    """Verifica la creación de un teclado de respuesta."""
    buttons = [
        [{"text": "Botón 1"}],
        [{"text": "Botón 2"}]
    ]
    
    keyboard = KeyboardFactory.create_reply(buttons)
    
    assert isinstance(keyboard, types.ReplyKeyboardMarkup)
    assert len(keyboard.keyboard) == 2
    assert keyboard.keyboard[0][0].text == "Botón 1"
    assert keyboard.keyboard[1][0].text == "Botón 2"

def test_create_keyboard_with_type():
    """Verifica la creación de un teclado usando el método create con tipo."""
    buttons = [
        [{"text": "Botón 1", "callback_data": "btn1"}]
    ]
    
    # Teclado inline
    inline_keyboard = KeyboardFactory.create(KeyboardType.INLINE, buttons)
    assert isinstance(inline_keyboard, types.InlineKeyboardMarkup)
    
    # Teclado de respuesta
    buttons = [
        [{"text": "Botón 1"}]
    ]
    reply_keyboard = KeyboardFactory.create(KeyboardType.REPLY, buttons)
    assert isinstance(reply_keyboard, types.ReplyKeyboardMarkup)
    
    # Tipo inválido
    with pytest.raises(ValueError):
        KeyboardFactory.create("invalid_type", buttons)

def test_main_menu_keyboard():
    """Verifica la creación del teclado de menú principal."""
    keyboard = KeyboardFactory.main_menu()
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 4  # 4 filas
    assert "Historia" in keyboard.inline_keyboard[0][0].text
    assert "Perfil" in keyboard.inline_keyboard[1][0].text
    assert "Misiones" in keyboard.inline_keyboard[1][1].text
    assert "Mochila" in keyboard.inline_keyboard[2][0].text
    assert "Ayuda" in keyboard.inline_keyboard[3][0].text

def test_admin_menu_keyboard():
    """Verifica la creación del teclado de administración."""
    keyboard = KeyboardFactory.admin_menu()
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 2  # 2 filas
    assert "Canal Gratuito" in keyboard.inline_keyboard[0][0].text
    assert "Canal VIP" in keyboard.inline_keyboard[1][0].text

def test_free_channel_admin_keyboard():
    """Verifica la creación del teclado de administración del canal gratuito."""
    # Canal no configurado
    keyboard = KeyboardFactory.free_channel_admin(configured=False)
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 2  # 2 filas
    assert "Configurar Canal" in keyboard.inline_keyboard[0][0].text
    assert "Volver" in keyboard.inline_keyboard[1][0].text
    
    # Canal configurado
    keyboard = KeyboardFactory.free_channel_admin(configured=True)
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 3  # 3 filas
    assert "Tiempo de Espera" in keyboard.inline_keyboard[0][0].text
    assert "Enviar Contenido" in keyboard.inline_keyboard[1][0].text
    assert "Volver" in keyboard.inline_keyboard[2][0].text

def test_wait_time_selection_keyboard():
    """Verifica la creación del teclado de selección de tiempo de espera."""
    keyboard = KeyboardFactory.wait_time_selection()
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 3  # 3 filas
    assert len(keyboard.inline_keyboard[0]) == 3  # 3 botones en la primera fila
    assert len(keyboard.inline_keyboard[1]) == 2  # 2 botones en la segunda fila
    assert "Inmediato" in keyboard.inline_keyboard[0][0].text
    assert "15 min" in keyboard.inline_keyboard[0][1].text
    assert "1 hora" in keyboard.inline_keyboard[0][2].text
    assert "12 horas" in keyboard.inline_keyboard[1][0].text
    assert "24 horas" in keyboard.inline_keyboard[1][1].text
    assert "Volver" in keyboard.inline_keyboard[2][0].text

def test_post_confirmation_keyboard():
    """Verifica la creación del teclado de confirmación de post."""
    keyboard = KeyboardFactory.post_confirmation()
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 2  # 2 filas
    assert "Enviar Post" in keyboard.inline_keyboard[0][0].text
    assert "Cancelar" in keyboard.inline_keyboard[1][0].text

def test_vip_admin_menu_keyboard():
    """Verifica la creación del teclado de administración del canal VIP."""
    tariffs = [
        {"id": 1, "name": "Premium", "price": 9.99, "duration_days": 30},
        {"id": 2, "name": "Gold", "price": 19.99, "duration_days": 90}
    ]
    
    keyboard = KeyboardFactory.vip_admin_menu(tariffs)
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 4  # 4 filas (2 tarifas + crear + volver)
    assert "Premium" in keyboard.inline_keyboard[0][0].text
    assert "Gold" in keyboard.inline_keyboard[1][0].text
    assert "Crear Nueva Tarifa" in keyboard.inline_keyboard[2][0].text
    assert "Volver" in keyboard.inline_keyboard[3][0].text

def test_tariff_view_keyboard():
    """Verifica la creación del teclado de vista de tarifa."""
    keyboard = KeyboardFactory.tariff_view(tariff_id=1)
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 3  # 3 filas
    assert "Generar Token" in keyboard.inline_keyboard[0][0].text
    assert "Eliminar Tarifa" in keyboard.inline_keyboard[1][0].text
    assert "Volver" in keyboard.inline_keyboard[2][0].text
    assert "admin:generate_token_1" in keyboard.inline_keyboard[0][0].callback_data

def test_narrative_menu_keyboard():
    """Verifica la creación del teclado del menú de narrativa."""
    keyboard = KeyboardFactory.narrative_menu()
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 4  # 4 filas
    assert "Continuar Historia" in keyboard.inline_keyboard[0][0].text
    assert "Explorar Ramas" in keyboard.inline_keyboard[1][0].text
    assert "Fragmentos Desbloqueados" in keyboard.inline_keyboard[2][0].text
    assert "Volver al Menú Principal" in keyboard.inline_keyboard[3][0].text

def test_missions_menu_keyboard():
    """Verifica la creación del teclado del menú de misiones."""
    keyboard = KeyboardFactory.missions_menu()
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 4  # 4 filas
    assert "Misiones Activas" in keyboard.inline_keyboard[0][0].text
    assert "Misiones Completadas" in keyboard.inline_keyboard[1][0].text
    assert "Buscar Nuevas Misiones" in keyboard.inline_keyboard[2][0].text
    assert "Volver al Menú Principal" in keyboard.inline_keyboard[3][0].text

def test_inventory_menu_keyboard():
    """Verifica la creación del teclado del menú de inventario."""
    keyboard = KeyboardFactory.inventory_menu()
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 4  # 4 filas
    assert "Objetos" in keyboard.inline_keyboard[0][0].text
    assert "Logros" in keyboard.inline_keyboard[1][0].text
    assert "Recompensas" in keyboard.inline_keyboard[2][0].text
    assert "Volver al Menú Principal" in keyboard.inline_keyboard[3][0].text

def test_help_menu_keyboard():
    """Verifica la creación del teclado del menú de ayuda."""
    keyboard = KeyboardFactory.help_menu()
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 4  # 4 filas
    assert "Cómo Jugar" in keyboard.inline_keyboard[0][0].text
    assert "Comandos" in keyboard.inline_keyboard[1][0].text
    assert "Preguntas Frecuentes" in keyboard.inline_keyboard[2][0].text
    assert "Volver al Menú Principal" in keyboard.inline_keyboard[3][0].text

def test_back_button_keyboard():
    """Verifica la creación del teclado con botón de volver."""
    keyboard = KeyboardFactory.back_button(callback_data="main:menu")
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 1  # 1 fila
    assert "Volver" in keyboard.inline_keyboard[0][0].text
    assert keyboard.inline_keyboard[0][0].callback_data == "main:menu"