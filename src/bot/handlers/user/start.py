from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.core.interfaces.IEventBus import IEventBus
from src.modules.events import UserStartedBotEvent
from src.modules.admin.service import AdminService
from src.bot.keyboards.keyboard_factory import KeyboardFactory

async def handle_start(
    message: types.Message, 
    command: types.BotCommand,
    event_bus: IEventBus,
    admin_service: AdminService
):
    """
    Maneja el comando /start del bot.
    
    Si se proporciona un token, valida el token para suscripciones VIP.
    De lo contrario, envía mensaje de bienvenida y publica un evento UserStartedBotEvent.
    """
    token = command.args
    user_id = message.from_user.id

    if token:
        validated_token = admin_service.validate_token(token, user_id)
        if validated_token:
            tariff = admin_service.get_tariff(validated_token['tariff_id'])
            await message.answer(
                f"¡Felicidades! Has canjeado un token para la tarifa '{tariff['name']}'.\n"
                f"Disfruta de tu acceso VIP por {tariff['duration_days']} días."
            )
        else:
            await message.answer("El token que has usado no es válido o ya ha sido canjeado.")
    else:
        # Publicar evento de inicio de usuario
        event = UserStartedBotEvent(user_id=user_id, username=message.from_user.username)
        await event_bus.publish(event)
        
        # Enviar mensaje de bienvenida con teclado principal
        await message.answer(
            "¡Bienvenido a Diana V2! ¿Qué te gustaría hacer hoy?",
            reply_markup=KeyboardFactory.main_menu()
        )

def register_start_handler(dp, event_bus, admin_service):
    """Registra el handler del comando /start en el dispatcher."""
    dp.message.register(
        lambda message, command: handle_start(
            message, command, event_bus, admin_service
        ),
        CommandStart()
    )