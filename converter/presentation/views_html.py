from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View

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
from converter.presentation.forms import ConversionTaskForm


def _get_repository():
    return DjangoORMConversionTaskRepository()


def _task_to_template_dict(task):
    """
    Преобразуем доменную сущность в словарь,
    совместимый с текущими Django-шаблонами.
    """
    return {
        "id": task.id,
        "pk": task.id,  # чтобы старые шаблоны с task.pk не ломались
        "filename": task.filename,
        "source_format": task.source_format,
        "target_format": task.target_format,
        "bitrate": task.bitrate,
        "channels": task.channels,
        "status": task.status,
        "created_at": task.created_at,
    }


class TaskListView(View):
    template_name = "converter/task_list.html"
    paginate_by = 5

    def get(self, request):
        source_format = request.GET.get("source_format")
        status_value = request.GET.get("status")

        use_case = ListTasksUseCase(_get_repository())

        try:
            tasks = use_case.execute(
                source_format=source_format,
                status=status_value,
            )
        except TaskValidationError as exc:
            tasks = []
            form_error = str(exc)
        else:
            form_error = None

        task_dicts = [_task_to_template_dict(task) for task in tasks]

        paginator = Paginator(task_dicts, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "tasks": page_obj,
            "object_list": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "is_paginated": page_obj.has_other_pages(),
            "selected_source_format": source_format or "",
            "selected_status": status_value or "",
            "form_error": form_error,
        }
        return render(request, self.template_name, context)


class TaskDetailView(View):
    template_name = "converter/task_detail.html"

    def get(self, request, pk: int):
        use_case = GetTaskUseCase(_get_repository())

        try:
            task = use_case.execute(pk)
        except TaskNotFoundError as exc:
            raise Http404(str(exc))

        task_data = _task_to_template_dict(task)

        context = {
            "task": task_data,
            "object": task_data,
        }
        return render(request, self.template_name, context)


class TaskCreateView(View):
    template_name = "converter/task_form.html"

    def get(self, request):
        form = ConversionTaskForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ConversionTaskForm(request.POST)

        if form.is_valid():
            use_case = CreateTaskUseCase(_get_repository())

            try:
                use_case.execute(**form.cleaned_data)
                return redirect("task_list")
            except TaskValidationError as exc:
                form.add_error(None, str(exc))

        return render(request, self.template_name, {"form": form})


class TaskUpdateView(View):
    template_name = "converter/task_form.html"

    def get(self, request, pk: int):
        get_use_case = GetTaskUseCase(_get_repository())

        try:
            task = get_use_case.execute(pk)
        except TaskNotFoundError as exc:
            raise Http404(str(exc))

        form = ConversionTaskForm(
            initial={
                "filename": task.filename,
                "source_format": task.source_format,
                "target_format": task.target_format,
                "bitrate": task.bitrate,
                "channels": task.channels,
                "status": task.status,
            }
        )

        context = {
            "form": form,
            "task": _task_to_template_dict(task),
            "object": _task_to_template_dict(task),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk: int):
        form = ConversionTaskForm(request.POST)

        if form.is_valid():
            use_case = UpdateTaskUseCase(_get_repository())

            try:
                use_case.execute(task_id=pk, **form.cleaned_data)
                return redirect("task_list")
            except TaskNotFoundError as exc:
                raise Http404(str(exc))
            except TaskValidationError as exc:
                form.add_error(None, str(exc))

        context = {
            "form": form,
            "task": {"pk": pk, "id": pk},
            "object": {"pk": pk, "id": pk},
        }
        return render(request, self.template_name, context)


class TaskDeleteView(View):
    template_name = "converter/task_confirm_delete.html"

    def get(self, request, pk: int):
        use_case = GetTaskUseCase(_get_repository())

        try:
            task = use_case.execute(pk)
        except TaskNotFoundError as exc:
            raise Http404(str(exc))

        task_data = _task_to_template_dict(task)

        context = {
            "task": task_data,
            "object": task_data,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk: int):
        use_case = DeleteTaskUseCase(_get_repository())

        try:
            use_case.execute(pk)
        except TaskNotFoundError as exc:
            raise Http404(str(exc))

        return redirect("task_list")