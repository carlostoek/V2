"""
📊 DIANA ADMIN ANALYTICS SYSTEM
===============================

Silicon Valley-grade analytics and real-time dashboards.
Beautiful visualizations, insights, and performance metrics.

Author: The Most Epic Silicon Valley Developer
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import structlog
from collections import defaultdict, deque

logger = structlog.get_logger()

# === ANALYTICS MODELS ===

class MetricType(Enum):
    """Types of metrics we track"""
    COUNTER = "counter"          # Simple count (users, actions, etc.)
    GAUGE = "gauge"             # Current value (active sessions, etc.)
    HISTOGRAM = "histogram"     # Distribution of values
    RATE = "rate"              # Change over time
    PERCENTAGE = "percentage"   # Percentage values

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "tags": self.tags
        }

@dataclass 
class Metric:
    """A metric with its historical data"""
    name: str
    type: MetricType
    description: str
    unit: str
    points: List[MetricPoint] = field(default_factory=list)
    
    def add_point(self, value: float, tags: Dict[str, str] = None):
        """Add a new data point"""
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {}
        )
        self.points.append(point)
        
        # Keep only last 1000 points to prevent memory issues
        if len(self.points) > 1000:
            self.points = self.points[-1000:]
    
    def get_current_value(self) -> Optional[float]:
        """Get most recent value"""
        return self.points[-1].value if self.points else None
    
    def get_trend(self, minutes: int = 60) -> str:
        """Get trend direction over time period"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_points = [p for p in self.points if p.timestamp >= cutoff]
        
        if len(recent_points) < 2:
            return "stable"
        
        start_value = recent_points[0].value
        end_value = recent_points[-1].value
        
        if end_value > start_value * 1.1:
            return "rising"
        elif end_value < start_value * 0.9:
            return "falling"
        else:
            return "stable"
    
    def get_change_percentage(self, minutes: int = 60) -> float:
        """Get percentage change over time period"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_points = [p for p in self.points if p.timestamp >= cutoff]
        
        if len(recent_points) < 2:
            return 0.0
        
        start_value = recent_points[0].value
        end_value = recent_points[-1].value
        
        if start_value == 0:
            return 100.0 if end_value > 0 else 0.0
        
        return ((end_value - start_value) / start_value) * 100

# === ANALYTICS ENGINE ===

class AnalyticsEngine:
    """Advanced analytics engine with real-time capabilities"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.event_log: deque = deque(maxlen=10000)  # Keep last 10k events
        self.alerts: List[Dict[str, Any]] = []
        self.dashboards: Dict[str, Dict[str, Any]] = {}
        
        # Initialize core metrics
        self._initialize_core_metrics()
    
    def _initialize_core_metrics(self):
        """Initialize core system metrics"""
        core_metrics = [
            ("admin_sessions_active", MetricType.GAUGE, "Active admin sessions", "sessions"),
            ("admin_actions_total", MetricType.COUNTER, "Total admin actions", "actions"),
            ("admin_errors_total", MetricType.COUNTER, "Total admin errors", "errors"),
            ("response_time_avg", MetricType.GAUGE, "Average response time", "ms"),
            
            ("users_total", MetricType.GAUGE, "Total users", "users"),
            ("users_active_today", MetricType.GAUGE, "Active users today", "users"),
            ("users_vip_total", MetricType.GAUGE, "Total VIP users", "users"),
            
            ("gamification_points_distributed", MetricType.COUNTER, "Gamification points distributed", "points"),
            ("gamification_missions_completed", MetricType.COUNTER, "Missions completed", "missions"),
            ("gamification_achievements_earned", MetricType.COUNTER, "Achievements earned", "achievements"),
            
            ("revenue_today", MetricType.GAUGE, "Revenue today", "USD"),
            ("revenue_total", MetricType.COUNTER, "Total revenue", "USD"),
            ("subscriptions_active", MetricType.GAUGE, "Active subscriptions", "subs"),
            
            ("system_health_score", MetricType.GAUGE, "Overall system health", "score"),
            ("services_healthy", MetricType.GAUGE, "Healthy services count", "services"),
        ]
        
        for name, type_, desc, unit in core_metrics:
            self.metrics[name] = Metric(name, type_, desc, unit)
    
    def track_event(self, event_type: str, data: Dict[str, Any] = None):
        """Track an event for analytics"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data or {}
        }
        self.event_log.append(event)
        logger.debug("Event tracked", type=event_type, data=data)
    
    def increment_metric(self, name: str, value: float = 1, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        if name not in self.metrics:
            self.metrics[name] = Metric(name, MetricType.COUNTER, f"Auto-created metric: {name}", "count")
        
        current = self.metrics[name].get_current_value() or 0
        self.metrics[name].add_point(current + value, tags)
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric value"""
        if name not in self.metrics:
            self.metrics[name] = Metric(name, MetricType.GAUGE, f"Auto-created metric: {name}", "value")
        
        self.metrics[name].add_point(value, tags)
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value"""
        if name not in self.metrics:
            self.metrics[name] = Metric(name, MetricType.HISTOGRAM, f"Auto-created metric: {name}", "value")
        
        self.metrics[name].add_point(value, tags)
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a metric by name"""
        return self.metrics.get(name)
    
    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all metrics"""
        return self.metrics.copy()
    
    def get_dashboard_data(self, dashboard_name: str) -> Dict[str, Any]:
        """Get dashboard data"""
        if dashboard_name == "overview":
            return self._get_overview_dashboard()
        elif dashboard_name == "vip":
            return self._get_vip_dashboard()
        elif dashboard_name == "gamification":
            return self._get_gamification_dashboard()
        elif dashboard_name == "performance":
            return self._get_performance_dashboard()
        else:
            return {"error": f"Unknown dashboard: {dashboard_name}"}
    
    def _get_overview_dashboard(self) -> Dict[str, Any]:
        """Get overview dashboard data"""
        return {
            "title": "System Overview",
            "widgets": [
                {
                    "type": "metric_card",
                    "title": "Active Users",
                    "value": self.metrics["users_active_today"].get_current_value() or 0,
                    "trend": self.metrics["users_active_today"].get_trend(),
                    "change": f"{self.metrics['users_active_today'].get_change_percentage():.1f}%"
                },
                {
                    "type": "metric_card", 
                    "title": "Admin Sessions",
                    "value": self.metrics["admin_sessions_active"].get_current_value() or 0,
                    "trend": self.metrics["admin_sessions_active"].get_trend(),
                    "change": f"{self.metrics['admin_sessions_active'].get_change_percentage():.1f}%"
                },
                {
                    "type": "metric_card",
                    "title": "System Health",
                    "value": f"{self.metrics['system_health_score'].get_current_value() or 100:.1f}%",
                    "trend": self.metrics["system_health_score"].get_trend(),
                    "change": f"{self.metrics['system_health_score'].get_change_percentage():.1f}%"
                },
                {
                    "type": "metric_card",
                    "title": "Revenue Today",
                    "value": f"${self.metrics['revenue_today'].get_current_value() or 0:.2f}",
                    "trend": self.metrics["revenue_today"].get_trend(),
                    "change": f"{self.metrics['revenue_today'].get_change_percentage():.1f}%"
                }
            ]
        }
    
    def _get_vip_dashboard(self) -> Dict[str, Any]:
        """Get VIP dashboard data"""
        return {
            "title": "VIP Management",
            "widgets": [
                {
                    "type": "metric_card",
                    "title": "VIP Users",
                    "value": self.metrics["users_vip_total"].get_current_value() or 0,
                    "trend": self.metrics["users_vip_total"].get_trend()
                },
                {
                    "type": "metric_card",
                    "title": "Active Subscriptions", 
                    "value": self.metrics["subscriptions_active"].get_current_value() or 0,
                    "trend": self.metrics["subscriptions_active"].get_trend()
                },
                {
                    "type": "metric_card",
                    "title": "Total Revenue",
                    "value": f"${self.metrics['revenue_total'].get_current_value() or 0:.2f}",
                    "trend": self.metrics["revenue_total"].get_trend()
                }
            ]
        }
    
    def _get_gamification_dashboard(self) -> Dict[str, Any]:
        """Get gamification dashboard data"""
        return {
            "title": "Gamification Analytics",
            "widgets": [
                {
                    "type": "metric_card",
                    "title": "Points Distributed",
                    "value": self.metrics["gamification_points_distributed"].get_current_value() or 0,
                    "trend": self.metrics["gamification_points_distributed"].get_trend()
                },
                {
                    "type": "metric_card",
                    "title": "Missions Completed",
                    "value": self.metrics["gamification_missions_completed"].get_current_value() or 0,
                    "trend": self.metrics["gamification_missions_completed"].get_trend()
                },
                {
                    "type": "metric_card",
                    "title": "Achievements Earned",
                    "value": self.metrics["gamification_achievements_earned"].get_current_value() or 0,
                    "trend": self.metrics["gamification_achievements_earned"].get_trend()
                }
            ]
        }
    
    def _get_performance_dashboard(self) -> Dict[str, Any]:
        """Get performance dashboard data"""
        return {
            "title": "Performance Metrics",
            "widgets": [
                {
                    "type": "metric_card",
                    "title": "Avg Response Time",
                    "value": f"{self.metrics['response_time_avg'].get_current_value() or 0:.1f}ms",
                    "trend": self.metrics["response_time_avg"].get_trend()
                },
                {
                    "type": "metric_card",
                    "title": "Total Actions",
                    "value": self.metrics["admin_actions_total"].get_current_value() or 0,
                    "trend": self.metrics["admin_actions_total"].get_trend()
                },
                {
                    "type": "metric_card",
                    "title": "Error Rate",
                    "value": f"{self._calculate_error_rate():.2f}%",
                    "trend": "stable"  # Would need more complex calculation
                }
            ]
        }
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        total_actions = self.metrics["admin_actions_total"].get_current_value() or 1
        total_errors = self.metrics["admin_errors_total"].get_current_value() or 0
        return (total_errors / total_actions) * 100
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        alerts = []
        
        # Check for high error rate
        error_rate = self._calculate_error_rate()
        if error_rate > 5:
            alerts.append({
                "level": "warning",
                "title": "High Error Rate",
                "message": f"Error rate is {error_rate:.1f}% (threshold: 5%)",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for low system health
        health_score = self.metrics["system_health_score"].get_current_value() or 100
        if health_score < 90:
            alerts.append({
                "level": "warning",
                "title": "System Health Low", 
                "message": f"System health is {health_score:.1f}% (threshold: 90%)",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def export_metrics(self, format: str = "json", time_range: int = 24) -> str:
        """Export metrics data"""
        cutoff = datetime.now() - timedelta(hours=time_range)
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "time_range_hours": time_range,
            "metrics": {}
        }
        
        for name, metric in self.metrics.items():
            recent_points = [
                p.to_dict() for p in metric.points 
                if p.timestamp >= cutoff
            ]
            
            export_data["metrics"][name] = {
                "name": metric.name,
                "type": metric.type.value,
                "description": metric.description,
                "unit": metric.unit,
                "points": recent_points
            }
        
        if format == "json":
            return json.dumps(export_data, indent=2)
        else:
            return str(export_data)

# === REAL-TIME UPDATES ===

class RealTimeUpdater:
    """Manages real-time dashboard updates"""
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        self.analytics = analytics_engine
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.update_interval = 5  # seconds
        self.running = False
    
    def subscribe(self, dashboard_name: str, callback: Callable):
        """Subscribe to dashboard updates"""
        self.subscribers[dashboard_name].append(callback)
    
    async def start_updates(self):
        """Start real-time updates"""
        self.running = True
        
        while self.running:
            try:
                # Update all subscribed dashboards
                for dashboard_name, callbacks in self.subscribers.items():
                    data = self.analytics.get_dashboard_data(dashboard_name)
                    
                    for callback in callbacks:
                        try:
                            await callback(data)
                        except Exception as e:
                            logger.error("Update callback failed", error=str(e))
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error("Real-time update failed", error=str(e))
                await asyncio.sleep(self.update_interval)
    
    def stop_updates(self):
        """Stop real-time updates"""
        self.running = False

# === CHART GENERATORS ===

class ChartGenerator:
    """Generate text-based charts for Telegram"""
    
    @staticmethod
    def create_trend_chart(metric: Metric, width: int = 20, height: int = 5) -> str:
        """Create a simple trend chart"""
        if not metric.points:
            return "No data available"
        
        # Get recent points
        recent_points = metric.points[-width:]
        values = [p.value for p in recent_points]
        
        if not values:
            return "No data available"
        
        min_val = min(values)
        max_val = max(values)
        
        if min_val == max_val:
            # Flat line
            return "▬" * width
        
        # Normalize values to chart height
        normalized = []
        for val in values:
            norm = int((val - min_val) / (max_val - min_val) * (height - 1))
            normalized.append(norm)
        
        # Create chart
        chart_lines = []
        for row in range(height - 1, -1, -1):
            line = ""
            for col in normalized:
                if col >= row:
                    line += "█"
                else:
                    line += " "
            chart_lines.append(line)
        
        return "\n".join(chart_lines)
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], width: int = 20) -> str:
        """Create a horizontal bar chart"""
        if not data:
            return "No data available"
        
        max_val = max(data.values())
        if max_val == 0:
            return "No data available"
        
        chart = []
        for label, value in data.items():
            bar_length = int((value / max_val) * width)
            bar = "█" * bar_length + "░" * (width - bar_length)
            chart.append(f"{label:<10} {bar} {value}")
        
        return "\n".join(chart)

# === GLOBAL ANALYTICS INSTANCE ===

# Global analytics engine
analytics_engine: Optional[AnalyticsEngine] = None
real_time_updater: Optional[RealTimeUpdater] = None

def get_analytics_engine() -> AnalyticsEngine:
    """Get the global analytics engine"""
    global analytics_engine, real_time_updater
    
    if analytics_engine is None:
        analytics_engine = AnalyticsEngine()
        real_time_updater = RealTimeUpdater(analytics_engine)
    
    return analytics_engine

def get_real_time_updater() -> RealTimeUpdater:
    """Get the real-time updater"""
    global real_time_updater
    
    if real_time_updater is None:
        get_analytics_engine()  # This will initialize both
    
    return real_time_updater

# === ANALYTICS DECORATORS ===

def track_admin_action(action_name: str):
    """Decorator to track admin actions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                result = await func(*args, **kwargs)
                
                # Track successful action
                analytics = get_analytics_engine()
                analytics.increment_metric("admin_actions_total")
                analytics.track_event("admin_action", {
                    "action": action_name,
                    "success": True
                })
                
                # Track response time
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                analytics.record_histogram("response_time_admin", duration_ms)
                
                return result
                
            except Exception as e:
                # Track error
                analytics = get_analytics_engine()
                analytics.increment_metric("admin_errors_total")
                analytics.track_event("admin_error", {
                    "action": action_name,
                    "error": str(e)
                })
                raise
        
        return wrapper
    return decorator