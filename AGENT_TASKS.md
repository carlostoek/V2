# Diana Bot V2 - Specialized Agent Task Assignments

## Introduction

This document provides specific task assignments for each specialized agent involved in the Phase 3 implementation of Diana Bot V2. Each agent has been assigned tasks based on their expertise, with clear deliverables and integration points.

## Agent Assignments

### 1. @bot-architecture-redesigner

**Focus Area**: Core Architecture Refactoring

**Detailed Tasks**:

1. **Dependency Injection Container Migration**
   - Create a new container architecture using `dependency-injector` library
   - Example implementation:
   ```python
   from dependency_injector import containers, providers
   
   class CoreContainer(containers.DeclarativeContainer):
       config = providers.Configuration()
       db = providers.Singleton(Database, connection_string=config.db.url)
       event_bus = providers.Singleton(EventBus)
       
       # Services
       user_service = providers.Factory(UserService, db=db, event_bus=event_bus)
       narrative_service = providers.Factory(NarrativeService, db=db, event_bus=event_bus)
       gamification_service = providers.Factory(GamificationService, db=db, event_bus=event_bus)
       admin_service = providers.Factory(AdminService, db=db, event_bus=event_bus)
   ```
   - Update bootstrap.py to utilize this container
   - Implement proper scoping for dependencies

2. **Bot Orchestrator Enhancement**
   - Expand the current orchestrator.py implementation to handle all interaction types
   - Implement Diana AI response generation logic
   - Example enhancement:
   ```python
   class BotOrchestrator:
       def __init__(self, container: Container):
           self._narrative_service = container.resolve(NarrativeService)
           self._gamification_service = container.resolve(GamificationService)
           self._user_service = container.resolve(UserService)
           self._admin_service = container.resolve(AdminService)
           self._diana_ai = container.resolve(DianaAIService)
           self._emotional_service = container.resolve(EmotionalService)
           
       async def handle_user_message(self, user_id: int, message_text: str):
           # Get user profile and analyze message
           user_profile = await self._user_service.get_or_create_user(user_id)
           emotional_context = await self._emotional_service.analyze_user_state(user_id)
           
           # Generate AI response based on context
           response = await self._diana_ai.generate_response(
               user_id, 
               message_text, 
               user_profile, 
               emotional_context
           )
           
           # Update systems
           await self._gamification_service.update_engagement(user_id)
           await self._narrative_service.record_interaction(user_id, message_text)
           
           return response
   ```

3. **Configuration Management Centralization**
   - Implement CentralConfig singleton
   - Example implementation:
   ```python
   class CentralConfig:
       _instance = None
       
       def __new__(cls):
           if cls._instance is None:
               cls._instance = super(CentralConfig, cls).__new__(cls)
               cls._instance._load_config()
           return cls._instance
           
       def _load_config(self):
           self._config = {}
           # Load from environment variables
           # Load from config files
           # Override with runtime values
           
       def get(self, key, default=None):
           return self._config.get(key, default)
           
       def set(self, key, value):
           self._config[key] = value
   ```
   - Update all services to use this central configuration

**Deliverables**:
- Complete DI container implementation (src/bot/core/containers.py)
- Enhanced Bot Orchestrator (src/bot/core/orchestrator.py)
- Central Configuration System (src/core/services/config.py)
- Unit tests for all components

**Integration Points**:
- Coordinate with all other agents to ensure proper service registration
- Work with @integration-specialist on event-driven architecture
- Support @telegram-admin-refactor with Orchestrator integration

### 2. @telegram-admin-refactor

**Focus Area**: Admin Module Implementation

**Detailed Tasks**:

1. **Admin Service Enhancement**
   - Complete the admin service implementation with subscription management
   - Example extensions:
   ```python
   class AdminService(ICoreService):
       async def create_subscription(self, user_id: int, tariff_id: int) -> Subscription:
           """Creates a subscription for a user based on a tariff."""
           tariff = await self.get_tariff(tariff_id)
           if not tariff:
               raise ValueError(f"Tariff with ID {tariff_id} not found")
               
           expiration_date = datetime.now() + timedelta(days=tariff.duration_days)
           subscription = Subscription(
               user_id=user_id,
               tariff_id=tariff_id,
               start_date=datetime.now(),
               end_date=expiration_date,
               is_active=True
           )
           
           async with self._session() as session:
               session.add(subscription)
               await session.commit()
               
           return subscription
       
       async def get_user_subscriptions(self, user_id: int) -> list[Subscription]:
           """Gets all subscriptions for a user."""
           async with self._session() as session:
               result = await session.execute(
                   select(Subscription).where(Subscription.user_id == user_id)
               )
               return result.scalars().all()
   ```

2. **Admin UI Development**
   - Complete the handlers/admin module
   - Implement keyboard layouts for admin functions
   - Example handler:
   ```python
   @router.callback_query(F.data.startswith("tariff_"))
   async def process_tariff_selection(query: CallbackQuery, state: FSMContext):
       """Handles tariff selection for viewing or editing."""
       tariff_id = int(query.data.split("_")[1])
       
       # Get the tariff details
       admin_service = query.bot.container.resolve(AdminService)
       tariff = await admin_service.get_tariff(tariff_id)
       
       if not tariff:
           await query.answer("Tariff not found")
           return
           
       # Store tariff ID in state
       await state.update_data(selected_tariff_id=tariff_id)
       
       # Show tariff details with edit options
       keyboard = create_tariff_management_keyboard(tariff_id)
       await query.message.edit_text(
           f"Tariff: {tariff.name}\n"
           f"Price: ${tariff.price:.2f}\n"
           f"Duration: {tariff.duration_days} days",
           reply_markup=keyboard
       )
   ```

3. **Token Management System**
   - Complete the token generation and validation system
   - Create handlers for token management
   - Implement redemption flow

4. **Analytics Dashboard**
   - Create statistics collection logic
   - Implement admin dashboard handlers and UI
   - Design data aggregation functions

**Deliverables**:
- Complete Admin Service (src/modules/admin/service.py)
- Admin UI Handlers (src/bot/handlers/admin/*)
- Admin Keyboards (src/bot/keyboards/admin/*)
- Token Management System (src/modules/admin/tokens.py)
- Analytics Components (src/modules/admin/analytics.py)
- Unit tests for all components

**Integration Points**:
- Coordinate with @bot-architecture-redesigner for Orchestrator integration
- Work with @integration-specialist on event publishing/subscribing
- Coordinate with @quality-assurance-specialist for testing

### 3. @integration-specialist

**Focus Area**: Event-Driven Integration and Testing

**Detailed Tasks**:

1. **Event Catalog Definition**
   - Document all events in the system
   - Ensure event structure consistency
   - Example catalog entry:
   ```python
   # src/modules/events.py
   
   class SubscriptionCreatedEvent(IEvent):
       """Event fired when a new subscription is created."""
       
       def __init__(self, user_id: int, subscription_id: int, tariff_id: int, end_date: datetime):
           self.user_id = user_id
           self.subscription_id = subscription_id
           self.tariff_id = tariff_id
           self.end_date = end_date
   ```

2. **Event Flow Documentation**
   - Create sequence diagrams for key flows
   - Document event dependencies
   - Example flow:
   ```markdown
   ## Subscription Creation Flow
   
   1. AdminService.create_subscription() is called
   2. Subscription record is created in database
   3. SubscriptionCreatedEvent is published
   4. UserService responds by updating user.is_vip status
   5. GamificationService responds by unlocking VIP missions
   6. NarrativeService responds by unlocking VIP story fragments
   ```

3. **Integration Tests Implementation**
   - Create comprehensive integration tests
   - Example integration test:
   ```python
   @pytest.mark.asyncio
   async def test_subscription_creation_updates_user_vip_status():
       # Arrange
       event_bus = EventBus()
       admin_service = AdminService(event_bus)
       user_service = UserService(event_bus)
       
       await admin_service.setup()
       await user_service.setup()
       
       user_id = 123
       await user_service.create_user(user_id, "testuser")
       
       # Act
       await admin_service.create_subscription(user_id, 1)  # Premium tariff
       
       # Assert
       user = await user_service.get_user(user_id)
       assert user.is_vip == True
   ```

4. **CI/CD Pipeline Setup**
   - Configure GitHub Actions for testing
   - Set up automated deployment

**Deliverables**:
- Complete Event Catalog (src/modules/events.py)
- Event Flow Documentation (docs/event_flows.md)
- Integration Tests (tests/integration/*)
- CI/CD Configuration (.github/workflows/*)

**Integration Points**:
- Coordinate with all service developers on event publishing/subscribing
- Work with @quality-assurance-specialist on test coverage
- Support @deployment-manager with CI/CD setup

### 4. @gamification-architect

**Focus Area**: Shop System and Trivia Implementation

**Detailed Tasks**:

1. **Shop System Implementation**
   - Design and implement shop data models
   - Create shop service
   - Example implementation:
   ```python
   class ShopService(ICoreService):
       def __init__(self, event_bus: IEventBus):
           self._event_bus = event_bus
           
       async def setup(self) -> None:
           """Initialize shop items and subscribe to events."""
           self._event_bus.subscribe(ItemPurchasedEvent, self.handle_item_purchased)
           
       async def get_shop_items(self, user_id: int) -> list[ShopItem]:
           """Gets available shop items for a user."""
           async with get_session() as session:
               # Get user level to filter items
               user_query = select(User).where(User.id == user_id)
               user_result = await session.execute(user_query)
               user = user_result.scalars().first()
               
               if not user:
                   return []
                   
               # Get items available for user's level
               query = select(ShopItem).where(
                   and_(
                       ShopItem.level_required <= user.level,
                       ShopItem.is_active == True
                   )
               )
               result = await session.execute(query)
               return result.scalars().all()
       
       async def purchase_item(self, user_id: int, item_id: int) -> bool:
           """Processes an item purchase."""
           async with get_session() as session:
               # Get item
               item_query = select(ShopItem).where(ShopItem.id == item_id)
               item_result = await session.execute(item_query)
               item = item_result.scalars().first()
               
               if not item:
                   return False
                   
               # Check if user has enough points
               points_query = select(UserPoints).where(UserPoints.user_id == user_id)
               points_result = await session.execute(points_query)
               user_points = points_result.scalars().first()
               
               if not user_points or user_points.current_points < item.price:
                   return False
                   
               # Deduct points
               user_points.current_points -= item.price
               user_points.total_spent += item.price
               
               # Create purchase record
               purchase = ItemPurchase(
                   user_id=user_id,
                   item_id=item_id,
                   price_paid=item.price,
                   purchased_at=datetime.now()
               )
               session.add(purchase)
               
               await session.commit()
               
               # Publish event
               event = ItemPurchasedEvent(
                   user_id=user_id,
                   item_id=item_id,
                   item_name=item.name,
                   price=item.price
               )
               await self._event_bus.publish(event)
               
               return True
   ```

2. **Trivia System Implementation**
   - Design trivia data models
   - Implement trivia service
   - Create trivia handlers and UI
   - Example trivia handler:
   ```python
   @router.message(Command("trivia"))
   async def start_trivia(message: Message, state: FSMContext):
       """Starts a trivia session."""
       trivia_service = message.bot.container.resolve(TriviaService)
       
       # Get random trivia question
       question = await trivia_service.get_random_question(message.from_user.id)
       
       if not question:
           await message.answer("No trivia questions available right now!")
           return
           
       # Save question ID to state
       await state.set_state(TriviaStates.answering)
       await state.update_data(question_id=question.id)
       
       # Create options keyboard
       options = question.options
       random.shuffle(options)
       
       keyboard = InlineKeyboardMarkup(
           inline_keyboard=[
               [InlineKeyboardButton(text=option, callback_data=f"trivia_{i}")]
               for i, option in enumerate(options)
           ]
       )
       
       await message.answer(
           f"🎮 Trivia Time!\n\n{question.text}",
           reply_markup=keyboard
       )
   ```

**Deliverables**:
- Shop System Models (src/bot/database/models/shop.py)
- Shop Service (src/modules/shop/service.py)
- Shop UI (src/bot/handlers/shop/*)
- Trivia System Models (src/bot/database/models/trivia.py)
- Trivia Service (src/modules/trivia/service.py)
- Trivia UI (src/bot/handlers/trivia/*)
- Unit tests for all components

**Integration Points**:
- Coordinate with @bot-architecture-redesigner for service registration
- Work with @integration-specialist on event publishing
- Coordinate with @quality-assurance-specialist for testing

### 5. @emotional-system-developer

**Focus Area**: Emotional System Refinement

**Detailed Tasks**:

1. **State Machine Implementation**
   - Implement emotional state transitions using Python Transitions
   - Example implementation:
   ```python
   from transitions import Machine
   
   class EmotionalStateManager:
       states = ['Neutral', 'Happy', 'Sad', 'Flirty', 'Mysterious', 'Angry']
       
       def __init__(self, user_id: int):
           self.user_id = user_id
           self.machine = Machine(
               model=self,
               states=EmotionalStateManager.states,
               initial='Neutral'
           )
           
           # Define transitions
           self.machine.add_transition(
               trigger='receive_compliment',
               source='*',  # Any state
               dest='Happy',
               conditions=['is_sincere_compliment']
           )
           
           self.machine.add_transition(
               trigger='receive_insult',
               source='*',
               dest='Angry',
               conditions=['is_direct_insult']
           )
           
           # More transitions...
           
       def is_sincere_compliment(self, message_text: str) -> bool:
           # Analysis logic to determine if message is a sincere compliment
           return True  # Simplified for example
           
       def is_direct_insult(self, message_text: str) -> bool:
           # Analysis logic to determine if message is a direct insult
           return False  # Simplified for example
   ```

2. **Emotional Middleware Enhancement**
   - Improve the emotional middleware to use the state machine
   - Implement emotional context tracking
   - Example middleware:
   ```python
   class EmotionalMiddleware(BaseMiddleware):
       async def __call__(
           self,
           handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
           event: Message,
           data: Dict[str, Any]
       ) -> Any:
           # Get emotional service
           emotional_service = event.bot.container.resolve(EmotionalService)
           
           # Process incoming message for emotional content
           if isinstance(event, Message) and event.text:
               # Analyze message emotional content
               emotion_data = await emotional_service.analyze_message(
                   event.from_user.id, 
                   event.text
               )
               
               # Update user's emotional state
               await emotional_service.update_emotional_state(
                   event.from_user.id,
                   emotion_data
               )
               
               # Add emotional context to handler data
               data["emotional_context"] = await emotional_service.get_emotional_context(
                   event.from_user.id
               )
           
           # Continue processing
           return await handler(event, data)
   ```

3. **Contextual Response Generation**
   - Implement response generation based on emotional state
   - Create templates for different emotional states
   - Example implementation:
   ```python
   class EmotionalResponseGenerator:
       def __init__(self):
           self.templates = {
               'Neutral': [
                   "I see. Tell me more about that.",
                   "Interesting. What else is on your mind?",
                   "Hmm, I understand."
               ],
               'Happy': [
                   "That's wonderful! I'm so happy to hear that!",
                   "Amazing! Tell me more about this!",
                   "That puts a smile on my face! 😊"
               ],
               # More state templates...
           }
           
       def generate_response(self, state: str, context: dict) -> str:
           """Generates a response based on emotional state and context."""
           templates = self.templates.get(state, self.templates['Neutral'])
           
           # Select template based on context
           # Apply template variables
           # Add emotional indicators
           
           return random.choice(templates)  # Simplified for example
   ```

**Deliverables**:
- Emotional State Manager (src/bot/services/emotional/state_manager.py)
- Enhanced Emotional Middleware (src/bot/middlewares/emotional.py)
- Contextual Response Generator (src/bot/services/emotional/response_generator.py)
- Unit tests for all components

**Integration Points**:
- Coordinate with @bot-architecture-redesigner for service registration
- Work with @integration-specialist on event publishing
- Support @telegram-admin-refactor with response generation

### 6. @quality-assurance-specialist

**Focus Area**: Testing Strategy and Implementation

**Detailed Tasks**:

1. **Unit Test Implementation**
   - Create comprehensive unit tests for all services
   - Implement test fixtures and mocks
   - Example unit test:
   ```python
   @pytest.mark.asyncio
   async def test_emotional_state_transition():
       # Arrange
       event_bus = EventBus()
       emotional_service = EmotionalService(event_bus)
       await emotional_service.setup()
       
       user_id = 123
       
       # Act
       initial_state = await emotional_service.get_emotional_state(user_id)
       await emotional_service.process_message(user_id, "You're so wonderful!")
       new_state = await emotional_service.get_emotional_state(user_id)
       
       # Assert
       assert initial_state != new_state
       assert new_state == "Happy"
   ```

2. **Integration Test Enhancement**
   - Create end-to-end tests for critical flows
   - Implement test data generators
   - Example integration test:
   ```python
   @pytest.mark.asyncio
   async def test_full_narrative_flow():
       # Arrange
       event_bus = EventBus()
       narrative_service = NarrativeService(event_bus)
       gamification_service = GamificationService(event_bus)
       
       await narrative_service.setup()
       await gamification_service.setup()
       
       user_id = 123
       
       # Act - Simulate user starting bot
       start_event = UserStartedBotEvent(user_id, "testuser")
       await event_bus.publish(start_event)
       
       # Get current fragment
       fragment = await narrative_service.get_user_fragment(user_id)
       
       # Make a choice
       choice_id = fragment["choices"][0]["id"]
       success = await narrative_service.make_narrative_choice(user_id, choice_id)
       
       # Assert
       assert success is True
       
       # Get updated fragment
       new_fragment = await narrative_service.get_user_fragment(user_id)
       assert new_fragment["key"] != fragment["key"]
       
       # Verify points were awarded
       points = await gamification_service.get_user_points(user_id)
       assert points["current_points"] > 0
   ```

3. **Coverage Reporting**
   - Set up test coverage tracking
   - Generate coverage reports
   - Identify areas needing more tests

4. **Performance Testing**
   - Implement load tests for critical endpoints
   - Measure response times and resource usage

**Deliverables**:
- Unit Tests (tests/unit/*)
- Integration Tests (tests/integration/*)
- Coverage Reports (tests/coverage/*)
- Performance Test Suite (tests/performance/*)
- Testing Documentation (docs/testing.md)

**Integration Points**:
- Coordinate with all developers to ensure testable code
- Work with @integration-specialist on CI/CD integration
- Support @deployment-manager with automated testing

### 7. @deployment-manager

**Focus Area**: Final Integration and Deployment

**Detailed Tasks**:

1. **End-to-End Testing**
   - Coordinate final integration testing
   - Validate all components work together
   - Fix integration issues

2. **Deployment Scripts**
   - Create deployment automation
   - Example deployment script:
   ```bash
   #!/bin/bash
   
   # Deploy Diana Bot V2
   
   echo "Starting deployment..."
   
   # Pull latest changes
   git pull origin main
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run database migrations
   alembic upgrade head
   
   # Run tests
   pytest
   
   # Restart service
   systemctl restart diana-bot
   
   echo "Deployment complete!"
   ```

3. **Documentation**
   - Create comprehensive documentation
   - Update README files
   - Generate API documentation

4. **Monitoring Setup**
   - Configure logging and monitoring
   - Set up alerts and dashboards

**Deliverables**:
- Deployment Scripts (scripts/deploy.sh)
- API Documentation (docs/api.md)
- User Manual (docs/manual.md)
- Monitoring Configuration (config/monitoring.yaml)

**Integration Points**:
- Coordinate with all developers for final integration
- Work with @quality-assurance-specialist on final testing
- Support project manager with deployment reporting

## Coordination and Communication

To ensure smooth coordination between agents:

1. **Daily Check-ins**: Each agent will report daily progress on assigned tasks
2. **Blocking Issues**: Agents should immediately report blocking issues to the project manager
3. **Integration Points**: Agents should coordinate directly on integration points
4. **Code Reviews**: All completed tasks should be reviewed by at least one other agent

## Next Steps

1. All agents should review this document and confirm their assignments
2. Begin implementation of highest priority tasks
3. Schedule first check-in for 24 hours from now

---

*This document will be continuously updated as the project progresses.*