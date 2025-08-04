# Diana Bot V2 - Tools and Frameworks Integration Strategy

## Overview

This document outlines the strategy for integrating the recommended tools and frameworks into the Diana Bot V2 project. The integration approach is designed to be progressive, allowing for incremental adoption without disrupting existing functionality.

## Core Integration Principles

1. **Minimal Disruption**: Tools should be integrated with minimal impact on existing code
2. **Incremental Adoption**: Start with core components and expand gradually
3. **Standardized Interfaces**: Use consistent interfaces for all integrations
4. **Comprehensive Testing**: Each integration should be fully tested before deployment

## Recommended Tools and Integration Approach

### 1. Dependency Injection with `dependency-injector`

#### Current State
The project currently uses a simple custom DI container in `src/bot/core/di.py` with manual registration and resolution of dependencies.

#### Integration Strategy

1. **Phase 1: Library Setup and Core Container**
   - Add `dependency-injector` to project dependencies
   - Create base container structure in `src/bot/core/containers.py`
   - Example implementation:
   ```python
   from dependency_injector import containers, providers
   from src.core.event_bus import EventBus
   from src.bot.database.engine import get_session
   
   class CoreContainer(containers.DeclarativeContainer):
       config = providers.Configuration()
       
       # Configure from environment or config files
       config.from_dict({
           "bot": {
               "token": os.getenv("BOT_TOKEN")
           },
           "db": {
               "url": os.getenv("DATABASE_URL")
           }
       })
       
       # Core services
       event_bus = providers.Singleton(EventBus)
       db_session = providers.Resource(get_session)
   ```

2. **Phase 2: Service Registration**
   - Create service-specific containers for each module
   - Example implementation:
   ```python
   class NarrativeContainer(containers.DeclarativeContainer):
       config = providers.Configuration()
       event_bus = providers.Dependency(provided_type=EventBus)
       db_session = providers.Dependency()
       
       narrative_service = providers.Factory(
           NarrativeService,
           event_bus=event_bus
       )
       
   class GamificationContainer(containers.DeclarativeContainer):
       config = providers.Configuration()
       event_bus = providers.Dependency(provided_type=EventBus)
       db_session = providers.Dependency()
       
       gamification_service = providers.Factory(
           GamificationService,
           event_bus=event_bus
       )
   ```

3. **Phase 3: Application Container**
   - Create a main application container that wires everything together
   - Example implementation:
   ```python
   class ApplicationContainer(containers.DeclarativeContainer):
       config = providers.Configuration()
       
       core = providers.Container(
           CoreContainer,
           config=config
       )
       
       narrative = providers.Container(
           NarrativeContainer,
           config=config,
           event_bus=core.event_bus,
           db_session=core.db_session
       )
       
       gamification = providers.Container(
           GamificationContainer,
           config=config,
           event_bus=core.event_bus,
           db_session=core.db_session
       )
       
       # More containers...
   ```

4. **Phase 4: Bootstrap Integration**
   - Update the bootstrap process to use the new container
   - Example implementation:
   ```python
   async def setup_bot():
       # Initialize container
       container = ApplicationContainer()
       
       # Configure from env/files
       container.config.from_dict({
           "bot": {
               "token": os.getenv("BOT_TOKEN")
           },
           # More config...
       })
       
       # Create bot instance with container
       bot = Bot(token=container.config.bot.token(), parse_mode=ParseMode.HTML)
       dp = Dispatcher()
       
       # Wire container to bot
       bot.container = container
       
       # Register middlewares
       dp.middleware.setup(UserMiddleware(container.core.event_bus()))
       dp.middleware.setup(DatabaseMiddleware(container.core.db_session))
       dp.middleware.setup(EmotionalMiddleware())
       dp.middleware.setup(PointsMiddleware())
       
       # Register handlers
       dp.include_router(admin_router)
       dp.include_router(user_router)
       dp.include_router(narrative_router)
       dp.include_router(gamification_router)
       
       return bot, dp
   ```

5. **Phase 5: Handler Updates**
   - Update handlers to use the container for dependency resolution
   - Example implementation:
   ```python
   @router.message(Command("start"))
   async def start_handler(message: Message):
       # Get services from container
       user_service = message.bot.container.narrative.user_service()
       narrative_service = message.bot.container.narrative.narrative_service()
       
       # Process command
       user_id = message.from_user.id
       username = message.from_user.username or "user"
       
       # Create or get user
       user = await user_service.get_or_create_user(user_id, username)
       
       # Get welcome fragment
       fragment = await narrative_service.get_user_fragment(user_id)
       
       await message.answer(
           f"Welcome to Diana Bot, {username}!\n\n{fragment['text']}"
       )
   ```

#### Integration Timeline
- Phase 1: Week 1, Days 1-2
- Phase 2: Week 1, Days 3-4
- Phase 3: Week 1, Day 5
- Phase 4: Week 2, Days 1-2
- Phase 5: Week 2, Days 3-5

### 2. State Machine with `python-transitions`

#### Current State
The project currently uses simple state tracking in database models for managing user and narrative states.

#### Integration Strategy

1. **Phase 1: Library Setup and Base Models**
   - Add `transitions` to project dependencies
   - Create base state machine models in `src/bot/services/state_machines.py`
   - Example implementation:
   ```python
   from transitions import Machine
   
   class DianaEmotionalState:
       states = ['Vulnerable', 'Enigmática', 'Provocadora', 'Analítica', 'Silenciosa']
       
       def __init__(self, user_id: int, initial_state: str = 'Enigmática'):
           self.user_id = user_id
           self.machine = Machine(
               model=self, 
               states=DianaEmotionalState.states, 
               initial=initial_state
           )
           
           # Define transitions
           self.machine.add_transition(
               trigger='respuesta_emocional', 
               source='Enigmática', 
               dest='Vulnerable',
               conditions=['is_emotional_response']
           )
           
           self.machine.add_transition(
               trigger='pregunta_personal', 
               source='*', 
               dest='Analítica',
               conditions=['is_personal_question']
           )
           
           # More transitions...
           
       def is_emotional_response(self, message: str) -> bool:
           # Implement logic to detect emotional responses
           return 'siento' in message.lower() or 'emoción' in message.lower()
           
       def is_personal_question(self, message: str) -> bool:
           # Implement logic to detect personal questions
           return '?' in message and any(word in message.lower() for word in 
                                        ['tu', 'tus', 'sientes', 'piensas'])
   ```

2. **Phase 2: Emotional System Integration**
   - Integrate state machine with the emotional service
   - Example implementation:
   ```python
   class EmotionalService:
       def __init__(self, event_bus: EventBus):
           self._event_bus = event_bus
           self._state_machines = {}  # Cache of user state machines
           
       async def setup(self) -> None:
           # Subscribe to events
           self._event_bus.subscribe(UserMessageEvent, self.handle_user_message)
           
       async def handle_user_message(self, event: UserMessageEvent) -> None:
           user_id = event.user_id
           message = event.message
           
           # Get or create state machine for user
           state_machine = await self._get_state_machine(user_id)
           
           # Process triggers based on message content
           if state_machine.is_emotional_response(message):
               state_machine.respuesta_emocional(message)
               
           elif state_machine.is_personal_question(message):
               state_machine.pregunta_personal(message)
           
           # More triggers...
           
           # Save state changes
           await self._save_state(user_id, state_machine)
           
       async def _get_state_machine(self, user_id: int) -> DianaEmotionalState:
           # Check cache first
           if user_id in self._state_machines:
               return self._state_machines[user_id]
               
           # Load from database
           async with get_session() as session:
               query = select(EmotionalState).where(EmotionalState.user_id == user_id)
               result = await session.execute(query)
               db_state = result.scalars().first()
               
               if db_state:
                   # Create state machine with saved state
                   state_machine = DianaEmotionalState(user_id, db_state.current_state)
               else:
                   # Create new state machine with default state
                   state_machine = DianaEmotionalState(user_id)
                   
           # Cache for future use
           self._state_machines[user_id] = state_machine
           return state_machine
           
       async def _save_state(self, user_id: int, state_machine: DianaEmotionalState) -> None:
           # Save to database
           async with get_session() as session:
               query = select(EmotionalState).where(EmotionalState.user_id == user_id)
               result = await session.execute(query)
               db_state = result.scalars().first()
               
               if db_state:
                   # Update existing state
                   db_state.current_state = state_machine.state
                   db_state.last_transition = datetime.now()
               else:
                   # Create new state record
                   db_state = EmotionalState(
                       user_id=user_id,
                       current_state=state_machine.state,
                       last_transition=datetime.now()
                   )
                   session.add(db_state)
                   
               await session.commit()
   ```

3. **Phase 3: Narrative Flow Integration**
   - Create a state machine for narrative progression
   - Integrate with the narrative service

4. **Phase 4: UI State Integration**
   - Create state machines for complex UI flows
   - Integrate with handlers

#### Integration Timeline
- Phase 1: Week 1, Days 3-4
- Phase 2: Week 1, Days 5-7
- Phase 3: Week 2, Days 1-3
- Phase 4: Week 2, Days 4-7

### 3. Event-Driven Architecture with Enhanced Event Bus

#### Current State
The project already has a basic event bus implementation in `src/core/event_bus.py` with simple publish/subscribe functionality.

#### Integration Strategy

1. **Phase 1: Enhanced Event Bus**
   - Extend the current event bus with additional features
   - Example implementation:
   ```python
   class EnhancedEventBus(IEventBus):
       """Enhanced implementation of the event bus with additional features."""
       
       def __init__(self):
           self._subscribers = defaultdict(list)
           self._wildcard_subscribers = []  # Subscribers to all events
           self._event_history = {}  # Event history for replay
           self._max_history = 100  # Max events to keep in history
           
       def subscribe(self, event_type: Type[IEvent], handler: Callable) -> None:
           """Subscribe a handler to a specific event type."""
           self._subscribers[event_type].append(handler)
           
       def subscribe_all(self, handler: Callable) -> None:
           """Subscribe a handler to all event types."""
           self._wildcard_subscribers.append(handler)
           
       async def publish(self, event: IEvent) -> None:
           """Publish an event to all subscribers."""
           event_type = type(event)
           
           # Store in history
           timestamp = datetime.now()
           if event_type not in self._event_history:
               self._event_history[event_type] = deque(maxlen=self._max_history)
               
           self._event_history[event_type].append((timestamp, event))
           
           # Notify specific subscribers
           specific_tasks = [
               handler(event) for handler in self._subscribers.get(event_type, [])
           ]
           
           # Notify wildcard subscribers
           wildcard_tasks = [
               handler(event) for handler in self._wildcard_subscribers
           ]
           
           # Wait for all handlers to complete
           await asyncio.gather(*specific_tasks, *wildcard_tasks)
           
       async def replay_events(self, event_type: Type[IEvent], handler: Callable) -> None:
           """Replay historical events of a specific type to a handler."""
           if event_type not in self._event_history:
               return
               
           for _, event in self._event_history[event_type]:
               await handler(event)
   ```

2. **Phase 2: Event Catalog Expansion**
   - Define a comprehensive set of events for all system actions
   - Example implementation:
   ```python
   # src/modules/events.py
   
   class UserRegisteredEvent(IEvent):
       """Event fired when a new user registers."""
       def __init__(self, user_id: int, username: str, registration_time: datetime):
           self.user_id = user_id
           self.username = username
           self.registration_time = registration_time
           
   class UserLevelUpEvent(IEvent):
       """Event fired when a user levels up."""
       def __init__(self, user_id: int, old_level: int, new_level: int):
           self.user_id = user_id
           self.old_level = old_level
           self.new_level = new_level
           
   class ItemPurchasedEvent(IEvent):
       """Event fired when a user purchases an item."""
       def __init__(self, user_id: int, item_id: int, item_name: str, price: float):
           self.user_id = user_id
           self.item_id = item_id
           self.item_name = item_name
           self.price = price
   
   # Many more events...
   ```

3. **Phase 3: Service Integration**
   - Update all services to publish and subscribe to relevant events
   - Example service update:
   ```python
   class UserService(ICoreService):
       def __init__(self, event_bus: IEventBus):
           self._event_bus = event_bus
           
       async def setup(self) -> None:
           """Set up event subscriptions."""
           self._event_bus.subscribe(ItemPurchasedEvent, self.handle_item_purchased)
           self._event_bus.subscribe(NarrativeProgressionEvent, self.handle_narrative_progression)
           
       async def register_user(self, user_id: int, username: str) -> User:
           """Register a new user."""
           async with get_session() as session:
               # Create user in database
               user = User(id=user_id, username=username)
               session.add(user)
               await session.commit()
               
               # Publish event
               event = UserRegisteredEvent(
                   user_id=user_id,
                   username=username,
                   registration_time=datetime.now()
               )
               await self._event_bus.publish(event)
               
               return user
               
       async def handle_item_purchased(self, event: ItemPurchasedEvent) -> None:
           """Handle item purchase events."""
           # Update user inventory
           async with get_session() as session:
               # Add item to user inventory
               inventory_item = UserInventoryItem(
                   user_id=event.user_id,
                   item_id=event.item_id,
                   acquired_at=datetime.now()
               )
               session.add(inventory_item)
               await session.commit()
   ```

4. **Phase 4: Event Monitoring and Debugging**
   - Implement event monitoring and debugging tools
   - Create visualization of event flows
   - Add logging for all events

#### Integration Timeline
- Phase 1: Week 1, Days 1-3
- Phase 2: Week 1, Days 4-5
- Phase 3: Week 2, Days 1-4
- Phase 4: Week 2, Days 5-7

### 4. Text Analysis with TextBlob and spaCy

#### Current State
The project currently has no advanced text analysis capabilities.

#### Integration Strategy

1. **Phase 1: TextBlob Integration**
   - Add `textblob` to project dependencies
   - Create a basic sentiment analysis service
   - Example implementation:
   ```python
   from textblob import TextBlob
   
   class TextAnalysisService:
       def analyze_sentiment(self, text: str) -> dict:
           """Analyze the sentiment of a text string."""
           analysis = TextBlob(text)
           
           return {
               "polarity": analysis.sentiment.polarity,  # -1.0 to 1.0
               "subjectivity": analysis.sentiment.subjectivity,  # 0.0 to 1.0
               "is_positive": analysis.sentiment.polarity > 0.1,
               "is_negative": analysis.sentiment.polarity < -0.1,
               "is_neutral": -0.1 <= analysis.sentiment.polarity <= 0.1,
               "is_subjective": analysis.sentiment.subjectivity > 0.5
           }
   ```

2. **Phase 2: spaCy Integration**
   - Add `spacy` to project dependencies
   - Download Spanish language model
   - Create advanced text analysis service
   - Example implementation:
   ```python
   import spacy
   
   class AdvancedTextAnalysisService:
       def __init__(self):
           # Load Spanish language model
           self.nlp = spacy.load("es_core_news_sm")
           
       def analyze_message(self, text: str) -> dict:
           """Perform comprehensive analysis of a message."""
           doc = self.nlp(text)
           
           # Extract entities
           entities = [
               {"text": ent.text, "label": ent.label_} 
               for ent in doc.ents
           ]
           
           # Extract key noun phrases
           noun_phrases = [
               chunk.text 
               for chunk in doc.noun_chunks
           ]
           
           # Extract key verbs
           verbs = [
               {"text": token.text, "lemma": token.lemma_} 
               for token in doc 
               if token.pos_ == "VERB"
           ]
           
           # Extract questions
           is_question = any(token.text == "?" for token in doc) or \
                         any(token.text.lower() in ["qué", "quién", "cómo", "dónde", "cuándo", "por qué"] 
                             for token in doc)
           
           return {
               "entities": entities,
               "noun_phrases": noun_phrases,
               "verbs": verbs,
               "is_question": is_question,
               "tokens": [
                   {"text": token.text, "lemma": token.lemma_, "pos": token.pos_, "tag": token.tag_}
                   for token in doc
               ]
           }
   ```

3. **Phase 3: Emotional Response Integration**
   - Integrate text analysis with emotional service
   - Example integration:
   ```python
   class EmotionalService:
       def __init__(self, event_bus: IEventBus):
           self._event_bus = event_bus
           self._text_analysis = TextAnalysisService()
           self._advanced_analysis = AdvancedTextAnalysisService()
           
       async def analyze_message(self, user_id: int, message: str) -> dict:
           """Analyze a message for emotional content."""
           # Basic sentiment analysis
           sentiment = self._text_analysis.analyze_sentiment(message)
           
           # Advanced linguistic analysis
           linguistics = self._advanced_analysis.analyze_message(message)
           
           # Combine analyses
           analysis = {
               "sentiment": sentiment,
               "linguistics": linguistics,
               "triggers": self._detect_emotional_triggers(message, sentiment, linguistics)
           }
           
           return analysis
           
       def _detect_emotional_triggers(self, message: str, sentiment: dict, linguistics: dict) -> list:
           """Detect emotional triggers in a message."""
           triggers = []
           
           # Check for compliments
           if sentiment["is_positive"] and any(
               phrase in message.lower() 
               for phrase in ["eres increíble", "te quiero", "me gustas"]
           ):
               triggers.append("compliment")
               
           # Check for personal questions
           if linguistics["is_question"] and any(
               entity["text"].lower() in ["tu", "tus", "tuya", "tuyo"] 
               for entity in linguistics["entities"]
           ):
               triggers.append("personal_question")
               
           # Check for emotional vulnerability
           if sentiment["is_negative"] and sentiment["is_subjective"] and any(
               verb["lemma"] in ["sentir", "sufrir", "llorar", "extrañar"] 
               for verb in linguistics["verbs"]
           ):
               triggers.append("emotional_vulnerability")
               
           # More triggers...
           
           return triggers
   ```

4. **Phase 4: Response Generation Integration**
   - Use text analysis to generate contextually appropriate responses
   - Create templates based on analysis results

#### Integration Timeline
- Phase 1: Week 1, Days 2-3
- Phase 2: Week 1, Days 4-6
- Phase 3: Week 2, Days 1-3
- Phase 4: Week 2, Days 4-7

### 5. Monitoring with Prometheus and Grafana

#### Current State
The project currently has no monitoring infrastructure.

#### Integration Strategy

1. **Phase 1: Prometheus Client Setup**
   - Add `prometheus-client` to project dependencies
   - Set up basic metrics collection
   - Example implementation:
   ```python
   from prometheus_client import Counter, Histogram, Gauge, start_http_server
   import time
   
   # Define metrics
   REQUESTS_TOTAL = Counter(
       'bot_requests_total', 
       'Total number of requests received by the bot',
       ['command', 'user_type']
   )
   
   RESPONSE_TIME = Histogram(
       'bot_response_time_seconds', 
       'Response time in seconds',
       ['command', 'user_type']
   )
   
   ACTIVE_USERS = Gauge(
       'bot_active_users', 
       'Number of active users',
       ['user_type']
   )
   
   # Start metrics server
   def start_metrics_server(port=8000):
       start_http_server(port)
       print(f"Metrics server started on port {port}")
   
   # Example middleware for tracking metrics
   class MetricsMiddleware(BaseMiddleware):
       async def __call__(
           self,
           handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
           event: Message,
           data: Dict[str, Any]
       ) -> Any:
           # Get user type (vip or regular)
           user_id = event.from_user.id
           user_service = event.bot.container.resolve(UserService)
           user = await user_service.get_user(user_id)
           user_type = "vip" if user and user.is_vip else "regular"
           
           # Get command name
           command = "unknown"
           if isinstance(event, Message) and event.text:
               if event.text.startswith("/"):
                   command = event.text.split()[0][1:]
               else:
                   command = "text_message"
                   
           # Increment request counter
           REQUESTS_TOTAL.labels(command=command, user_type=user_type).inc()
           
           # Measure response time
           start_time = time.time()
           try:
               return await handler(event, data)
           finally:
               response_time = time.time() - start_time
               RESPONSE_TIME.labels(command=command, user_type=user_type).observe(response_time)
   ```

2. **Phase 2: Grafana Dashboard Setup**
   - Set up Grafana for visualization
   - Create basic dashboards for key metrics
   - Example dashboard configuration:
   ```json
   {
     "dashboard": {
       "id": null,
       "title": "Diana Bot Metrics",
       "tags": ["bot", "telegram"],
       "timezone": "browser",
       "panels": [
         {
           "title": "Active Users",
           "type": "graph",
           "datasource": "Prometheus",
           "targets": [
             {
               "expr": "bot_active_users",
               "legendFormat": "{{user_type}}",
               "refId": "A"
             }
           ]
         },
         {
           "title": "Requests Per Minute",
           "type": "graph",
           "datasource": "Prometheus",
           "targets": [
             {
               "expr": "rate(bot_requests_total[1m])",
               "legendFormat": "{{command}}",
               "refId": "A"
             }
           ]
         },
         {
           "title": "Response Time (95th Percentile)",
           "type": "graph",
           "datasource": "Prometheus",
           "targets": [
             {
               "expr": "histogram_quantile(0.95, sum(rate(bot_response_time_seconds_bucket[5m])) by (command, le))",
               "legendFormat": "{{command}}",
               "refId": "A"
             }
           ]
         }
       ]
     }
   }
   ```

3. **Phase 3: Custom Business Metrics**
   - Add metrics for business KPIs
   - Track user engagement, conversions, etc.
   - Example implementation:
   ```python
   # Define business metrics
   NARRATIVE_PROGRESS = Counter(
       'bot_narrative_progress_total', 
       'Number of narrative fragments viewed',
       ['fragment_id', 'user_type']
   )
   
   POINTS_AWARDED = Counter(
       'bot_points_awarded_total', 
       'Number of points awarded to users',
       ['source', 'user_type']
   )
   
   SUBSCRIPTIONS = Counter(
       'bot_subscriptions_total', 
       'Number of subscriptions purchased',
       ['tariff', 'is_renewal']
   )
   
   # Update NarrativeService to track progress
   class NarrativeService:
       async def make_narrative_choice(self, user_id: int, choice_id: int) -> bool:
           # Existing implementation...
           
           # Track narrative progress
           user = await self._user_service.get_user(user_id)
           user_type = "vip" if user and user.is_vip else "regular"
           
           NARRATIVE_PROGRESS.labels(
               fragment_id=choice.target_fragment_key, 
               user_type=user_type
           ).inc()
           
           # Continue with existing logic...
   ```

4. **Phase 4: Alerting and Reporting**
   - Set up alerting rules
   - Create automated reports
   - Example alerting configuration:
   ```yaml
   groups:
   - name: diana_bot_alerts
     rules:
     - alert: HighResponseTime
       expr: histogram_quantile(0.95, sum(rate(bot_response_time_seconds_bucket[5m])) by (command, le)) > 2
       for: 5m
       labels:
         severity: warning
       annotations:
         summary: "High response time for command {{ $labels.command }}"
         description: "95th percentile response time is above 2 seconds for command {{ $labels.command }}"
         
     - alert: ErrorRateHigh
       expr: rate(bot_errors_total[5m]) / rate(bot_requests_total[5m]) > 0.01
       for: 5m
       labels:
         severity: critical
       annotations:
         summary: "Error rate is high"
         description: "Error rate is above 1% in the last 5 minutes"
   ```

#### Integration Timeline
- Phase 1: Week 1, Days 3-5
- Phase 2: Week 2, Days 1-2
- Phase 3: Week 2, Days 3-5
- Phase 4: Week 3, Days 1-2

## Integration Priority Matrix

| Tool/Framework | Priority | Difficulty | Impact | Timeline |
|----------------|----------|------------|--------|----------|
| Dependency Injection | High | Medium | High | Week 1-2 |
| State Machine | Medium | Medium | Medium | Week 1-2 |
| Event Bus Enhancement | High | Low | High | Week 1-2 |
| Text Analysis | Medium | High | Medium | Week 1-2 |
| Monitoring | Low | Medium | Medium | Week 2-3 |

## Testing Strategy for Integrations

Each integration should follow these testing steps:

1. **Unit Testing**: Test individual components in isolation
2. **Integration Testing**: Test interaction between components
3. **Compatibility Testing**: Ensure backward compatibility with existing code
4. **Performance Testing**: Measure impact on performance
5. **Acceptance Testing**: Validate against requirements

## Integration Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing functionality | High | Medium | Comprehensive testing, gradual rollout |
| Performance degradation | Medium | Low | Performance testing, monitoring |
| Complex dependencies | Medium | Medium | Clear documentation, dependency graphs |
| Integration delays | Medium | Medium | Prioritization, parallel work streams |
| Knowledge gaps | Medium | High | Training, documentation, pair programming |

## Next Steps

1. Set up development environments with required dependencies
2. Create integration branches for each tool/framework
3. Begin with highest priority integrations: Dependency Injection and Event Bus
4. Implement comprehensive testing for each integration
5. Document all integrations thoroughly

---

*This strategy will be updated as implementation progresses and new requirements emerge.*