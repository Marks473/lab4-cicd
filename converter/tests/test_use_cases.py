from django.test import SimpleTestCase

from converter.application.use_cases import (
    CreateTaskUseCase,
    DeleteTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
    TaskNotFoundError,
    TaskValidationError,
    UpdateTaskUseCase,
)
from converter.domain.entities import ConversionTaskEntity


class FakeConversionTaskRepository:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def list_all(self, filters=None):
        filters = filters or {}
        result = self.tasks[:]

        source_format = filters.get("source_format")
        status = filters.get("status")

        if source_format:
            result = [task for task in result if task.source_format == source_format]

        if status:
            result = [task for task in result if task.status == status]

        return result

    def get_by_id(self, task_id: int):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def create(self, task: ConversionTaskEntity):
        task.id = self.next_id
        self.next_id += 1
        self.tasks.append(task)
        return task

    def update(self, task: ConversionTaskEntity):
        for index, existing_task in enumerate(self.tasks):
            if existing_task.id == task.id:
                self.tasks[index] = task
                return task
        return None

    def delete(self, task_id: int):
        self.tasks = [task for task in self.tasks if task.id != task_id]


class CreateTaskUseCaseTest(SimpleTestCase):
    def setUp(self):
        self.repository = FakeConversionTaskRepository()
        self.use_case = CreateTaskUseCase(self.repository)

    def test_create_task_success(self):
        task = self.use_case.execute(
            filename="song.mp3",
            source_format="mp3",
            target_format="ogg",
            bitrate=192,
            channels=2,
            status="new",
        )

        self.assertEqual(task.id, 1)
        self.assertEqual(task.filename, "song.mp3")
        self.assertEqual(task.source_format, "mp3")
        self.assertEqual(task.target_format, "ogg")
        self.assertEqual(task.bitrate, 192)
        self.assertEqual(task.channels, 2)
        self.assertEqual(task.status, "new")

    def test_create_task_with_default_status(self):
        task = self.use_case.execute(
            filename="track.ogg",
            source_format="ogg",
            target_format="mp3",
            bitrate=256,
            channels=1,
        )

        self.assertEqual(task.status, "new")

    def test_create_task_with_invalid_bitrate_raises_error(self):
        with self.assertRaises(TaskValidationError):
            self.use_case.execute(
                filename="bad.mp3",
                source_format="mp3",
                target_format="ogg",
                bitrate=0,
                channels=2,
                status="new",
            )

    def test_create_task_with_invalid_channels_raises_error(self):
        with self.assertRaises(TaskValidationError):
            self.use_case.execute(
                filename="bad_channels.mp3",
                source_format="mp3",
                target_format="ogg",
                bitrate=192,
                channels=5,
                status="new",
            )

    def test_create_task_with_invalid_format_raises_error(self):
        with self.assertRaises(TaskValidationError):
            self.use_case.execute(
                filename="bad_format.wav",
                source_format="wav",
                target_format="ogg",
                bitrate=192,
                channels=2,
                status="new",
            )


class ListTasksUseCaseTest(SimpleTestCase):
    def setUp(self):
        self.repository = FakeConversionTaskRepository()

        self.repository.create(
            ConversionTaskEntity(
                id=None,
                filename="a.mp3",
                source_format="mp3",
                target_format="ogg",
                bitrate=128,
                channels=2,
                status="new",
                created_at=None,
            )
        )
        self.repository.create(
            ConversionTaskEntity(
                id=None,
                filename="b.ogg",
                source_format="ogg",
                target_format="mp3",
                bitrate=256,
                channels=1,
                status="processing",
                created_at=None,
            )
        )
        self.repository.create(
            ConversionTaskEntity(
                id=None,
                filename="c.mp3",
                source_format="mp3",
                target_format="ogg",
                bitrate=320,
                channels=2,
                status="done",
                created_at=None,
            )
        )

        self.use_case = ListTasksUseCase(self.repository)

    def test_list_all_tasks(self):
        tasks = self.use_case.execute()
        self.assertEqual(len(tasks), 3)

    def test_filter_by_source_format(self):
        tasks = self.use_case.execute(source_format="mp3")
        self.assertEqual(len(tasks), 2)
        self.assertTrue(all(task.source_format == "mp3" for task in tasks))

    def test_filter_by_status(self):
        tasks = self.use_case.execute(status="processing")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].filename, "b.ogg")

    def test_invalid_filter_raises_error(self):
        with self.assertRaises(TaskValidationError):
            self.use_case.execute(source_format="wav")


class GetTaskUseCaseTest(SimpleTestCase):
    def setUp(self):
        self.repository = FakeConversionTaskRepository()
        self.created_task = self.repository.create(
            ConversionTaskEntity(
                id=None,
                filename="get_me.mp3",
                source_format="mp3",
                target_format="ogg",
                bitrate=192,
                channels=2,
                status="new",
                created_at=None,
            )
        )
        self.use_case = GetTaskUseCase(self.repository)

    def test_get_existing_task(self):
        task = self.use_case.execute(self.created_task.id)
        self.assertEqual(task.filename, "get_me.mp3")

    def test_get_nonexistent_task_raises_error(self):
        with self.assertRaises(TaskNotFoundError):
            self.use_case.execute(999)


class UpdateTaskUseCaseTest(SimpleTestCase):
    def setUp(self):
        self.repository = FakeConversionTaskRepository()
        self.created_task = self.repository.create(
            ConversionTaskEntity(
                id=None,
                filename="old.mp3",
                source_format="mp3",
                target_format="ogg",
                bitrate=128,
                channels=2,
                status="new",
                created_at=None,
            )
        )
        self.use_case = UpdateTaskUseCase(self.repository)

    def test_update_task_success(self):
        updated_task = self.use_case.execute(
            task_id=self.created_task.id,
            filename="updated.mp3",
            source_format="mp3",
            target_format="ogg",
            bitrate=320,
            channels=1,
            status="processing",
        )

        self.assertEqual(updated_task.filename, "updated.mp3")
        self.assertEqual(updated_task.bitrate, 320)
        self.assertEqual(updated_task.channels, 1)
        self.assertEqual(updated_task.status, "processing")

    def test_update_nonexistent_task_raises_error(self):
        with self.assertRaises(TaskNotFoundError):
            self.use_case.execute(
                task_id=999,
                filename="updated.mp3",
                source_format="mp3",
                target_format="ogg",
                bitrate=320,
                channels=1,
                status="processing",
            )

    def test_update_with_invalid_data_raises_error(self):
        with self.assertRaises(TaskValidationError):
            self.use_case.execute(
                task_id=self.created_task.id,
                filename="updated.mp3",
                source_format="mp3",
                target_format="ogg",
                bitrate=-10,
                channels=1,
                status="processing",
            )


class DeleteTaskUseCaseTest(SimpleTestCase):
    def setUp(self):
        self.repository = FakeConversionTaskRepository()
        self.created_task = self.repository.create(
            ConversionTaskEntity(
                id=None,
                filename="delete_me.mp3",
                source_format="mp3",
                target_format="ogg",
                bitrate=192,
                channels=2,
                status="new",
                created_at=None,
            )
        )
        self.use_case = DeleteTaskUseCase(self.repository)

    def test_delete_existing_task(self):
        self.use_case.execute(self.created_task.id)
        self.assertIsNone(self.repository.get_by_id(self.created_task.id))

    def test_delete_nonexistent_task_raises_error(self):
        with self.assertRaises(TaskNotFoundError):
            self.use_case.execute(999)