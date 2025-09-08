from pydantic import BaseModel

class SaleSchema(BaseModel):
    sr: int
    id : str
    lat : float
    long : float
    userId : str
    description : str | None
    price : int
    status : str

    class Config:
        rom_attributes = True