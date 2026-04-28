from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import users, simulation, results, sync, market

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"VALIDATION ERROR: {exc.errors()}")
    print(f"BODY: {exc.body}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(simulation.router, prefix=settings.API_V1_STR, tags=["simulation"])
app.include_router(results.router, prefix=settings.API_V1_STR, tags=["results"])
app.include_router(sync.router, prefix=settings.API_V1_STR, tags=["sync"])
app.include_router(market.router, prefix=settings.API_V1_STR, tags=["market"])

@app.get("/")
def root():
    return {"message": "Welcome to the Personal Financial Digital Twin API"}
