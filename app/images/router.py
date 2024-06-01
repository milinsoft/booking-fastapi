from shutil import copyfileobj

from fastapi import APIRouter, UploadFile, status

from app.tasks.tasks import process_pic

router = APIRouter(prefix="/images", tags=["Images UPLOAD"])


@router.post("/hotels", status_code=status.HTTP_201_CREATED)
async def add_hotel_image(filename: str, fileuploader: UploadFile) -> str:
    img_path = f"app/static/images/{filename}.webp"
    with open(img_path, "wb+") as f:
        copyfileobj(fileuploader.file, f)
    process_pic.delay(img_path)
    return "Your picture be uploaded in background!"
