-- quick_fix_story_fragments.sql
-- Fix inmediato para eliminar el error de foreign key

-- 1. Crear fragmento por defecto si no existe
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

-- 2. Crear fragmentos básicos del sistema Diana
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

-- 3. Verificar que se crearon correctamente
SELECT key, title, fragment_type 
FROM story_fragments 
WHERE key IN ('default_welcome', 'diana_welcome_level_1', 'lucien_challenge_1')
ORDER BY key;

-- 4. Opcional: Actualizar usuarios existentes con fragmento por defecto
UPDATE user_narrative_states 
SET current_fragment_key = 'default_welcome'
WHERE current_fragment_key IS NULL 
   OR current_fragment_key NOT IN (SELECT key FROM story_fragments);

-- 5. Crear trigger para auto-crear usuarios si no existen (bonus)
CREATE OR REPLACE FUNCTION ensure_user_exists()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO users (id, created_at, updated_at)
    VALUES (NEW.user_id, NOW(), NOW())
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a user_narrative_states
DROP TRIGGER IF EXISTS ensure_user_exists_trigger ON user_narrative_states;
CREATE TRIGGER ensure_user_exists_trigger
    BEFORE INSERT ON user_narrative_states
    FOR EACH ROW
    EXECUTE FUNCTION ensure_user_exists();
