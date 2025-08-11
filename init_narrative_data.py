#!/usr/bin/env python3
"""
Script de inicialización de datos narrativos para Diana Bot V2.
Crear datos de prueba para el sistema narrativo.
"""

import asyncio
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.bot.database.engine import get_session
from src.bot.database.models.narrative import StoryFragment, NarrativeChoice, UserNarrativeState
from src.bot.database.models.user import User


async def create_sample_story_fragments():
    """Crear fragmentos de historia de muestra."""
    
    fragments_data = [
        {
            "key": "welcome_intro",
            "title": "El Encuentro Inicial",
            "character": "diana",
            "text": "Hola... me llamo Diana. Hay algo especial en ti que me intriga. ¿Estás listo para descubrir secretos que pocos conocen?",
            "level_required": 1,
            "is_vip_only": False,
            "reward_besitos": 10,
            "tags": ["welcome", "introduction"],
            "choices": [
                {
                    "text": "Sí, estoy listo para la aventura",
                    "target_fragment_key": "path_curious"
                },
                {
                    "text": "Cuéntame más sobre ti primero",
                    "target_fragment_key": "path_cautious"
                }
            ]
        },
        {
            "key": "path_curious",
            "title": "El Camino del Curioso",
            "character": "diana",
            "text": "Me gusta tu espíritu aventurero... Sígueme. Hay un lugar que solo comparto con aquellos que no temen explorar lo desconocido.",
            "level_required": 1,
            "is_vip_only": False,
            "reward_besitos": 15,
            "tags": ["adventure", "progression"],
            "choices": [
                {
                    "text": "Te sigo sin dudarlo",
                    "target_fragment_key": "secret_garden"
                },
                {
                    "text": "¿Es seguro ese lugar?",
                    "target_fragment_key": "safety_concern"
                }
            ]
        },
        {
            "key": "path_cautious",
            "title": "La Prudencia de la Sabiduría",
            "character": "diana",
            "text": "Mmm... la prudencia es una virtud. Soy Diana, guardiana de secretos antiguos. Mi mundo está lleno de misterios y pasión... ¿Te atreves a conocerlo?",
            "level_required": 1,
            "is_vip_only": False,
            "reward_besitos": 12,
            "tags": ["wisdom", "mystery"],
            "choices": [
                {
                    "text": "Tus secretos me intrigan",
                    "target_fragment_key": "mystery_path"
                },
                {
                    "text": "¿Qué clase de pasión?",
                    "target_fragment_key": "passion_path"
                }
            ]
        },
        {
            "key": "secret_garden",
            "title": "El Jardín Secreto",
            "character": "diana",
            "text": "Bienvenido a mi refugio privado. Aquí es donde vengo a reflexionar... y a conocer mejor a quienes me intrigan. Las flores aquí guardan secretos.",
            "level_required": 1,
            "is_vip_only": False,
            "reward_besitos": 20,
            "tags": ["location", "intimate", "secrets"],
            "choices": [
                {
                    "text": "¿Qué secretos guardan las flores?",
                    "target_fragment_key": "flower_secrets"
                },
                {
                    "text": "Este lugar es hermoso",
                    "target_fragment_key": "appreciation"
                }
            ]
        },
        {
            "key": "mystery_path",
            "title": "Los Misterios de Diana",
            "character": "diana",
            "text": "Los misterios... son mi especialidad. Verás, no soy una mujer ordinaria. Tengo conexiones con un mundo que pocos conocen... ¿Quieres ser parte de él?",
            "level_required": 2,
            "is_vip_only": False,
            "reward_besitos": 25,
            "tags": ["mystery", "progression", "exclusive"],
            "choices": [
                {
                    "text": "Quiero ser parte de tu mundo",
                    "target_fragment_key": "inner_circle_invite"
                },
                {
                    "text": "¿Qué tipo de conexiones?",
                    "target_fragment_key": "connections_reveal"
                }
            ]
        },
        {
            "key": "vip_exclusive_content",
            "title": "El Círculo Íntimo",
            "character": "diana",
            "text": "Solo mis miembros VIP tienen acceso a esta parte de mi historia... Aquí es donde las cosas se ponen realmente interesantes. ¿Estás preparado para este nivel de intimidad?",
            "level_required": 3,
            "is_vip_only": True,
            "reward_besitos": 50,
            "tags": ["vip", "exclusive", "intimate"],
            "choices": [
                {
                    "text": "Estoy más que preparado",
                    "target_fragment_key": "ultimate_secret"
                },
                {
                    "text": "Dime qué debo hacer",
                    "target_fragment_key": "vip_instructions"
                }
            ]
        }
    ]
    
    async for session in get_session():
        for fragment_data in fragments_data:
            # Verificar si ya existe
            existing_query = select(StoryFragment).where(StoryFragment.key == fragment_data["key"])
            existing = await session.execute(existing_query)
            if existing.scalars().first():
                print(f"Fragmento {fragment_data['key']} ya existe, saltando...")
                continue
                
            # Crear fragmento
            choices_data = fragment_data.pop("choices", [])
            fragment = StoryFragment(**fragment_data)
            
            session.add(fragment)
            await session.flush()  # Para obtener el key
            
            # Crear opciones
            for choice_data in choices_data:
                choice = NarrativeChoice(
                    fragment_key=fragment.key,
                    text=choice_data["text"],
                    target_fragment_key=choice_data["target_fragment_key"],
                    required_items=choice_data.get("required_items", {})
                )
                session.add(choice)
            
            print(f"Creado fragmento: {fragment_data['key']}")
        
        await session.commit()
        print("Fragmentos de historia creados exitosamente!")


async def create_sample_lore_pieces():
    """Crear algunas pistas narrativas de muestra para usuarios."""
    
    lore_pieces_data = {
        "historia_diana": {
            "title": "Historia de Diana",
            "description": "Una antigua leyenda habla de Diana, una mujer misteriosa con poder sobre los corazones",
            "source": "introduction"
        },
        "jardin_secreto": {
            "title": "El Jardín Secreto",
            "description": "Existe un jardín oculto donde Diana guarda sus secretos más profundos",
            "source": "exploration"
        },
        "circulo_intimo": {
            "title": "El Círculo Íntimo",
            "description": "Solo unos pocos elegidos forman parte del círculo íntimo de Diana",
            "source": "progression"
        }
    }
    
    async for session in get_session():
        # Obtener o crear un usuario de prueba
        test_user_query = select(User).where(User.id == 123456789)  # ID de prueba
        test_user_result = await session.execute(test_user_query)
        test_user = test_user_result.scalars().first()
        
        if not test_user:
            print("No hay usuario de prueba. Las pistas se crearán cuando un usuario interactúe.")
            return
        
        # Verificar si ya tiene estado narrativo
        state_query = select(UserNarrativeState).where(UserNarrativeState.user_id == test_user.id)
        state_result = await session.execute(state_query)
        state = state_result.scalars().first()
        
        if not state:
            # Crear estado narrativo inicial
            state = UserNarrativeState(
                user_id=test_user.id,
                current_fragment_key="welcome_intro",
                visited_fragments=["welcome_intro"],
                decisions_made={},
                narrative_items={"lore_pieces": {}},
                narrative_variables={}
            )
            session.add(state)
            await session.flush()
        
        # Agregar pistas de muestra
        narrative_items = state.narrative_items
        if "lore_pieces" not in narrative_items:
            narrative_items["lore_pieces"] = {}
            
        for piece_key, piece_data in lore_pieces_data.items():
            if piece_key not in narrative_items["lore_pieces"]:
                narrative_items["lore_pieces"][piece_key] = {
                    "title": piece_data["title"],
                    "description": piece_data["description"],
                    "unlocked_at": datetime.now().isoformat(),
                    "source": piece_data["source"]
                }
        
        state.narrative_items = narrative_items
        await session.commit()
        print(f"Pistas narrativas agregadas para usuario {test_user.id}")


async def main():
    """Función principal de inicialización."""
    print("Inicializando datos narrativos de Diana Bot V2...")
    
    try:
        await create_sample_story_fragments()
        await create_sample_lore_pieces()
        print("\n✅ Inicialización de datos narrativos completada!")
        print("\n📝 Comandos disponibles:")
        print("   /historia - Explorar la narrativa interactiva")
        print("   /mochila - Ver pistas narrativas recolectadas")
        print("\n💡 Tip: Interactúa con el bot para generar más contenido narrativo.")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())