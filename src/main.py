from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.routers import admin_router, orders_router, employees_router, nova_poshta_router, auth_router
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


@asynccontextmanager
async def lifespan(app: FastAPI):
    # redis = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)
    # FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(title="AmazonTikTok App", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(auth_router, tags=["auth"])
app.include_router(admin_router, tags=["admin"])
app.include_router(orders_router, tags=["orders"])
app.include_router(employees_router, prefix="/employees", tags=["employees"])
app.include_router(nova_poshta_router, prefix="/api/np", tags=["nova-poshta"])



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
