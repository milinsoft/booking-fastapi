from shutil import copyfileobj

from fastapi import APIRouter, UploadFile, status

router = APIRouter(prefix="/images", tags=["Images UPLOAD"])


@router.post("/hotels", status_code=status.HTTP_201_CREATED)
async def add_hotel_image(filename: str, fileuploader: UploadFile) -> str:
    with open(f"static/images/{filename}.webp", "wb+") as f:
        copyfileobj(fileuploader.file, f)
    return "Upload Successful"
