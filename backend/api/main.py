import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import contracts, users, audit
from api.core.config import settings

app = FastAPI(
    title="Smart Contract Intelligence Platform",
    description="AI-powered platform for creating, visualizing, and auditing smart contracts",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contracts.router, prefix="/api/contracts", tags=["contracts"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])

@app.get("/", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": "smart-contract-intelligence-api"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)