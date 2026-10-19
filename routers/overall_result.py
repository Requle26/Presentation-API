from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_overall_page():
    return {"result" : "this is overall page"}