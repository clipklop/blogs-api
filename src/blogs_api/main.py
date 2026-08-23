from typing import Annotated

from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import status, Depends

import uvicorn
from fastapi import FastAPI

from blogs_api.database import get_db
from blogs_api.routers import (
    post,
    user,
)

app = FastAPI(title="Blogs API")

DbSession = Annotated[Session, Depends(get_db)]

@app.get("/")
def read_db_health(db: Session = Depends(get_db)):
    """Check the health of the database."""
    try:
        # Perform a simple query to check database connectivity
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

app.include_router(post.router)
app.include_router(user.router)


def main():
    uvicorn.run("blogs_api.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
