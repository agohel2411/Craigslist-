from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///../data/table.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False})



from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()



from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine, autocimmit=False, autoflush=False)