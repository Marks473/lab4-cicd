from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from converter.application.use_cases import (
    CreateTaskUseCase,
    DeleteTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
    TaskNotFoundError,
    TaskValidationError,
    UpdateTaskUseCase,
)
from converter.infrastructure.repositories import DjangoORMConversionTaskRepository


def _get_repository():
    return DjangoORMConversionTaskRepository()


def _task_to_dict(task):
    return {
        "id": task.id,
        "filename": task.filename,
        "source_format": task.source_format,
        "target_format": task.target_format,
        "bitrate": task.bitrate,
        "channels": task.channels,
        "status": task.status,
        "created_at": task.created_at,
    }


class ConversionTaskInputSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255)
    source_format = serializers.ChoiceField(choices=["mp3", "ogg"])
    target_format = serializers.ChoiceField(choices=["mp3", "ogg"])
    bitrate = serializers.IntegerField(min_value=1)
    channels = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(
        choices=["new", "processing", "done"],
        required=False,
        default="new",
    )


class ConversionTaskOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    filename = serializers.CharField()
    source_format = serializers.CharField()
    target_format = serializers.CharField()
    bitrate = serializers.IntegerField()
    channels = serializers.IntegerField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField(allow_null=True)


class TaskListCreateAPIView(APIView):
    def get(self, request):
        source_format = request.query_params.get("source_format")
        status_value = request.query_params.get("status")

        use_case = ListTasksUseCase(_get_repository())

        try:
            tasks = use_case.execute(
                source_format=source_format,
                status=status_value,
            )
        except TaskValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = [_task_to_dict(task) for task in tasks]
        serializer = ConversionTaskOutputSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        input_serializer = ConversionTaskInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        use_case = CreateTaskUseCase(_get_repository())

        try:
            task = use_case.execute(**input_serializer.validated_data)
        except TaskValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ConversionTaskOutputSerializer(_task_to_dict(task))
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class TaskRetrieveUpdateDeleteAPIView(APIView):
    def get(self, request, pk: int):
        use_case = GetTaskUseCase(_get_repository())

        try:
            task = use_case.execute(pk)
        except TaskNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ConversionTaskOutputSerializer(_task_to_dict(task))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk: int):
        input_serializer = ConversionTaskInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        use_case = UpdateTaskUseCase(_get_repository())

        try:
            task = use_case.execute(task_id=pk, **input_serializer.validated_data)
        except TaskNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except TaskValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ConversionTaskOutputSerializer(_task_to_dict(task))
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int):
        get_use_case = GetTaskUseCase(_get_repository())

        try:
            existing_task = get_use_case.execute(pk)
        except TaskNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        input_serializer = ConversionTaskInputSerializer(
            data=request.data,
            partial=True,
        )
        input_serializer.is_valid(raise_exception=True)

        merged_data = {
            "filename": input_serializer.validated_data.get("filename", existing_task.filename),
            "source_format": input_serializer.validated_data.get("source_format", existing_task.source_format),
            "target_format": input_serializer.validated_data.get("target_format", existing_task.target_format),
            "bitrate": input_serializer.validated_data.get("bitrate", existing_task.bitrate),
            "channels": input_serializer.validated_data.get("channels", existing_task.channels),
            "status": input_serializer.validated_data.get("status", existing_task.status),
        }

        update_use_case = UpdateTaskUseCase(_get_repository())

        try:
            updated_task = update_use_case.execute(task_id=pk, **merged_data)
        except TaskValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ConversionTaskOutputSerializer(_task_to_dict(updated_task))
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int):
        use_case = DeleteTaskUseCase(_get_repository())

        try:
            use_case.execute(pk)
        except TaskNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)