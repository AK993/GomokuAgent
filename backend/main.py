from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.api import router



app = FastAPI(
    title="Gomoku Agent API"
)



app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_methods=["*"],

    allow_headers=["*"]

)



app.include_router(
    router
)



@app.get("/")
def root():

    return {

        "message":
        "Gomoku Agent Server"

    }