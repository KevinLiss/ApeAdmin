"""ApeUI API routes — P0 placeholder."""

from fastapi import APIRouter

router = APIRouter(prefix="/apeui", tags=["ApeUI 官网"])


@router.get("/health")
async def health():
    return {"code": 200, "msg": "success", "data": {"ok": True, "plugin": "apeui"}}
