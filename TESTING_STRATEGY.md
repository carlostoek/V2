# Diana Bot V2 - Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the Diana Bot V2 project, with the goal of achieving >90% code coverage across all components. The strategy defines the testing approach, tools, methodologies, and responsibilities to ensure high-quality, reliable software.

## Testing Objectives

1. **Ensure Reliability**: Validate that all components work as expected
2. **Prevent Regressions**: Catch issues before they impact users
3. **Achieve >90% Coverage**: Comprehensive testing of all core functionality
4. **Enable Confident Refactoring**: Provide safety net for architectural changes
5. **Validate Integrations**: Ensure all components work together seamlessly

## Testing Types

### 1. Unit Testing

Unit tests verify individual components in isolation, focusing on:

- Service methods
- Handler functions
- Utility functions
- Model behaviors

**Coverage Target**: 95% for core services, 90% for handlers, 85% for utilities

**Example Unit Test**:

```python
import pytest
from unittest.mock import AsyncMock, patch

from src.modules.narrative.service import NarrativeService
from src.core.event_bus import EventBus
from src.modules.events import UserStartedBotEvent

@pytest.mark.asyncio
async def test_handle_user_started():
    # Arrange
    event_bus = EventBus()
    narrative_service = NarrativeService(event_bus)
    
    # Mock dependencies
    narrative_service._ensure_user_narrative_state = AsyncMock()
    narrative_service._starting_fragment_key = "welcome_fragment"
    
    # Act
    user_id = 123
    event = UserStartedBotEvent(user_id=user_id, username="test_user")
    await narrative_service.handle_user_started(event)
    
    # Assert
    assert user_id in narrative_service.story_fragments_to_send
    assert narrative_service.story_fragments_to_send[user_id] == "welcome_fragment"
    narrative_service._ensure_user_narrative_state.assert_called_once_with(
        user_id, "welcome_fragment"
    )
```

### 2. Integration Testing

Integration tests verify interactions between components, focusing on:

- Service collaborations
- Event handling chains
- Database interactions
- External API integrations

**Coverage Target**: 85% for service interactions, 80% for event chains

**Example Integration Test**:

```python
import pytest
from unittest.mock import AsyncMock

from src.core.event_bus import EventBus
from src.modules.narrative.service import NarrativeService
from src.modules.gamification.service import GamificationService
from src.modules.events import UserStartedBotEvent, PointsAwardedEvent

@pytest.mark.asyncio
async def test_user_started_awards_points_and_narrative():
    # Arrange
    event_bus = EventBus()
    
    # Create services with mocked database operations
    narrative_service = NarrativeService(event_bus)
    gamification_service = GamificationService(event_bus)
    
    # Mock internal methods
    narrative_service._ensure_user_narrative_state = AsyncMock()
    narrative_service._starting_fragment_key = "welcome_fragment"
    
    # Set up services
    await narrative_service.setup()
    await gamification_service.setup()
    
    # Spy on points awarded event
    points_awarded_spy = AsyncMock()
    event_bus.subscribe(PointsAwardedEvent, points_awarded_spy)
    
    # Act
    user_id = 123
    event = UserStartedBotEvent(user_id=user_id, username="test_user")
    await event_bus.publish(event)
    
    # Assert
    # Check narrative service response
    assert user_id in narrative_service.story_fragments_to_send
    assert narrative_service.story_fragments_to_send[user_id] == "welcome_fragment"
    
    # Check gamification service response
    assert gamification_service.get_points(user_id) == 10
    
    # Verify points awarded event was published
    points_awarded_spy.assert_called_once()
    args = points_awarded_spy.call_args[0][0]
    assert args.user_id == user_id
    assert args.points == 10
    assert args.source_event == "UserStartedBotEvent"
```

### 3. End-to-End Testing

E2E tests verify complete user flows, focusing on:

- User journeys
- UI interactions
- Multi-step processes
- Error handling

**Coverage Target**: 70% for critical user flows

**Example E2E Test**:

```python
import pytest
from unittest.mock import AsyncMock, patch

from aiogram.types import Message, User, Chat
from aiogram.filters import Command

from src.bot.core.bootstrap import setup_bot
from src.modules.narrative.service import NarrativeService

@pytest.mark.asyncio
async def test_start_command_flow():
    # Arrange
    bot, dp = await setup_bot()
    
    # Mock message creation
    user = User(id=123, is_bot=False, first_name="Test", username="test_user")
    chat = Chat(id=123, type="private")
    message = Message(
        message_id=1,
        date=1234567890,
        chat=chat,
        from_user=user,
        text="/start"
    )
    
    # Mock bot's answer method
    message.answer = AsyncMock()
    
    # Mock narrative service to return a specific fragment
    mock_fragment = {
        "key": "welcome_fragment",
        "title": "Welcome",
        "text": "Welcome to Diana's world",
        "choices": []
    }
    
    with patch.object(
        NarrativeService, 
        'get_user_fragment', 
        AsyncMock(return_value=mock_fragment)
    ):
        # Act
        # Find the appropriate handler
        for handler in dp.handlers.message:
            if isinstance(handler.filter, Command) and "start" in handler.filter.commands:
                await handler.callback(message, {})
                break
        
        # Assert
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Welcome to Diana's world" in call_args
```

### 4. Database Testing

Database tests verify data persistence and retrieval, focusing on:

- Model validations
- Query performance
- Transaction integrity
- Migration tests

**Coverage Target**: 90% for database models and queries

**Example Database Test**:

```python
import pytest
from sqlalchemy import select

from src.bot.database.models.user import User
from src.bot.database.models.narrative import UserNarrativeState

@pytest.mark.asyncio
async def test_user_narrative_state_relationship(db_session):
    # Arrange
    # Create test user
    user = User(id=123, username="test_user", is_vip=False, level=1)
    db_session.add(user)
    await db_session.commit()
    
    # Create narrative state for user
    narrative_state = UserNarrativeState(
        user_id=123,
        current_fragment_key="welcome_fragment",
        visited_fragments=["welcome_fragment"],
        decisions_made={},
        narrative_items={},
        narrative_variables={}
    )
    db_session.add(narrative_state)
    await db_session.commit()
    
    # Act
    # Query user with narrative state
    query = select(User).where(User.id == 123)
    result = await db_session.execute(query)
    user = result.scalars().first()
    
    # Query narrative state for user
    state_query = select(UserNarrativeState).where(UserNarrativeState.user_id == 123)
    state_result = await db_session.execute(state_query)
    state = state_result.scalars().first()
    
    # Assert
    assert user is not None
    assert state is not None
    assert state.user_id == user.id
    assert state.current_fragment_key == "welcome_fragment"
    assert "welcome_fragment" in state.visited_fragments
```

### 5. Snapshot Testing

Snapshot tests verify UI components and messages, focusing on:

- Message formats
- Keyboard layouts
- Response templates
- API responses

**Coverage Target**: 75% for UI components

**Example Snapshot Test**:

```python
import pytest
import json
from unittest.mock import AsyncMock

from src.bot.keyboards.keyboard_factory import create_narrative_keyboard
from src.bot.keyboards.admin.main_kb import create_admin_main_keyboard

def test_narrative_keyboard_format():
    # Arrange
    choices = [
        {"id": 1, "text": "Option 1", "target_fragment_key": "fragment_1"},
        {"id": 2, "text": "Option 2", "target_fragment_key": "fragment_2"}
    ]
    
    # Act
    keyboard = create_narrative_keyboard(choices)
    
    # Assert
    keyboard_dict = keyboard.model_dump()
    
    # Check structure
    assert "inline_keyboard" in keyboard_dict
    assert len(keyboard_dict["inline_keyboard"]) == 2
    
    # Check first button
    first_button = keyboard_dict["inline_keyboard"][0][0]
    assert first_button["text"] == "Option 1"
    assert first_button["callback_data"].startswith("narrative_choice_")
    
    # Save/compare snapshot
    with open("tests/snapshots/narrative_keyboard.json", "w") as f:
        json.dump(keyboard_dict, f, indent=2)
```

### 6. Performance Testing

Performance tests verify system responsiveness, focusing on:

- Response times
- Resource usage
- Concurrency handling
- Bottleneck identification

**Coverage Target**: Core service methods and critical paths

**Example Performance Test**:

```python
import pytest
import asyncio
import time
from unittest.mock import AsyncMock

from src.modules.gamification.service import GamificationService
from src.core.event_bus import EventBus
from src.modules.events import ReactionAddedEvent

@pytest.mark.asyncio
async def test_gamification_service_performance():
    # Arrange
    event_bus = EventBus()
    gamification_service = GamificationService(event_bus)
    await gamification_service.setup()
    
    # Act
    # Measure time to process 100 concurrent events
    start_time = time.time()
    
    user_ids = list(range(1, 101))
    events = [
        ReactionAddedEvent(
            user_id=user_id,
            message_id=1,
            points_to_award=5
        ) 
        for user_id in user_ids
    ]
    
    # Process events concurrently
    await asyncio.gather(*[event_bus.publish(event) for event in events])
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Assert
    # Check all users received points
    for user_id in user_ids:
        assert gamification_service.get_points(user_id) == 5
    
    # Verify performance within acceptable range
    assert execution_time < 1.0  # Should process 100 events in under 1 second
```

## Testing Tools and Infrastructure

### 1. Test Framework: pytest

- **Benefits**: Rich fixture system, async support, parameterization
- **Usage**: Primary test runner for all test types
- **Configuration**:
  ```python
  # pytest.ini
  [pytest]
  asyncio_mode = auto
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  markers =
      unit: Unit tests
      integration: Integration tests
      e2e: End-to-end tests
      db: Database tests
      performance: Performance tests
  ```

### 2. Mocking: unittest.mock and pytest-mock

- **Benefits**: Isolate components, control dependencies, simulate edge cases
- **Usage**: Mock external dependencies, services, database

### 3. Coverage: pytest-cov

- **Benefits**: Measure code coverage, identify untested areas
- **Usage**: Generate coverage reports for all test runs
- **Configuration**:
  ```ini
  [coverage:run]
  source = src
  omit = 
      */migrations/*
      */tests/*
      */__init__.py
      */config.py
  
  [coverage:report]
  exclude_lines =
      pragma: no cover
      def __repr__
      raise NotImplementedError
      pass
      raise ImportError
  ```

### 4. Database Testing: pytest-asyncio with in-memory SQLite

- **Benefits**: Fast, isolated database testing
- **Usage**: Test database models, queries, and transactions
- **Configuration**:
  ```python
  # conftest.py
  @pytest.fixture(scope="function")
  async def db_session():
      """Provides a clean, isolated database session for each test."""
      from src.bot.database.engine import engine, Base, async_session
  
      async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.create_all)
  
      async with async_session() as session:
          yield session
  
      async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.drop_all)
  ```

### 5. API Testing: pytest-aiohttp

- **Benefits**: Test HTTP endpoints and webhooks
- **Usage**: Test external API integrations

### 6. Performance Testing: locust

- **Benefits**: Simulate user load, measure performance
- **Usage**: Load testing critical paths

### 7. CI/CD Integration: GitHub Actions

- **Benefits**: Automated testing, deployment pipeline
- **Usage**: Run tests on every PR and push
- **Configuration**:
  ```yaml
  # .github/workflows/tests.yml
  name: Tests
  
  on:
    push:
      branches: [ main, develop ]
    pull_request:
      branches: [ main, develop ]
  
  jobs:
    test:
      runs-on: ubuntu-latest
      
      steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          
      - name: Run tests
        run: |
          pytest --cov=src tests/
          
      - name: Upload coverage report
        uses: codecov/codecov-action@v3
  ```

## Test Organization

Tests are organized by type and module, following this structure:

```
tests/
├── conftest.py                    # Common fixtures
├── unit/                          # Unit tests
│   ├── conftest.py                # Unit test fixtures
│   ├── services/                  # Service tests
│   │   ├── test_narrative_service.py
│   │   ├── test_gamification_service.py
│   │   └── ...
│   ├── handlers/                  # Handler tests
│   │   ├── test_user_handlers.py
│   │   ├── test_narrative_handlers.py
│   │   └── ...
│   └── ...
├── integration/                   # Integration tests
│   ├── conftest.py                # Integration test fixtures
│   ├── test_narrative_gamification.py
│   ├── test_user_narrative.py
│   └── ...
├── e2e/                           # End-to-end tests
│   ├── conftest.py                # E2E test fixtures
│   ├── test_user_flow.py
│   ├── test_admin_flow.py
│   └── ...
└── performance/                   # Performance tests
    ├── locustfile.py
    ├── test_service_performance.py
    └── ...
```

## Test Data Management

### 1. Fixtures

Test fixtures provide consistent test data across test cases:

```python
# conftest.py
@pytest.fixture
def sample_user():
    return {
        "id": 123,
        "username": "test_user",
        "is_vip": False,
        "level": 1
    }

@pytest.fixture
def sample_fragment():
    return {
        "key": "test_fragment",
        "title": "Test Fragment",
        "character": "Diana",
        "text": "This is a test fragment.",
        "level_required": 1,
        "is_vip_only": False,
        "choices": [
            {
                "id": 1,
                "text": "Option 1",
                "target_fragment_key": "fragment_1"
            },
            {
                "id": 2,
                "text": "Option 2",
                "target_fragment_key": "fragment_2"
            }
        ]
    }
```

### 2. Factory Pattern

Use factories to generate test data with variations:

```python
# tests/factories.py
class UserFactory:
    @staticmethod
    def create(id=123, username="test_user", is_vip=False, level=1):
        return User(
            id=id,
            username=username,
            is_vip=is_vip,
            level=level
        )

class FragmentFactory:
    @staticmethod
    def create(key="test_fragment", title="Test Fragment", **kwargs):
        defaults = {
            "character": "Diana",
            "text": "This is a test fragment.",
            "level_required": 1,
            "is_vip_only": False,
            "choices": []
        }
        
        # Override defaults with any provided kwargs
        for key, value in kwargs.items():
            defaults[key] = value
            
        return StoryFragment(**defaults)
```

### 3. Parameterized Tests

Use parameterization for comprehensive test coverage:

```python
@pytest.mark.parametrize("points,expected_level", [
    (0, 1),
    (50, 1),
    (99, 1),
    (100, 2),
    (399, 2),
    (400, 3),
    (899, 3),
    (900, 4),
    (10000, 11)
])
def test_calculate_level(points, expected_level):
    # Arrange
    gamification_service = GamificationService(EventBus())
    
    # Act
    level = gamification_service._calculate_level(points)
    
    # Assert
    assert level == expected_level
```

## Testing Workflow

### 1. Development Testing

Developers follow this testing workflow:

1. Write unit tests for new features
2. Run tests locally before committing
3. Fix failing tests before pushing
4. Add integration tests for service interactions

### 2. CI/CD Testing

The CI/CD pipeline follows this testing workflow:

1. Run unit tests for every push
2. Run integration tests for every PR
3. Run E2E tests before deployment
4. Generate and publish coverage reports

### 3. Code Coverage Tracking

Code coverage is tracked and enforced:

1. Generate coverage reports for all test runs
2. Block PRs with coverage below threshold
3. Identify and prioritize areas with low coverage
4. Set coverage targets by module

## Testing Roles and Responsibilities

### 1. Developers

- Write unit tests for all new code
- Ensure tests pass locally before pushing
- Maintain minimum coverage standards
- Review test coverage reports

### 2. Quality Assurance Specialist

- Write integration and E2E tests
- Design test scenarios for critical flows
- Review test coverage and identify gaps
- Create performance test suites

### 3. Project Manager

- Track testing progress and coverage
- Prioritize test improvements
- Ensure testing standards are followed
- Report on test results and issues

## Test-Driven Development Approach

For new features, follow this TDD approach:

1. **Write Test First**: Create failing tests that define the expected behavior
2. **Implement Minimum Code**: Write just enough code to make tests pass
3. **Refactor**: Improve code while keeping tests passing
4. **Expand Test Coverage**: Add edge cases and error conditions
5. **Integrate**: Add integration tests once unit tests pass

## Test Coverage Goals by Module

| Module | Unit Coverage | Integration Coverage | Total Coverage |
|--------|---------------|----------------------|----------------|
| Core | 95% | 85% | 90% |
| Narrative | 90% | 85% | 88% |
| Gamification | 90% | 85% | 88% |
| Admin | 90% | 80% | 85% |
| User | 90% | 85% | 88% |
| Handlers | 85% | 80% | 83% |
| Database | 90% | 90% | 90% |
| **Overall** | **90%** | **85%** | **>90%** |

## Implementation Plan

### Phase 1: Foundation (Week 1)

1. Set up testing infrastructure
2. Create common fixtures and utilities
3. Implement core service unit tests
4. Set up CI/CD pipeline with coverage reporting

### Phase 2: Expansion (Week 2)

1. Add unit tests for all services and handlers
2. Implement integration tests for critical flows
3. Create database test suite
4. Begin E2E testing for main user flows

### Phase 3: Completion (Week 3)

1. Add tests for edge cases and error handling
2. Implement performance test suite
3. Fill coverage gaps
4. Create automated test reports

## Monitoring and Reporting

Testing progress will be monitored and reported via:

1. **Daily Test Reports**: Coverage and failing tests
2. **Weekly Test Review**: Progress toward coverage goals
3. **Pull Request Checks**: Coverage impact of new code
4. **Test Dashboard**: Visual representation of test health

## Conclusion

This comprehensive testing strategy provides a roadmap to achieve >90% test coverage for the Diana Bot V2 project. By following this strategy, we will ensure high-quality, reliable software that meets all requirements and provides a solid foundation for future development.

---

*This document will be updated as the project evolves and new testing requirements emerge.*