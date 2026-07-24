from fastapi import APIRouter

router = APIRouter(tags=["admin"])


@router.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
