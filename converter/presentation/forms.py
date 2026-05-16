from django import forms


FORMAT_CHOICES = [
    ("mp3", "MP3"),
    ("ogg", "OGG"),
]

STATUS_CHOICES = [
    ("new", "New"),
    ("processing", "Processing"),
    ("done", "Done"),
]

CHANNEL_CHOICES = [
    (1, "1"),
    (2, "2"),
]


class ConversionTaskForm(forms.Form):
    filename = forms.CharField(
        max_length=255,
        label="Имя файла",
    )
    source_format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        label="Исходный формат",
    )
    target_format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        label="Целевой формат",
    )
    bitrate = forms.IntegerField(
        min_value=1,
        label="Битрейт (kbps)",
    )
    channels = forms.TypedChoiceField(
        choices=CHANNEL_CHOICES,
        coerce=int,
        label="Число каналов",
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        initial="new",
        label="Статус",
    )