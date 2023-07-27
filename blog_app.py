from fastapi import FastAPI
import uvicorn
from api.routers import users_router, posts_router, ratings_router, link_router


app = FastAPI()
app.include_router(users_router.router)
app.include_router(posts_router.router)
app.include_router(ratings_router.router)
app.include_router(link_router.router)


if __name__ == '__main__':
    uvicorn.run(
        'blog_app:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )