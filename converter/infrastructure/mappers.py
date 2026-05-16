from converter.domain.entities import ConversionTaskEntity
from converter.models import ConversionTask


def to_entity(model: ConversionTask) -> ConversionTaskEntity:
    return ConversionTaskEntity(
        id=model.id,
        filename=model.filename,
        source_format=model.source_format,
        target_format=model.target_format,
        bitrate=model.bitrate,
        channels=model.channels,
        status=model.status,
        created_at=model.created_at,
    )


def to_model_data(entity: ConversionTaskEntity) -> dict:
    return {
        "filename": entity.filename,
        "source_format": entity.source_format,
        "target_format": entity.target_format,
        "bitrate": entity.bitrate,
        "channels": entity.channels,
        "status": entity.status,
    }