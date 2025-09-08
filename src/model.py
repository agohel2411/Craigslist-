from sqlalchemy import Column, Integer, String, Float
from src.database import Base

class Sales(Base):
    __tablename__= 'sales'
    sr = Column(Integer, primary_key=True, index=True)
    id = Column(String)
    lat = Column(Float)
    long = Column(Float)
    userId = Column(String)
    description = Column(String, nullable=True)
    price = Column(Integer)
    status = Column(String)