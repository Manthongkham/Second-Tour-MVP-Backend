from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes.route import router

app = FastAPI()
app.include_router(router)  

origins = [
    "http://localhost:5173",
    "https://second-tour-mvp-frontend.vercel.app/",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}