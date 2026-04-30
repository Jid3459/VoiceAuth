from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import auth, orders

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Voice Authentication & Product Ordering System",
    description="Intelligent backend with SpeechBrain ECAPA-TDNN voice authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(orders.router)

@app.get("/")
def root():
    return {
        "message": "Voice Authentication & Product Ordering System API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}