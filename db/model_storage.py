"""
Storage module for Model operations.
"""

import asyncpg
from typing import List, Optional, Dict, Any, Callable
from models.model import Model
from models.model_details import ModelDetails
from models.model_task import ModelTask
from models.model_provider import ModelProvider
from db.db_utils import typed_pool, get_recovery_manager


class ModelStorage:
    def __init__(self, pool: asyncpg.Pool, get_query: Callable[[str], str]):
        self.pool = pool
        self.typed_pool = typed_pool(pool)
        self.get_query = get_query
        self._recovery_manager = get_recovery_manager(pool)

    async def list_models(self) -> List[Model]:
        """List all available models."""
        query = self.get_query("list_models")

        async with self.typed_pool.acquire() as conn:
            rows = await self._recovery_manager.execute_with_recovery(conn.fetch, query)
            return [self._row_to_model(row) for row in rows]

    async def get_model(self, model_id: str) -> Optional[Model]:
        """Get a model by its ID."""
        query = self.get_query("get_model")

        async with self.typed_pool.acquire() as conn:
            row = await self._recovery_manager.execute_with_recovery(
                conn.fetchrow, query, model_id
            )
            return self._row_to_model(row) if row else None

    async def create_model(self, model: Model) -> Model:
        """Create a new model."""
        query = self.get_query("create_model")

        async with self.typed_pool.acquire() as conn:
            row = await self._recovery_manager.execute_with_recovery(
                conn.fetchrow,
                query,
                model.id,
                model.name,
                model.model,
                model.task.value,  # Store enum value
                model.modified_at,
                model.digest,
                model.details.model_dump_json(),  # Store details as JSON
                model.provider.value,
            )
            return self._row_to_model(row)

    async def delete_model(self, model_id: str) -> bool:
        """Delete a model by its ID."""
        query = self.get_query("delete_model")

        async with self.typed_pool.acquire() as conn:
            result = await self._recovery_manager.execute_with_recovery(
                conn.execute, query, model_id
            )
            return "DELETE 1" in result

    def _row_to_model(self, row: Dict[str, Any]) -> Model:
        """Convert a database row to a Model object."""
        # Extract details from row (required field)
        details_data = row.get("details")
        if details_data is None:
            raise ValueError("Model details cannot be None")

        if isinstance(details_data, dict):
            details = ModelDetails(**details_data)
        else:
            # Parse from JSON string
            details = ModelDetails.model_validate_json(details_data)

        # Extract provider from row (required field)
        provider_data = row.get("provider")
        if provider_data is None:
            raise ValueError("Model provider cannot be None")

        # Convert provider to ModelProvider enum if it's a string
        if isinstance(provider_data, str):
            provider = ModelProvider(provider_data)
        else:
            provider = provider_data

        return Model(
            id=row["id"],
            name=row["name"],
            model=row["model_name"],  # Assuming column name is model_name
            task=ModelTask(row["task"]),  # Convert string to enum
            modified_at=row["modified_at"],
            digest=row["digest"],
            details=details,
            provider=provider,
        )
