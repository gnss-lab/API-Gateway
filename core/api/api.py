from fastapi import FastAPI
from .routers import HelloWorld


app = FastAPI(debug=True)

app.include_router(HelloWorld.router)
