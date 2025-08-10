"""
Bot Middleware Module
====================

Contains middleware for enhancing bot functionality:
- User Experience Middleware
- Error Handling Middleware  
- Analytics Middleware
"""

from .user_experience import create_user_experience_middleware

__all__ = ['create_user_experience_middleware']