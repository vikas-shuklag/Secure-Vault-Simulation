from fastapi import Depends
from sqlalchemy.orm import Session

# Real DB session generator will be added in DB migration phase
def get_db():
    yield None

# This allows routers to seamlessly require DB access without tight coupling
DbSession = Depends(get_db)
