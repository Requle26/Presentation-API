from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import (
    auth,
    input,
    overall_result,
    slide_detail_feedback,
)


@app.get("/")
def get_root():
    return {"message" : "API is running!"}

app.include_router(auth.router, prefix="/auth",)
app.include_router(input.router, prefix="/file_input",)
app.include_router(overall_result.router, prefix="/result",)
app.include_router(slide_detail_feedback.router, prefix="/slide",)
