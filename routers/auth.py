from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_auth_page():
    return {"message" : "this is auth page"}