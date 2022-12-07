from fastapi import APIRouter
from database.database import dbmotor, dbuser
from models.modelmotor import Motor
from models.modeluser import User
from schemas.schema import motor_serializer, motors_serializer
from fastapi import FastAPI, HTTPException, Depends, Request,status
from authentication.hashing import Hash
from authentication.jwttoken import create_access_token
from authentication.authentication import get_current_user

app_motor = APIRouter()

@app_motor.get("/motor")
def tes_autentikasi(current_user:User = Depends(get_current_user)):
	return {"data": "Hello World! Authentication Success"}

@app_motor.get("/motor/{jenis_motor}")
def cek_harga(jenis_motor: str):
    motor = dbmotor.find_one({"Tipe Motor": jenis_motor})
    harga_motor = motor['Harga']
    return harga_motor

@app_motor.get("/motor/cicilan/{jenis_motor}")
def hitung_cicilan(jenis_motor: str, bunga: float, tenor: int, down_payment: int):
    cicilan = {'cicilan': ''}
    motor = dbmotor.find_one({"Tipe Motor": jenis_motor})
    harga_motor = motor['Harga']
    hutang = harga_motor - down_payment
    cicilan['cicilan'] = ((hutang * bunga * tenor) + hutang) / tenor
    return cicilan

@app_motor.get("/motor/cicilan/rekomendasi/{jenis_motor}")
def hitung_rekomendasi(jenis_motor: str, bunga: float, tenor: int, down_payment: int, budget_per_bulan: int):
    cicilan = {'cicilan': ''}
    motor = dbmotor.find_one({"Tipe Motor": jenis_motor})
    harga_motor = motor['Harga']
    hutang = harga_motor - down_payment
    cicilan['cicilan'] = ((hutang * bunga * tenor) + hutang) / tenor

    kemampuan = {'kemampuan': ''}
    kemampuan['kemampuan'] = budget_per_bulan - 1000000

    batas_rekomendasi = {'batas_rekomendasi': ''}
    batas_rekomendasi['batas_rekomendasi'] = ((kemampuan['kemampuan']*tenor)/(bunga*tenor+1)) + down_payment
    batas_rekomendasi_bulat = batas_rekomendasi['batas_rekomendasi']//1

    batas_bawah = {'batas_bawah': ''}
    batas_bawah['batas_bawah'] = batas_rekomendasi['batas_rekomendasi']-10000000 #diambil hingga kurang dari 10 juta dari harga yang direkomendasikan

    # motor_sesuai_budget = dbmotor.find({"$and":[{"Harga": {"$lt": batas_rekomendasi}}, {"Harga": {"gt": batas_bawah}}]})
    # motor_sesuai_budget = dbmotor.find({"Harga": {"$lt": batas_rekomendasi}})
    list_motor =[]
    for x in dbmotor.find({"$and":[{"Harga": {"$lt": batas_rekomendasi['batas_rekomendasi']}}, {"Harga": {"$gt": batas_bawah['batas_bawah']}}]}).limit(5):
        list_motor.append(x['Tipe Motor'])

    if (cicilan['cicilan'] <= kemampuan['kemampuan'] and len(list_motor)>0): #spare 1 juta untuk biaya bensin dan kebutuhan motor lainnya
        return{"cicilan sebesar": cicilan['cicilan'], "message": "Anda mampu untuk membeli motor tersebut", "rekomendasi motor sesuai budget": list_motor}

    elif (cicilan['cicilan'] > kemampuan['kemampuan'] and cicilan['cicilan'] < budget_per_bulan and len(list_motor)>0):
         return{"cicilan sebesar": cicilan['cicilan'], "message": "Anda mampu untuk membeli motor, tapi sangat mepet dengan budget. Pertimbangkan untuk membeli motor lain yang lebih murah untuk mengantisipasi adanya biaya diluar dugaan", "rekomendasi motor sesuai budget": list_motor}

    elif (cicilan['cicilan'] > kemampuan['kemampuan'] and len(list_motor)==0):
        return{"cicilan sebesar": cicilan['cicilan'], "message": "Budget Anda belum cukup untuk membeli motor. Harus lebih semangat untuk mencari uang"}

    else:
        return{"cicilan sebesar": cicilan['cicilan'], "message": "Anda tidak mampu untuk membeli motor tersebut", "rekomendasi cicilan per bulan": kemampuan['kemampuan'] ,"rekomendasi harga motor": batas_rekomendasi_bulat, "rekomendasi motor sesuai budget": list_motor}    