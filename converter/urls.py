from django.urls import path

from converter.presentation.views_api import (
    TaskListCreateAPIView,
    TaskRetrieveUpdateDeleteAPIView,
)
from converter.presentation.views_html import (
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
)

urlpatterns = [
    path("", TaskListView.as_view(), name="task_list"),
    path("task/<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("task/create/", TaskCreateView.as_view(), name="task_create"),
    path("task/<int:pk>/update/", TaskUpdateView.as_view(), name="task_update"),
    path("task/<int:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),

    path("api/tasks/", TaskListCreateAPIView.as_view(), name="api_task_list_create"),
    path("api/tasks/<int:pk>/", TaskRetrieveUpdateDeleteAPIView.as_view(), name="api_task_detail"),
]