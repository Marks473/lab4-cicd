from typing import Optional

from converter.domain.entities import ConversionTaskEntity
from converter.domain.repositories import ConversionTaskRepository
from converter.infrastructure.mappers import to_entity, to_model_data
from converter.models import ConversionTask


class DjangoORMConversionTaskRepository(ConversionTaskRepository):
    def list_all(self, filters=None):
        queryset = ConversionTask.objects.all().order_by("-created_at")

        filters = filters or {}

        source_format = filters.get("source_format")
        status_value = filters.get("status")

        if source_format:
            queryset = queryset.filter(source_format=source_format)

        if status_value:
            queryset = queryset.filter(status=status_value)

        return [to_entity(obj) for obj in queryset]

    def get_by_id(self, task_id: int) -> Optional[ConversionTaskEntity]:
        try:
            obj = ConversionTask.objects.get(pk=task_id)
            return to_entity(obj)
        except ConversionTask.DoesNotExist:
            return None

    def create(self, task: ConversionTaskEntity) -> ConversionTaskEntity:
        obj = ConversionTask.objects.create(**to_model_data(task))
        return to_entity(obj)

    def update(self, task: ConversionTaskEntity) -> ConversionTaskEntity:
        obj = ConversionTask.objects.get(pk=task.id)

        obj.filename = task.filename
        obj.source_format = task.source_format
        obj.target_format = task.target_format
        obj.bitrate = task.bitrate
        obj.channels = task.channels
        obj.status = task.status

        obj.save()
        return to_entity(obj)

    def delete(self, task_id: int) -> None:
        ConversionTask.objects.filter(pk=task_id).delete()