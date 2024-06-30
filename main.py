from fastapi import FastAPI
from users import routers as users_routers
from posts import routers as posts_routers

app = FastAPI()

app.include_router(users_routers.router)
app.include_router(posts_routers.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
