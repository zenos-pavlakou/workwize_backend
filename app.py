from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from routes.ai import router as ai_router
from routes.system import router as system_router




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://radbytes.org:5000", 
        "http://localhost:8080", 
        "http://localhost:8081", 
        "http://206.189.114.61:5000",
        "https://radbytes.org",
        "https://radbytes.org:443",
        "https://www.radbytes.org",
        "https://www.radbytes.org:443",
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)
app.include_router(system_router)

    



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


