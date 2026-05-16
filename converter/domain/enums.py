from enum import Enum

class AudioFormat(str, Enum):
    MP3 = "mp3"
    OGG = "ogg"

class ConversionStatus(str, Enum):
    NEW = "new"
    PROCESSING = "processing"
    DONE = "done"