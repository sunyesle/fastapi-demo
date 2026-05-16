from pathlib import Path
import uuid

from PIL import Image, ImageOps
from fastapi import UploadFile

from src.config import settings
from src.exceptions import BadRequest


UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_SIZE = settings.MAX_UPLOAD_SIZE


async def save_image(file: UploadFile, folder: str) -> str:
    # 파일명 여부 확인
    if not file.filename:
        raise BadRequest()

    # 확장자 확인
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise BadRequest("Unsupported file format.")

    # 파일 크기 확인
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise BadRequest(f"File size must be less than {MAX_SIZE // 1024 // 1024}MB.")

    # 파일명 생성
    filename = f"{uuid.uuid4().hex}{ext}"

    # 폴더 생성
    folder_path = UPLOAD_DIR / folder
    folder_path.mkdir(exist_ok=True)

    # 파일 저장
    file_path = folder_path / filename
    with open(file_path, "wb") as f:
        f.write(content)

    # 이미지 최적화
    optimize_image(file_path)

    return f"/uploads/{folder}/{filename}"

def optimize_image(file_path: Path, max_width: int = 1200) -> None:
    try:
        with Image.open(file_path) as img:
            img = ImageOps.exif_transpose(img)

            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            img.save(file_path, "JPEG", quality=85, optimize=True)
    except Exception as e:
        print(f"Image optimization error: {e}")

def delete_image(url: str) -> bool:
    if not url.startswith("/uploads/"):
        return False

    file_path = Path(url.replace("/uploads/", str(UPLOAD_DIR) + "/"))
    if file_path.exists():
        file_path.unlink()
        return True
    return False
