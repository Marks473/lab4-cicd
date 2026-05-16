from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from converter.models import ConversionTask


class TaskAPITest(APITestCase):
    def setUp(self):
        self.task = ConversionTask.objects.create(
            filename="api_song.mp3",
            source_format="mp3",
            target_format="ogg",
            bitrate=128,
            channels=2,
            status="done",
        )

    def test_get_task_list(self):
        response = self.client.get(reverse("api_task_list_create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["filename"], "api_song.mp3")

    def test_create_task_api(self):
        data = {
            "filename": "created_api.ogg",
            "source_format": "ogg",
            "target_format": "mp3",
            "bitrate": 192,
            "channels": 1,
            "status": "new",
        }
        response = self.client.post(reverse("api_task_list_create"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConversionTask.objects.count(), 2)
        self.assertEqual(response.data["filename"], "created_api.ogg")

    def test_create_task_api_with_invalid_data(self):
        data = {
            "filename": "bad_api.ogg",
            "source_format": "ogg",
            "target_format": "mp3",
            "bitrate": 0,
            "channels": 1,
            "status": "new",
        }
        response = self.client.post(reverse("api_task_list_create"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_single_task_api(self):
        response = self.client.get(reverse("api_task_detail", args=[self.task.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["filename"], "api_song.mp3")
        self.assertEqual(response.data["status"], "done")

    def test_get_single_task_api_404(self):
        response = self.client.get(reverse("api_task_detail", args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_task_api(self):
        data = {
            "filename": "updated_api.mp3",
            "source_format": "mp3",
            "target_format": "ogg",
            "bitrate": 320,
            "channels": 1,
            "status": "processing",
        }
        response = self.client.put(
            reverse("api_task_detail", args=[self.task.pk]),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.task.refresh_from_db()
        self.assertEqual(self.task.filename, "updated_api.mp3")
        self.assertEqual(self.task.bitrate, 320)
        self.assertEqual(self.task.channels, 1)
        self.assertEqual(self.task.status, "processing")

    def test_patch_task_api(self):
        data = {
            "status": "processing",
            "bitrate": 256,
        }
        response = self.client.patch(
            reverse("api_task_detail", args=[self.task.pk]),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "processing")
        self.assertEqual(self.task.bitrate, 256)
        self.assertEqual(self.task.filename, "api_song.mp3")

    def test_delete_task_api(self):
        response = self.client.delete(reverse("api_task_detail", args=[self.task.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ConversionTask.objects.count(), 0)

    def test_filter_task_list_api_by_source_format(self):
        ConversionTask.objects.create(
            filename="another.ogg",
            source_format="ogg",
            target_format="mp3",
            bitrate=256,
            channels=1,
            status="new",
        )

        response = self.client.get(reverse("api_task_list_create"), {"source_format": "ogg"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["filename"], "another.ogg")

    def test_filter_task_list_api_by_status(self):
        ConversionTask.objects.create(
            filename="processing_song.mp3",
            source_format="mp3",
            target_format="ogg",
            bitrate=192,
            channels=2,
            status="processing",
        )

        response = self.client.get(reverse("api_task_list_create"), {"status": "processing"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["filename"], "processing_song.mp3")