"""Custom API exceptions."""

from fastapi import HTTPException, status


class EntityNotFoundError(HTTPException):
    """Exception raised when an entity is not found."""

    def __init__(self, entity_type: str, entity_id: str | None = None):
        """
        Initialize EntityNotFoundError.

        Args:
            entity_type: Type of entity (e.g., "AgentDesk", "Task")
            entity_id: Optional entity identifier
        """
        if entity_id:
            detail = f"{entity_type} with id '{entity_id}' not found"
        else:
            detail = f"{entity_type} not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class EntityAlreadyExistsError(HTTPException):
    """Exception raised when trying to create an entity that already exists."""

    def __init__(self, entity_type: str, identifier: str):
        """
        Initialize EntityAlreadyExistsError.

        Args:
            entity_type: Type of entity (e.g., "AgentDesk", "Task")
            identifier: The identifier that already exists
        """
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{entity_type} with identifier '{identifier}' already exists"
        )


class InvalidOperationError(HTTPException):
    """Exception raised when an operation is invalid."""

    def __init__(self, message: str):
        """
        Initialize InvalidOperationError.

        Args:
            message: Error message describing why the operation is invalid
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class ValidationError(HTTPException):
    """Exception raised for validation errors."""

    def __init__(self, message: str):
        """
        Initialize ValidationError.

        Args:
            message: Validation error message
        """
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )
