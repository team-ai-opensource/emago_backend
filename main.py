from fastapi import FastAPI
from routes.gpt import gpt_touter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(gpt_touter)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "홈"

