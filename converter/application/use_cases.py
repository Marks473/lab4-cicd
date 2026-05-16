from __future__ import annotations

from typing import Optional

from converter.domain.entities import ConversionTaskEntity
from converter.infrastructure.repositories import ConversionTaskRepository


ALLOWED_FORMATS = {"mp3", "ogg"}
ALLOWED_STATUSES = {"new", "processing", "done"}
ALLOWED_CHANNELS = {1, 2}


class TaskValidationError(ValueError):
    """Ошибка бизнес-валидации."""
    pass


class TaskNotFoundError(LookupError):
    """Задача не найдена."""
    pass


def _normalize_str(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def _validate_task_data(
    filename: str,
    source_format: str,
    target_format: str,
    bitrate: int,
    channels: int,
    status_value: str,
) -> None:
    filename = _normalize_str(filename)

    if not filename:
        raise TaskValidationError("Имя файла не должно быть пустым.")

    if source_format not in ALLOWED_FORMATS:
        raise TaskValidationError(
            f"Недопустимый исходный формат: {source_format}. "
            f"Допустимые значения: {', '.join(sorted(ALLOWED_FORMATS))}."
        )

    if target_format not in ALLOWED_FORMATS:
        raise TaskValidationError(
            f"Недопустимый целевой формат: {target_format}. "
            f"Допустимые значения: {', '.join(sorted(ALLOWED_FORMATS))}."
        )

    if bitrate <= 0:
        raise TaskValidationError("Битрейт должен быть положительным.")

    if channels not in ALLOWED_CHANNELS:
        raise TaskValidationError("Число каналов должно быть 1 или 2.")

    if status_value not in ALLOWED_STATUSES:
        raise TaskValidationError(
            f"Недопустимый статус: {status_value}. "
            f"Допустимые значения: {', '.join(sorted(ALLOWED_STATUSES))}."
        )


class CreateTaskUseCase:
    def __init__(self, repository: ConversionTaskRepository):
        self.repository = repository

    def execute(
        self,
        filename: str,
        source_format: str,
        target_format: str,
        bitrate: int,
        channels: int,
        status: str = "new",
    ) -> ConversionTaskEntity:
        _validate_task_data(
            filename=filename,
            source_format=source_format,
            target_format=target_format,
            bitrate=bitrate,
            channels=channels,
            status_value=status,
        )

        task = ConversionTaskEntity(
            id=None,
            filename=filename.strip(),
            source_format=source_format,
            target_format=target_format,
            bitrate=bitrate,
            channels=channels,
            status=status,
            created_at=None,
        )

        return self.repository.create(task)


class ListTasksUseCase:
    def __init__(self, repository: ConversionTaskRepository):
        self.repository = repository

    def execute(
        self,
        source_format: Optional[str] = None,
        status: Optional[str] = None,
    ):
        filters = {}

        source_format = _normalize_str(source_format)
        status = _normalize_str(status)

        if source_format:
            if source_format not in ALLOWED_FORMATS:
                raise TaskValidationError("Недопустимое значение фильтра source_format.")
            filters["source_format"] = source_format

        if status:
            if status not in ALLOWED_STATUSES:
                raise TaskValidationError("Недопустимое значение фильтра status.")
            filters["status"] = status

        return self.repository.list_all(filters=filters)


class GetTaskUseCase:
    def __init__(self, repository: ConversionTaskRepository):
        self.repository = repository

    def execute(self, task_id: int) -> ConversionTaskEntity:
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Задача с id={task_id} не найдена.")
        return task


class UpdateTaskUseCase:
    def __init__(self, repository: ConversionTaskRepository):
        self.repository = repository

    def execute(
        self,
        task_id: int,
        filename: str,
        source_format: str,
        target_format: str,
        bitrate: int,
        channels: int,
        status: str,
    ) -> ConversionTaskEntity:
        existing_task = self.repository.get_by_id(task_id)
        if existing_task is None:
            raise TaskNotFoundError(f"Задача с id={task_id} не найдена.")

        _validate_task_data(
            filename=filename,
            source_format=source_format,
            target_format=target_format,
            bitrate=bitrate,
            channels=channels,
            status_value=status,
        )

        updated_task = ConversionTaskEntity(
            id=existing_task.id,
            filename=filename.strip(),
            source_format=source_format,
            target_format=target_format,
            bitrate=bitrate,
            channels=channels,
            status=status,
            created_at=existing_task.created_at,
        )

        return self.repository.update(updated_task)


class DeleteTaskUseCase:
    def __init__(self, repository: ConversionTaskRepository):
        self.repository = repository

    def execute(self, task_id: int) -> None:
        existing_task = self.repository.get_by_id(task_id)
        if existing_task is None:
            raise TaskNotFoundError(f"Задача с id={task_id} не найдена.")
        self.repository.delete(task_id)