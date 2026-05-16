from django.test import TestCase
from django.urls import reverse

from converter.models import ConversionTask


class TaskViewsTest(TestCase):
    def setUp(self):
        self.task = ConversionTask.objects.create(
            filename="track.ogg",
            source_format="ogg",
            target_format="mp3",
            bitrate=256,
            channels=1,
            status="processing",
        )

    def test_task_list_view_status_code(self):
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 200)

    def test_task_list_view_contains_task(self):
        response = self.client.get(reverse("task_list"))
        self.assertContains(response, "track.ogg")
        self.assertContains(response, "processing")

    def test_task_detail_view_status_code(self):
        response = self.client.get(reverse("task_detail", args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)

    def test_task_detail_view_contains_task_data(self):
        response = self.client.get(reverse("task_detail", args=[self.task.pk]))
        self.assertContains(response, "track.ogg")
        self.assertContains(response, "ogg")
        self.assertContains(response, "mp3")
        self.assertContains(response, "256")
        self.assertContains(response, "processing")

    def test_task_create_view_get(self):
        response = self.client.get(reverse("task_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Форма задачи")

    def test_task_create_view_post(self):
        response = self.client.post(
            reverse("task_create"),
            {
                "filename": "new_song.mp3",
                "source_format": "mp3",
                "target_format": "ogg",
                "bitrate": 320,
                "channels": 2,
                "status": "new",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task_list"))
        self.assertEqual(ConversionTask.objects.count(), 2)

        created_task = ConversionTask.objects.get(filename="new_song.mp3")
        self.assertEqual(created_task.target_format, "ogg")
        self.assertEqual(created_task.bitrate, 320)

    def test_task_create_view_invalid_post(self):
        response = self.client.post(
            reverse("task_create"),
            {
                "filename": "",
                "source_format": "mp3",
                "target_format": "ogg",
                "bitrate": 320,
                "channels": 2,
                "status": "new",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConversionTask.objects.count(), 1)

    def test_task_update_view_get(self):
        response = self.client.get(reverse("task_update", args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "track.ogg")

    def test_task_update_view_post(self):
        response = self.client.post(
            reverse("task_update", args=[self.task.pk]),
            {
                "filename": "updated_track.ogg",
                "source_format": "ogg",
                "target_format": "mp3",
                "bitrate": 320,
                "channels": 2,
                "status": "done",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task_list"))

        self.task.refresh_from_db()
        self.assertEqual(self.task.filename, "updated_track.ogg")
        self.assertEqual(self.task.bitrate, 320)
        self.assertEqual(self.task.channels, 2)
        self.assertEqual(self.task.status, "done")

    def test_task_delete_view_get(self):
        response = self.client.get(reverse("task_delete", args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Удаление задачи")

    def test_task_delete_view_post(self):
        response = self.client.post(reverse("task_delete", args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task_list"))
        self.assertEqual(ConversionTask.objects.count(), 0)

    def test_task_list_filter_by_source_format(self):
        ConversionTask.objects.create(
            filename="song2.mp3",
            source_format="mp3",
            target_format="ogg",
            bitrate=192,
            channels=2,
            status="new",
        )

        response = self.client.get(reverse("task_list"), {"source_format": "mp3"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "song2.mp3")
        self.assertNotContains(response, "track.ogg")

    def test_task_list_filter_by_status(self):
        ConversionTask.objects.create(
            filename="song_done.mp3",
            source_format="mp3",
            target_format="ogg",
            bitrate=192,
            channels=2,
            status="done",
        )

        response = self.client.get(reverse("task_list"), {"status": "done"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "song_done.mp3")
        self.assertNotContains(response, "track.ogg")