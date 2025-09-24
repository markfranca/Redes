from fastapi import FastAPI
#from .routers import example_router

app = FastAPI()

#app.include_router

@app.get("/")
async def read_root():
    return {"Hello": "World"}
