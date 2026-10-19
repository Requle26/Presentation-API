from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_slide_page():
    return {"message" : "this is slide feedback page"}