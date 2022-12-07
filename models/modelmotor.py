from pydantic import BaseModel

class Motor(BaseModel):
    Tipe_Motor: str 
    Harga: int 
    class Config:
        schema_extra = {
            "HargaMotor" : {
                "Tipe_Motor": "Mio M3 125",
                "Harga": 15550000,
            }
        }