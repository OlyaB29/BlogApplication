from fastapi import APIRouter
from urllib.parse import quote


router = APIRouter()


@router.get("/encode_link")
async def encode_link(link: str) -> str:
    encoded_link = quote(link, safe='/')
    return encoded_link
