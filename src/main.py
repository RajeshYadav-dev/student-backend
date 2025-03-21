import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routers.student_routers import student_router
from contextlib import asynccontextmanager
from src.database.student_database import init_database
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def life_span(app: FastAPI):
    print("🚀 Server Started..")
    init_database()  # ✅ Ensure DB initializes
    yield
    print("🛑 Server Stopped..")

version = "v1"
app = FastAPI(
    version=version,
    lifespan=life_span,
    title="Student API",
    description="API for Students",
    contact={
        "name": "Rajesh Yadav",
        "url": "https://github.com/RajeshYadav-dev",
        "email": "rajeshyadav0565@gmail.com"
    }
)

origins = [
    "https://studentfrontend-psi.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",  # ✅ Local Testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# ✅ Fix for Render’s dynamic PORT
PORT = int(os.getenv("PORT", 8000))

# ✅ Debugging route to check if server is running
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ✅ Ensure correct API route prefix
app.include_router(student_router, prefix=f"/api/{version}/students", tags=["student"])

# ✅ Serve static files (if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Run app correctly for Render deployment
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=PORT, reload=True)
