from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _normalize_tags(raw: list[str]) -> list[str]:
    """
    Strip whitespace, lowercase, drop blanks, deduplicate, preserve order.
    Raises ValueError if any tag exceeds 32 characters or if more than 10
    tags remain after normalization.
    """
    seen: set[str] = set()
    result: list[str] = []

    for tag in raw:
        normalized = tag.strip().lower()
        if not normalized:
            continue
        if len(normalized) > 32:
            raise ValueError(
                f"Each tag must be at most 32 characters (got '{normalized[:32]}...')"
            )
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    if len(result) > 10:
        raise ValueError(
            f"A task can have at most 10 tags (got {len(result)})"
        )

    return result


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Validate and normalize a task title.

        Args:
            value (str): The raw title.

        Returns:
            str: The stripped title.

        Raises:
            ValueError: If the stripped title is blank, or if it is
                longer than 200 characters. Pydantic surfaces this
                as part of a 422 response.
        """
        stripped = value.strip()
        if not stripped:
            raise ValueError("title cannot be blank")
        if len(stripped) > 200:
            raise ValueError("title must be at most 200 characters")
        return stripped

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        """Normalize and validate a task's tags.

        Delegates to `_normalize_tags`.

        Args:
            value (list[str]): The raw tag list.

        Returns:
            list[str]: Stripped, lowercased, deduplicated tags with
            blank entries removed, preserving first-seen order.

        Raises:
            ValueError: If any tag exceeds 32 characters after
                normalization, or if more than 10 tags remain.
        """
        return _normalize_tags(value)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        """Validate and normalize an optional task title.

        Args:
            value (Optional[str]): The raw title, or None if the
                field was not supplied in the update payload.

        Returns:
            Optional[str]: None if `value` is None, otherwise the
            stripped title.

        Raises:
            ValueError: If a non-None value strips to blank, or is
                longer than 200 characters.
        """
        if value is None:
            return value
        stripped = value.strip()
        if not stripped:
            raise ValueError("title cannot be blank")
        if len(stripped) > 200:
            raise ValueError("title must be at most 200 characters")
        return stripped

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        """Validate and normalize an optional tag list.

        Args:
            value (Optional[list[str]]): The raw tag list, or None
                if the field was not supplied in the update payload.

        Returns:
            Optional[list[str]]: None if `value` is None, otherwise
            the result of `_normalize_tags(value)`.

        Raises:
            ValueError: If any tag exceeds 32 characters after
                normalization, or if more than 10 tags remain.
        """
        if value is None:
            return value
        return _normalize_tags(value)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    tags: list[str]
    created_at: datetime
    updated_at: datetime