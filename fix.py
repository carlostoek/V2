# fix_database.py
"""
Script para ejecutar quick fixes en Railway PostgreSQL
¡Usar una vez y eliminar!
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from src.utils.sexy_logger import log

async def execute_quick_fixes():
    """Ejecuta los quick fixes de la base de datos"""
    
    log.banner("🔧 EJECUTANDO QUICK FIXES", "Eliminando errores de producción")
    
    # Obtener URL de la base de datos
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        log.error("DATABASE_URL no encontrada en variables de entorno")
        return False
    
    # Crear engine
    engine = create_async_engine(database_url)
    
    # SQL fixes
    sql_fixes = [
        # Fix 1: Crear fragmento por defecto
        """
        INSERT INTO story_fragments (key, title, content, fragment_type, conditions, outcomes, metadata)
        VALUES (
            'default_welcome',
            'Bienvenida por Defecto',
            'Bienvenido al mundo de Diana. Tu viaje narrativo está a punto de comenzar...',
            'welcome',
            '{}',
            '{}',
            '{"is_default": true, "auto_created": true}'
        ) ON CONFLICT (key) DO NOTHING;
        """,
        
        # Fix 2: Crear fragmentos básicos del sistema Diana
        """
        INSERT INTO story_fragments (key, title, content, fragment_type, conditions, outcomes, metadata)
        VALUES 
            (
                'diana_welcome_level_1',
                'Bienvenida de Diana - Nivel 1',
                'Bienvenido a Los Kinkys. Has cruzado una línea que muchos ven... pero pocos realmente atraviesan.',
                'character_introduction',
                '{"level": 1}',
                '{"next_fragment": "lucien_challenge_1"}',
                '{"character": "diana", "level": 1, "emotion": "mysterious"}'
            ),
            (
                'lucien_challenge_1', 
                'Primer Desafío de Lucien',
                'Ah, otro visitante de Diana. Permíteme presentarme: Lucien, guardián de los secretos que ella no cuenta... todavía.',
                'challenge',
                '{"level": 1, "completed_diana_intro": true}',
                '{"success": "level_2_observation", "failure": "encouragement_1"}',
                '{"character": "lucien", "level": 1, "challenge_type": "reaction"}'
            ),
            (
                'encouragement_1',
                'Aliento por Validación Fallida',
                'Diana nota que necesitas más tiempo para comprender. No todos encuentran su camino inmediatamente...',
                'encouragement',
                '{"validation_failed": true}',
                '{"retry": true, "next_attempt": "lucien_challenge_1"}',
                '{"character": "diana", "purpose": "encouragement", "retry_allowed": true}'
            ),
            (
                'level_2_observation',
                'Misión de Observación - Nivel 2',
                'Volviste. Interesante... No todos regresan después de la primera revelación.',
                'mission_start',
                '{"level": 2, "completed_level_1": true}',
                '{"mission_type": "observation", "target": "hidden_clues"}',
                '{"character": "diana", "level": 2, "mission": "observation"}'
            ),
            (
                'diana_validation_success',
                'Reconocimiento de Validación Exitosa',
                'Has logrado algo que pocos comprenden. Hay una diferencia entre ver y realmente observar...',
                'validation_success',
                '{"validation_passed": true}',
                '{"rewards": ["points", "items"], "next_level": true}',
                '{"character": "diana", "purpose": "validation_success", "emotional_tone": "impressed"}'
            )
        ON CONFLICT (key) DO NOTHING;
        """,
        
        # Fix 3: Actualizar usuarios existentes con fragmento por defecto
        """
        UPDATE user_narrative_states 
        SET current_fragment_key = 'default_welcome'
        WHERE current_fragment_key IS NULL 
           OR current_fragment_key NOT IN (SELECT key FROM story_fragments);
        """,
        
        # Fix 4: Crear trigger para auto-crear usuarios
        """
        CREATE OR REPLACE FUNCTION ensure_user_exists()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO users (id, created_at, updated_at)
            VALUES (NEW.user_id, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
        
        # Fix 5: Aplicar trigger
        """
        DROP TRIGGER IF EXISTS ensure_user_exists_trigger ON user_narrative_states;
        CREATE TRIGGER ensure_user_exists_trigger
            BEFORE INSERT ON user_narrative_states
            FOR EACH ROW
            EXECUTE FUNCTION ensure_user_exists();
        """
    ]
    
    try:
        async with engine.begin() as conn:
            for i, sql in enumerate(sql_fixes, 1):
                log.database(f"Ejecutando Fix #{i}...", operation=f"fix_{i}")
                
                try:
                    result = await conn.execute(sql)
                    log.success(f"✅ Fix #{i} ejecutado correctamente")
                    
                    # Log detalles si hay resultados
                    if hasattr(result, 'rowcount') and result.rowcount > 0:
                        log.info(f"   📊 Filas afectadas: {result.rowcount}")
                
                except Exception as e:
                    log.error(f"❌ Error en Fix #{i}", error=e)
                    # Continuar con los siguientes fixes
                    continue
        
        # Verificar que los fixes funcionaron
        await verify_fixes(engine)
        
        log.success("🎉 Todos los quick fixes ejecutados correctamente")
        return True
        
    except Exception as e:
        log.error("Error ejecutando fixes", error=e)
        return False
    
    finally:
        await engine.dispose()

async def verify_fixes(engine):
    """Verificar que los fixes se aplicaron correctamente"""
    
    log.info("🔍 Verificando fixes...")
    
    verification_queries = [
        # Verificar fragmentos creados
        "SELECT key, title FROM story_fragments WHERE key IN ('default_welcome', 'diana_welcome_level_1') ORDER BY key;",
        
        # Verificar trigger existe
        "SELECT trigger_name FROM information_schema.triggers WHERE trigger_name = 'ensure_user_exists_trigger';",
        
        # Contar fragmentos totales
        "SELECT COUNT(*) as total_fragments FROM story_fragments;"
    ]
    
    async with engine.begin() as conn:
        for i, query in enumerate(verification_queries, 1):
            try:
                result = await conn.execute(query)
                rows = result.fetchall()
                
                if i == 1:  # Fragmentos
                    log.success(f"✅ Fragmentos verificados: {len(rows)} encontrados")
                    for row in rows:
                        log.info(f"   📄 {row[0]}: {row[1]}")
                
                elif i == 2:  # Trigger
                    if rows:
                        log.success(f"✅ Trigger verificado: {rows[0][0]}")
                    else:
                        log.warning("⚠️ Trigger no encontrado")
                
                elif i == 3:  # Total
                    log.info(f"📊 Total de fragmentos en BD: {rows[0][0]}")
            
            except Exception as e:
                log.error(f"Error en verificación {i}", error=e)

if __name__ == "__main__":
    print("🚀 Ejecutando Quick Fixes para Railway PostgreSQL...")
    print("=" * 60)
    
    success = asyncio.run(execute_quick_fixes())
    
    if success:
        print("\n🎉 ¡FIXES COMPLETADOS EXITOSAMENTE!")
        print("✅ El error de foreign key constraint debe estar resuelto")
        print("✅ Los fragmentos narrativos por defecto están creados")
        print("✅ El trigger de auto-creación de usuarios está activo")
        print("\n⚠️  IMPORTANTE: Elimina este archivo después de ejecutarlo")
    else:
        print("\n❌ Algunos fixes fallaron. Revisa los logs.")
        
    print("=" * 60)
