"""Clase base para los modelos."""

import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, Text
import json

Base = declarative_base()

class TimestampMixin:
    """Mixin para agregar campos de fecha de creación y actualización."""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class JSONArray(TypeDecorator):
    """
    Array type that works with both PostgreSQL ARRAY and SQLite JSON.
    Automatically selects the appropriate implementation based on database type.
    """
    impl = Text
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(self.item_type))
        else:
            return dialect.type_descriptor(JSON())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            return json.dumps(value) if value else "[]"
    
    def process_result_value(self, value, dialect):
        if value is None:
            return []
        if dialect.name == 'postgresql':
            return value if value else []
        else:
            try:
                return json.loads(value) if value else []
            except (json.JSONDecodeError, TypeError):
                return []

def make_array_column(item_type):
    """Factory function to create array columns that work with both SQLite and PostgreSQL."""
    array_type = JSONArray()
    array_type.item_type = item_type
    return array_type