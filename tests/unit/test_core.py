import os

def test_directory_structure():
    """Verifica que la estructura de directorios base exista."""
    base_path = './V2/src'
    assert os.path.isdir(os.path.join(base_path, 'core/interfaces'))
    assert os.path.isdir(os.path.join(base_path, 'modules/gamification'))
    assert os.path.isdir(os.path.join(base_path, 'infrastructure/database'))
