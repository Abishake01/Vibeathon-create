from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, projects, ai

# Create database tables
# Drop and recreate to handle schema changes
try:
    Base.metadata.drop_all(bind=engine)
except:
    pass
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Web Builder API",
    description="Backend API for creating and managing HTML/CSS/JS projects",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(ai.router)


@app.get("/")
async def root():
    return {
        "message": "Web Builder API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

