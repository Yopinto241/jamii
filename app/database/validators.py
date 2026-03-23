"""
Database constraint validation helpers
"""

import psycopg2
from fastapi import HTTPException
from app.database.db import get_connection


class DatabaseValidator:
    """Validates database operations and constraints"""
    
    @staticmethod
    def check_duplicate_name(table: str, name: str, conn=None, extra_where: str = None):
        """Check if a name already exists in a table"""
        if not conn:
            conn = get_connection()
            close_after = True
        else:
            close_after = False
        
        try:
            cur = conn.cursor()
            query = f"SELECT id FROM {table} WHERE LOWER(name) = LOWER(%s)"
            params = [name]
            
            if extra_where:
                query += f" AND {extra_where}"
            
            cur.execute(query, tuple(params))
            result = cur.fetchone()
            cur.close()
            
            return result is not None
        finally:
            if close_after:
                conn.close()
    
    @staticmethod
    def check_foreign_key(table: str, id_column: str, value: int, conn=None):
        """Check if a foreign key reference exists"""
        if not conn:
            conn = get_connection()
            close_after = True
        else:
            close_after = False
        
        try:
            cur = conn.cursor()
            query = f"SELECT id FROM {table} WHERE {id_column} = %s"
            cur.execute(query, (value,))
            result = cur.fetchone()
            cur.close()
            
            return result is not None
        finally:
            if close_after:
                conn.close()
    
    @staticmethod
    def check_unique_phone(table: str, phone: str, conn=None, exclude_id: int = None):
        """Check if a phone number is unique"""
        if not conn:
            conn = get_connection()
            close_after = True
        else:
            close_after = False
        
        try:
            cur = conn.cursor()
            query = f"SELECT id FROM {table} WHERE phone = %s"
            params = [phone]
            
            if exclude_id:
                query += " AND id != %s"
                params.append(exclude_id)
            
            cur.execute(query, tuple(params))
            result = cur.fetchone()
            cur.close()
            
            return result is not None
        finally:
            if close_after:
                conn.close()
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list):
        """Validate that required fields are present and not empty"""
        for field in required_fields:
            if field not in data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
            
            if data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{field}' cannot be empty"
                )
    
    @staticmethod
    def validate_phone(phone: str):
        """Validate phone number format"""
        phone_str = str(phone).strip()
        
        # Remove spaces, hyphens, parentheses
        cleaned = phone_str.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Must start with + or be numeric
        if not cleaned.startswith("+") and not cleaned.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Invalid phone format"
            )
        
        # Must be at least 7 digits
        if len(cleaned.replace("+", "")) < 7:
            raise HTTPException(
                status_code=400,
                detail="Phone number too short"
            )
        
        return phone_str
    
    @staticmethod
    def handle_database_error(error: Exception, context: str = ""):
        """Convert database errors to appropriate HTTP exceptions"""
        error_msg = str(error)
        
        if "duplicate key" in error_msg.lower():
            raise HTTPException(
                status_code=409,
                detail=f"Duplicate entry: {context or 'Record already exists'}"
            )
        elif "foreign key" in error_msg.lower():
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete: {context or 'Referenced by other records'}"
            )
        elif "not null" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Required field is missing or null"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {error_msg}"
            )
