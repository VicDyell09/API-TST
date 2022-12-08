import uvicorn
from fastapi import FastAPI
from routes.motor import app_motor
from routes.user import app_user

app = FastAPI()
app.include_router(app_motor)
app.include_router(app_user)

@app.get("/", tags=["Root"])
async def welcome():
	return {"Selamat datang di MotorVic, silakan login untuk dapat mengakses API ini"}
    
if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
