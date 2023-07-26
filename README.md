Simple RESTful API on FastAPI for a blog application with async SQLAlchemy, alembic, PostgreSQL, Redis

Functionality:

Authentication and registration
Email verification on API emailhunter.co
User can signup and login
User can create and view topics
User can create, edit, delete his own posts and view all posts on different topics
User can like or dislike other users’ posts but not his own
User can edit, delete ratings he has set
Number of likes and dislikes for each post is stored in redis and updated whenever ratings get added, deleted or edited

The application is packaged in docker

Build

Run
docker compose up --build

Documentation
To open API documentation go here: http://127.0.0.1:8000/docs