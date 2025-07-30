# Arquitectura del Sistema V2

Este documento define la arquitectura, convenciones y patrones de diseño para el bot V2.

## 1. Principios Fundamentales

- **Arquitectura Limpia (Clean Architecture):** Las dependencias fluyen hacia el interior. La lógica de negocio no conoce los detalles de la base de datos o el framework de Telegram.
- **Bus de Eventos (Event Bus):** Los módulos se comunican de forma asíncrona a través de un bus de eventos central. Esto elimina el acoplamiento directo.
- **Inyección de Dependencias (Dependency Injection):** Las dependencias (como servicios o repositorios) se inyectan en los constructores, no se importan directamente.

## 2. Estructura de Directorios

```
V2/
├── pyproject.toml      # Dependencias y configuración del proyecto
├── README.md
└── src/
    ├── core/             # Núcleo de la aplicación
    │   ├── __init__.py
    │   ├── event_bus.py    # Implementación del Event Bus
    │   ├── interfaces/     # Contratos (Abstract Base Classes)
    │   └── services/       # Servicios base (configuración, logging)
    ├── modules/          # Módulos de negocio (dominios)
    │   ├── __init__.py
    │   ├── gamification/
    │   ├── narrative/
    │   └── admin/
    ├── infrastructure/   # Implementaciones concretas (DB, Telegram API)
    │   ├── __init__.py
    │   ├── database/
    │   └── telegram/
    └── main.py           # Punto de entrada de la aplicación
└── tests/
    ├── __init__.py
    ├── integration/
    └── unit/
```

## 3. Convenciones de Nomenclatura (Naming Conventions)

- **Archivos y Módulos:** `snake_case.py` (ej: `event_bus.py`).
- **Clases y Tipos:** `PascalCase` (ej: `GamificationService`).
- **Interfaces (ABCs):** Prefijo `I` seguido de `PascalCase` (ej: `IEventBus`).
- **Funciones y Métodos:** `snake_case()` (ej: `register_event()`).
- **Variables y Constantes:** `snake_case` para variables, `UPPER_SNAKE_CASE` para constantes.
