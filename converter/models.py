from django.db import models


class ConversionTask(models.Model):
    FORMAT_CHOICES = [
        ("mp3", "MP3"),
        ("ogg", "OGG"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("processing", "Processing"),
        ("done", "Done"),
    ]

    filename = models.CharField(max_length=255, verbose_name="Имя файла")
    source_format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        verbose_name="Исходный формат",
    )
    target_format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        verbose_name="Целевой формат",
    )
    bitrate = models.PositiveIntegerField(verbose_name="Битрейт (kbps)")
    channels = models.PositiveIntegerField(verbose_name="Число каналов")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.filename} ({self.source_format} -> {self.target_format})"