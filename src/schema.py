from pydantic import BaseModel

class SaleSchema(BaseModel):
    id : str
    lat : float
    long : float
    userId : str
    description : str | None
    price : int
    status : str

    class Config:
        orm_mode = True