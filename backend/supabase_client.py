import os
from supabase import create_client, Client
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.client: Client = create_client(url, key)
        logger.info("Supabase client initialized")

    async def create_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in the specified table"""
        try:
            # Convert datetime objects to ISO string format
            processed_data = self._process_data_for_insert(data)
            result = self.client.table(table).insert(processed_data).execute()
            if result.data:
                return result.data[0]
            else:
                raise Exception(f"Failed to create record in {table}")
        except Exception as e:
            logger.error(f"Error creating record in {table}: {str(e)}")
            raise

    async def get_record(self, table: str, id_field: str, id_value: str) -> Optional[Dict[str, Any]]:
        """Get a single record by ID"""
        try:
            result = self.client.table(table).select("*").eq(id_field, id_value).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting record from {table}: {str(e)}")
            raise

    async def get_records(self, table: str, filters: Optional[Dict[str, Any]] = None, 
                         order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get multiple records with optional filters"""
        try:
            query = self.client.table(table).select("*")
            
            if filters:
                for field, value in filters.items():
                    if isinstance(value, dict):
                        # Handle complex filters like {"$in": [1, 2, 3]}
                        for operator, op_value in value.items():
                            if operator == "$in":
                                query = query.in_(field, op_value)
                            elif operator == "$gte":
                                query = query.gte(field, op_value)
                            elif operator == "$lte":
                                query = query.lte(field, op_value)
                            elif operator == "$regex":
                                query = query.ilike(field, f"%{op_value}%")
                    else:
                        query = query.eq(field, value)
            
            if order_by:
                if order_by.startswith("-"):
                    # Descending order
                    query = query.order(order_by[1:], desc=True)
                else:
                    # Ascending order
                    query = query.order(order_by)
            
            if limit:
                query = query.limit(limit)
                
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting records from {table}: {str(e)}")
            raise

    async def update_record(self, table: str, id_field: str, id_value: str, 
                          data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by ID"""
        try:
            processed_data = self._process_data_for_update(data)
            result = self.client.table(table).update(processed_data).eq(id_field, id_value).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating record in {table}: {str(e)}")
            raise

    async def delete_record(self, table: str, id_field: str, id_value: str) -> bool:
        """Delete a record by ID"""
        try:
            result = self.client.table(table).delete().eq(id_field, id_value).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting record from {table}: {str(e)}")
            raise

    async def count_records(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records in a table with optional filters"""
        try:
            query = self.client.table(table).select("*", count="exact")
            
            if filters:
                for field, value in filters.items():
                    if isinstance(value, dict):
                        for operator, op_value in value.items():
                            if operator == "$in":
                                query = query.in_(field, op_value)
                            elif operator == "$gte":
                                query = query.gte(field, op_value)
                            elif operator == "$lte":
                                query = query.lte(field, op_value)
                    else:
                        query = query.eq(field, value)
            
            result = query.execute()
            return result.count if result.count is not None else 0
        except Exception as e:
            logger.error(f"Error counting records in {table}: {str(e)}")
            raise

    async def find_one(self, table: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single record with filters (equivalent to MongoDB find_one)"""
        try:
            query = self.client.table(table).select("*")
            
            for field, value in filters.items():
                if isinstance(value, dict):
                    for operator, op_value in value.items():
                        if operator == "$regex":
                            query = query.ilike(field, f"%{op_value}%")
                        elif operator == "$in":
                            query = query.in_(field, op_value)
                else:
                    query = query.eq(field, value)
            
            result = query.limit(1).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error finding record in {table}: {str(e)}")
            raise

    async def aggregate(self, table: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simplified aggregation for basic grouping operations"""
        try:
            # This is a simplified version - Supabase doesn't have full MongoDB aggregation
            # We'll handle basic cases like counting by category
            for stage in pipeline:
                if "$group" in stage:
                    group_fields = stage["$group"]
                    if "_id" in group_fields and "count" in group_fields:
                        group_by = group_fields["_id"]
                        if group_by.startswith("$"):
                            field_name = group_by[1:]  # Remove $ prefix
                            # Use PostgreSQL aggregation
                            result = self.client.rpc('aggregate_by_field', {
                                'table_name': table,
                                'field_name': field_name
                            }).execute()
                            return result.data if result.data else []
            
            # Fallback for unsupported aggregations
            return []
        except Exception as e:
            logger.error(f"Error in aggregation for {table}: {str(e)}")
            return []

    def _process_data_for_insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data before inserting to Supabase"""
        processed = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                processed[key] = value.isoformat()
            elif hasattr(value, 'dict'):  # Pydantic model
                processed[key] = value.dict()
            elif isinstance(value, list) and value and hasattr(value[0], 'dict'):
                processed[key] = [item.dict() for item in value]
            else:
                processed[key] = value
        return processed

    def _process_data_for_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data before updating in Supabase"""
        processed = {}
        for key, value in data.items():
            if value is not None:  # Skip None values
                if isinstance(value, datetime):
                    processed[key] = value.isoformat()
                elif hasattr(value, 'dict'):  # Pydantic model
                    processed[key] = value.dict()
                elif isinstance(value, list) and value and hasattr(value[0], 'dict'):
                    processed[key] = [item.dict() for item in value]
                else:
                    processed[key] = value
        return processed

    async def execute_raw_sql(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query (for complex operations)"""
        try:
            result = self.client.rpc('execute_sql', {'query': query, 'params': params or {}}).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error executing raw SQL: {str(e)}")
            raise

    def get_connection_info(self) -> Dict[str, Any]:
        """Get Supabase connection information"""
        try:
            return {
                "url": self.client.supabase_url,
                "key_preview": self.client.supabase_key[:20] + "..." if hasattr(self.client, 'supabase_key') else "***",
                "project_id": self.client.supabase_url.split('//')[1].split('.')[0] if self.client.supabase_url else None,
                "status": "connected"
            }
        except Exception as e:
            logger.error(f"Error getting connection info: {str(e)}")
            return {
                "url": "unknown",
                "key_preview": "***",
                "project_id": "unknown", 
                "status": "error",
                "error": str(e)
            }

    def translate_token(self, token: str) -> Dict[str, Any]:
        """Decode and analyze JWT token"""
        try:
            import jwt
            # Decode without verification to inspect payload
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Extract key information
            info = {
                "issuer": decoded.get("iss", "unknown"),
                "project_ref": decoded.get("ref", "unknown"),
                "role": decoded.get("role", "unknown"),
                "issued_at": decoded.get("iat", 0),
                "expires_at": decoded.get("exp", 0),
                "valid": True
            }
            
            # Convert timestamps to readable format
            if info["issued_at"]:
                info["issued_at_readable"] = datetime.fromtimestamp(info["issued_at"]).isoformat()
            if info["expires_at"]:
                info["expires_at_readable"] = datetime.fromtimestamp(info["expires_at"]).isoformat()
                info["is_expired"] = datetime.now().timestamp() > info["expires_at"]
            
            return info
            
        except Exception as e:
            logger.error(f"Error translating token: {str(e)}")
            return {
                "valid": False,
                "error": str(e),
                "raw_token_preview": token[:20] + "..." if len(token) > 20 else token
            }

    async def get_database_schema(self) -> List[Dict[str, Any]]:
        """Get database schema information"""
        try:
            # Try to get schema via RPC call
            schema_info = self.client.rpc('get_schema_info').execute()
            if schema_info.data:
                return schema_info.data
            else:
                # Fallback: return known tables structure
                return [
                    {"table_name": "courses", "columns": ["id", "title", "description", "level", "status"]},
                    {"table_name": "lessons", "columns": ["id", "course_id", "title", "content", "video_url"]},
                    {"table_name": "students", "columns": ["id", "name", "email", "total_score", "is_active"]},
                    {"table_name": "admin_users", "columns": ["id", "username", "email", "role", "created_at"]},
                    {"table_name": "team_members", "columns": ["id", "name", "position", "bio", "photo"]},
                    {"table_name": "qa_questions", "columns": ["id", "question", "answer", "category", "views"]}
                ]
        except Exception as e:
            logger.error(f"Error getting database schema: {str(e)}")
            return []

# Global instance
supabase_client = SupabaseClient()