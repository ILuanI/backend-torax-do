from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings


class FileStorage:
    def __init__(self, base_dir: str = settings.upload_dir) -> None:
        self.base_dir = Path(base_dir)
        self.originals_dir = self.base_dir / "radiografias_originales"
        self.processed_dir = self.base_dir / "radiografias_procesadas"
        self.reports_dir = self.base_dir / "reportes_pdf"
        self.ensure_directories()

    def ensure_directories(self) -> None:
        for directory in (self.originals_dir, self.processed_dir, self.reports_dir):
            directory.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> Path:
        suffix = Path(file.filename or "").suffix.lower() or ".png"
        target = self.originals_dir / f"{uuid4().hex}{suffix}"
        content = await file.read()
        target.write_bytes(content)
        return target

    def processed_image_path(self) -> Path:
        return self.processed_dir / f"{uuid4().hex}.png"

    def report_path(self) -> Path:
        return self.reports_dir / f"{uuid4().hex}.pdf"


file_storage = FileStorage()
