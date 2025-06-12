from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from .database import Base


class FetchedData(Base):
    __tablename__ = "fetched_data"

    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False) 