import asyncio
import pytest
from unittest.mock import Mock

from src.core.event_bus import EventBus
from src.core.interfaces.IEventBus import IEvent

# Clases de eventos de prueba
class TestEvent(IEvent):
    def __init__(self, value: int):
        self.value = value

class AnotherEvent(IEvent):
    pass

@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    """Verifica que un handler suscrito es llamado cuando se publica un evento."""
    # Arrange
    event_bus = EventBus()
    event = TestEvent(value=42)
    
    # Creamos un mock asíncrono para el handler
    handler_mock = Mock()
    future = asyncio.Future()
    future.set_result(None)
    handler_mock.return_value = future

    # Act
    event_bus.subscribe(TestEvent, handler_mock)
    await event_bus.publish(event)

    # Assert
    handler_mock.assert_called_once_with(event)

@pytest.mark.asyncio
async def test_event_bus_no_call_for_different_event():
    """Verifica que un handler no es llamado para un evento al que no está suscrito."""
    # Arrange
    event_bus = EventBus()
    event = AnotherEvent()
    handler_mock = Mock()

    # Act
    event_bus.subscribe(TestEvent, handler_mock)
    await event_bus.publish(event)

    # Assert
    handler_mock.assert_not_called()
