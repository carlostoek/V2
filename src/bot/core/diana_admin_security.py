"""
🛡️ DIANA ADMIN SECURITY SYSTEM
===============================

Comprehensive security and permissions system for Diana Admin Master:
- Multi-level admin permissions
- Audit logging with detailed tracking
- Session management and timeout
- Action validation and rate limiting
- Security event monitoring

This module ensures admin operations are secure, logged, and properly authorized.
"""

import asyncio
import structlog
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

# === SECURITY CONFIGURATION ===

class AdminPermission(Enum):
    """Admin permission types"""
    # VIP Management
    VIP_READ = "vip:read"
    VIP_WRITE = "vip:write"
    VIP_DELETE = "vip:delete"
    VIP_CONFIG = "vip:config"
    
    # Channel Management  
    CHANNEL_READ = "channel:read"
    CHANNEL_WRITE = "channel:write"
    CHANNEL_DELETE = "channel:delete"
    CHANNEL_CONFIG = "channel:config"
    
    # Gamification
    GAMIFICATION_READ = "gamification:read"
    GAMIFICATION_WRITE = "gamification:write"
    GAMIFICATION_CONFIG = "gamification:config"
    
    # System Admin
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    
    # User Management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Global Permissions
    SUPER_ADMIN = "global:super_admin"
    ADMIN = "global:admin"
    MODERATOR = "global:moderator"
    VIEWER = "global:viewer"

@dataclass
class AdminRole:
    """Admin role definition"""
    name: str
    permissions: Set[AdminPermission]
    description: str
    max_session_hours: int = 8
    can_delegate: bool = False

@dataclass
class AdminSession:
    """Admin session tracking"""
    user_id: int
    session_id: str
    role: AdminRole
    started_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    actions_count: int = 0
    is_active: bool = True
    
@dataclass
class AdminAuditLog:
    """Admin audit log entry"""
    timestamp: datetime
    user_id: int
    session_id: str
    action: str
    target: Optional[str]
    parameters: Dict[str, Any]
    result: str  # success, failure, error
    ip_address: Optional[str]
    user_agent: Optional[str] = None
    risk_level: str = "low"  # low, medium, high, critical

class DianaAdminSecurity:
    """
    🛡️ ADMIN SECURITY SYSTEM
    
    Comprehensive security layer for Diana Bot admin operations with:
    - Role-based access control
    - Session management
    - Comprehensive audit logging
    - Rate limiting and anomaly detection
    """
    
    def __init__(self):
        self.logger = structlog.get_logger()
        
        # Security state
        self.active_sessions: Dict[int, AdminSession] = {}
        self.audit_logs: List[AdminAuditLog] = []
        self.failed_attempts: Dict[int, List[datetime]] = {}
        
        # Rate limiting
        self.rate_limits: Dict[int, Dict[str, List[datetime]]] = {}
        
        # Initialize roles
        self.roles = self._initialize_admin_roles()
        
        # User role assignments (would be from database in production)
        self.user_roles: Dict[int, str] = {
            # ADD YOUR TELEGRAM USER ID HERE - Get it from @userinfobot
            1280444712: "super_admin",  # 👈 REPLACE WITH YOUR REAL USER ID
            # Example: 987654321: "admin",
        }
        
    def _initialize_admin_roles(self) -> Dict[str, AdminRole]:
        """Initialize admin role definitions"""
        
        roles = {
            "super_admin": AdminRole(
                name="Super Admin",
                permissions={
                    AdminPermission.SUPER_ADMIN,
                    AdminPermission.VIP_READ, AdminPermission.VIP_WRITE, AdminPermission.VIP_DELETE, AdminPermission.VIP_CONFIG,
                    AdminPermission.CHANNEL_READ, AdminPermission.CHANNEL_WRITE, AdminPermission.CHANNEL_DELETE, AdminPermission.CHANNEL_CONFIG,
                    AdminPermission.GAMIFICATION_READ, AdminPermission.GAMIFICATION_WRITE, AdminPermission.GAMIFICATION_CONFIG,
                    AdminPermission.SYSTEM_READ, AdminPermission.SYSTEM_WRITE, AdminPermission.SYSTEM_CONFIG, AdminPermission.SYSTEM_LOGS,
                    AdminPermission.USER_READ, AdminPermission.USER_WRITE, AdminPermission.USER_DELETE
                },
                description="Full system access with all permissions",
                max_session_hours=12,
                can_delegate=True
            ),
            
            "admin": AdminRole(
                name="Admin",
                permissions={
                    AdminPermission.ADMIN,
                    AdminPermission.VIP_READ, AdminPermission.VIP_WRITE, AdminPermission.VIP_CONFIG,
                    AdminPermission.CHANNEL_READ, AdminPermission.CHANNEL_WRITE, AdminPermission.CHANNEL_CONFIG,
                    AdminPermission.GAMIFICATION_READ, AdminPermission.GAMIFICATION_WRITE,
                    AdminPermission.SYSTEM_READ,
                    AdminPermission.USER_READ, AdminPermission.USER_WRITE
                },
                description="Standard admin access for daily operations",
                max_session_hours=8,
                can_delegate=False
            ),
            
            "moderator": AdminRole(
                name="Moderator", 
                permissions={
                    AdminPermission.MODERATOR,
                    AdminPermission.VIP_READ,
                    AdminPermission.CHANNEL_READ, AdminPermission.CHANNEL_WRITE,
                    AdminPermission.GAMIFICATION_READ,
                    AdminPermission.USER_READ
                },
                description="Moderation and limited admin access",
                max_session_hours=6,
                can_delegate=False
            ),
            
            "viewer": AdminRole(
                name="Viewer",
                permissions={
                    AdminPermission.VIEWER,
                    AdminPermission.VIP_READ,
                    AdminPermission.CHANNEL_READ,
                    AdminPermission.GAMIFICATION_READ,
                    AdminPermission.SYSTEM_READ,
                    AdminPermission.USER_READ
                },
                description="Read-only access to admin panels",
                max_session_hours=4,
                can_delegate=False
            )
        }
        
        return roles
    
    # === PERMISSION CHECKING ===
    
    async def check_permission(self, user_id: int, permission: AdminPermission) -> bool:
        """Check if user has specific permission"""
        try:
            # Check if user has active session
            session = self.active_sessions.get(user_id)
            if not session or not session.is_active:
                return False
                
            # Check session timeout
            if self._is_session_expired(session):
                await self.invalidate_session(user_id)
                return False
            
            # Check permission
            has_permission = permission in session.role.permissions
            
            # Log permission check
            await self._log_security_event(
                user_id, session.session_id, f"permission_check:{permission.value}",
                {"result": has_permission}, "success" if has_permission else "denied"
            )
            
            return has_permission
            
        except Exception as e:
            self.logger.error("Error checking permission", error=str(e), user_id=user_id)
            return False
    
    async def check_multiple_permissions(self, user_id: int, permissions: List[AdminPermission]) -> Dict[AdminPermission, bool]:
        """Check multiple permissions at once"""
        results = {}
        for permission in permissions:
            results[permission] = await self.check_permission(user_id, permission)
        return results
    
    async def require_permission(self, user_id: int, permission: AdminPermission) -> bool:
        """Require permission or raise exception"""
        if not await self.check_permission(user_id, permission):
            await self._log_security_event(
                user_id, "", f"permission_denied:{permission.value}",
                {"required": permission.value}, "denied", risk_level="medium"
            )
            raise PermissionError(f"Access denied: {permission.value} required")
        return True
    
    # === SESSION MANAGEMENT ===
    
    async def create_admin_session(self, user_id: int, ip_address: str = None) -> Optional[AdminSession]:
        """Create new admin session"""
        try:
            # Check if user has admin role
            role_name = self.user_roles.get(user_id)
            if not role_name or role_name not in self.roles:
                # Mock role assignment for demo - in production would query database
                if user_id in {123456789, 987654321}:  # Mock admin users
                    role_name = "admin"
                    self.user_roles[user_id] = role_name
                else:
                    return None
            
            role = self.roles[role_name]
            
            # Generate session ID
            session_data = f"{user_id}:{datetime.now().isoformat()}:{ip_address or 'unknown'}"
            session_id = hashlib.sha256(session_data.encode()).hexdigest()[:16]
            
            # Create session
            session = AdminSession(
                user_id=user_id,
                session_id=session_id,
                role=role,
                started_at=datetime.now(),
                last_activity=datetime.now(),
                ip_address=ip_address
            )
            
            # Invalidate old session if exists
            if user_id in self.active_sessions:
                await self.invalidate_session(user_id)
            
            # Store session
            self.active_sessions[user_id] = session
            
            # Log session creation
            await self._log_security_event(
                user_id, session_id, "session_created",
                {"role": role_name, "ip": ip_address}, "success"
            )
            
            self.logger.info("Admin session created", user_id=user_id, role=role_name, session_id=session_id)
            return session
            
        except Exception as e:
            self.logger.error("Error creating admin session", error=str(e), user_id=user_id)
            return None
    
    async def get_active_session(self, user_id: int) -> Optional[AdminSession]:
        """Get active session for user"""
        session = self.active_sessions.get(user_id)
        if session and session.is_active and not self._is_session_expired(session):
            # Update last activity
            session.last_activity = datetime.now()
            return session
        elif session:
            # Session expired, invalidate
            await self.invalidate_session(user_id)
        return None
    
    async def invalidate_session(self, user_id: int) -> bool:
        """Invalidate admin session"""
        try:
            session = self.active_sessions.get(user_id)
            if session:
                session.is_active = False
                
                # Log session end
                await self._log_security_event(
                    user_id, session.session_id, "session_invalidated",
                    {"duration_minutes": (datetime.now() - session.started_at).total_seconds() // 60}, "success"
                )
                
                # Remove from active sessions
                del self.active_sessions[user_id]
                
                self.logger.info("Admin session invalidated", user_id=user_id)
                return True
            return False
            
        except Exception as e:
            self.logger.error("Error invalidating session", error=str(e), user_id=user_id)
            return False
    
    def _is_session_expired(self, session: AdminSession) -> bool:
        """Check if session is expired"""
        max_duration = timedelta(hours=session.role.max_session_hours)
        return (datetime.now() - session.started_at) > max_duration
    
    # === RATE LIMITING ===
    
    async def check_rate_limit(self, user_id: int, action: str, max_per_minute: int = 60) -> bool:
        """Check if user is within rate limits"""
        try:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            
            # Initialize user rate limits if needed
            if user_id not in self.rate_limits:
                self.rate_limits[user_id] = {}
            
            if action not in self.rate_limits[user_id]:
                self.rate_limits[user_id][action] = []
            
            # Clean old entries
            self.rate_limits[user_id][action] = [
                timestamp for timestamp in self.rate_limits[user_id][action]
                if timestamp > minute_ago
            ]
            
            # Check limit
            current_count = len(self.rate_limits[user_id][action])
            if current_count >= max_per_minute:
                await self._log_security_event(
                    user_id, "", f"rate_limit_exceeded:{action}",
                    {"count": current_count, "limit": max_per_minute}, "blocked",
                    risk_level="medium"
                )
                return False
            
            # Add current request
            self.rate_limits[user_id][action].append(now)
            return True
            
        except Exception as e:
            self.logger.error("Error checking rate limit", error=str(e), user_id=user_id)
            return True  # Allow on error to avoid blocking legitimate users
    
    # === AUDIT LOGGING ===
    
    async def log_admin_action(
        self,
        user_id: int,
        action: str,
        target: str = None,
        parameters: Dict[str, Any] = None,
        result: str = "success",
        risk_level: str = "low"
    ) -> None:
        """Log admin action for audit trail"""
        session = self.active_sessions.get(user_id)
        session_id = session.session_id if session else "no_session"
        ip_address = session.ip_address if session else None
        
        await self._log_security_event(
            user_id, session_id, action, parameters or {}, result, 
            target=target, risk_level=risk_level, ip_address=ip_address
        )
        
        # Update session action count
        if session:
            session.actions_count += 1
    
    async def _log_security_event(
        self,
        user_id: int,
        session_id: str,
        action: str,
        parameters: Dict[str, Any],
        result: str,
        target: str = None,
        risk_level: str = "low",
        ip_address: str = None
    ) -> None:
        """Internal security event logging"""
        
        audit_entry = AdminAuditLog(
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            action=action,
            target=target,
            parameters=parameters,
            result=result,
            ip_address=ip_address,
            risk_level=risk_level
        )
        
        # Store audit log
        self.audit_logs.append(audit_entry)
        
        # Keep only last 10000 entries in memory
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
        
        # Log to structured logger
        self.logger.info(
            "Admin security event",
            user_id=user_id,
            session_id=session_id,
            action=action,
            target=target,
            result=result,
            risk_level=risk_level,
            parameters=parameters
        )
        
        # Check for suspicious patterns
        await self._analyze_security_patterns(user_id, audit_entry)
    
    async def _analyze_security_patterns(self, user_id: int, log_entry: AdminAuditLog) -> None:
        """Analyze patterns for security anomalies"""
        try:
            # Check for rapid consecutive failures
            recent_failures = [
                log for log in self.audit_logs[-50:]  # Last 50 entries
                if (log.user_id == user_id and 
                    log.result in ["failure", "denied", "blocked"] and
                    (datetime.now() - log.timestamp).total_seconds() < 300)  # Last 5 minutes
            ]
            
            if len(recent_failures) >= 5:
                await self._log_security_event(
                    user_id, log_entry.session_id, "security_alert:rapid_failures",
                    {"failure_count": len(recent_failures)}, "alert", risk_level="high"
                )
                
                # Consider session invalidation for high-risk patterns
                if len(recent_failures) >= 10:
                    await self.invalidate_session(user_id)
            
        except Exception as e:
            self.logger.error("Error analyzing security patterns", error=str(e))
    
    # === AUDIT QUERIES ===
    
    def get_audit_logs(
        self,
        user_id: int = None,
        action_filter: str = None,
        risk_level: str = None,
        limit: int = 100
    ) -> List[AdminAuditLog]:
        """Get filtered audit logs"""
        
        logs = self.audit_logs.copy()
        
        # Apply filters
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if action_filter:
            logs = [log for log in logs if action_filter in log.action]
        
        if risk_level:
            logs = [log for log in logs if log.risk_level == risk_level]
        
        # Sort by timestamp descending and limit
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security system summary"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        recent_logs = [log for log in self.audit_logs if log.timestamp > last_24h]
        
        return {
            "active_sessions": len(self.active_sessions),
            "total_audit_entries": len(self.audit_logs),
            "events_last_24h": len(recent_logs),
            "events_last_hour": len([log for log in recent_logs if log.timestamp > last_hour]),
            "high_risk_events_24h": len([log for log in recent_logs if log.risk_level == "high"]),
            "failed_attempts_24h": len([log for log in recent_logs if log.result in ["failure", "denied", "blocked"]]),
            "unique_users_24h": len(set(log.user_id for log in recent_logs)),
            "top_actions_24h": self._get_top_actions(recent_logs),
            "system_health": "healthy" if len(self.active_sessions) > 0 else "inactive"
        }
    
    def _get_top_actions(self, logs: List[AdminAuditLog], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top actions from logs"""
        action_counts = {}
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
        
        sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"action": action, "count": count} for action, count in sorted_actions[:top_n]]
