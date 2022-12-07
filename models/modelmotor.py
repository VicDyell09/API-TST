from pydantic import BaseModel, Field

class Motor(BaseModel):
    Tipe_Motor: str = Field(default=None)
    Harga: int = Field(default=None)
    class Config:
        schema_extra = {
            "HargaMotor" : {
                "Tipe_Motor": "Mio M3 125",
                "Harga": 15550000,
            }
        }