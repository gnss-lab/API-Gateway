from fastapi import FastAPI
from .routers import HelloWorld
from .routers import FileUpload
from .routers.mosgimService import generate_map


app = FastAPI(debug=True)

app.include_router(HelloWorld.router)
app.include_router(FileUpload.router)
app.include_router(generate_map.router)
