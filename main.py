from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
from .models import Base
from .database import engine
from .routers.auth import router as auth_router #relative import sunucu için
from .routers.todo import router as todo_router
import os

app = FastAPI()

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")

app.include_router(auth_router)
app.include_router(todo_router)

app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")

@app.get("/")
def read_root(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTTP_302_FOUND)

Base.metadata.create_all(bind=engine)