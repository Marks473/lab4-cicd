from django.test import TestCase

from converter.models import ConversionTask


class ConversionTaskModelTest(TestCase):
    def test_str_method(self):
        task = ConversionTask.objects.create(
            filename="song.mp3",
            source_format="mp3",
            target_format="ogg",
            bitrate=192,
            channels=2,
            status="new",
        )
        self.assertEqual(str(task), "song.mp3 (mp3 -> ogg)")

    def test_default_status_is_new(self):
        task = ConversionTask.objects.create(
            filename="track.ogg",
            source_format="ogg",
            target_format="mp3",
            bitrate=256,
            channels=1,
        )
        self.assertEqual(task.status, "new")

    def test_created_at_is_set_automatically(self):
        task = ConversionTask.objects.create(
            filename="auto_time.mp3",
            source_format="mp3",
            target_format="ogg",
            bitrate=128,
            channels=2,
            status="processing",
        )
        self.assertIsNotNone(task.created_at)