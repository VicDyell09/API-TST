from fastapi import APIRouter, Depends
from database.database import dbmotor
from models.modelmotor import Motor
from models.modeluser import User
from authentication.authentication import get_current_user
from random import random
from routes.connect import *
from enum import Enum

app_motor = APIRouter()

#disclaimer: 
# tipe motor dimulai dengan huruf besar dan harus tepat
# tenor dipilih berdasarkan dropdown
# bunga dalam float per bulan. contoh bunga perbulan 15%, maka masukkan 0.015
# down payment berupa integer. contoh 1000000


#enum class untuk Tenor, yaitu tenor hanya bisa 12 bulan, 18 bulan, 24 bulan, dan 30 bulan (tenor secara umum)
class Tenor(str, Enum):
    dua_belas_bulan = "12"
    delapan_belas_bulan = "18"
    dua_puluh_empat = "24"
    tiga_puluh = "30"

#enum class untuk jenis bbm, dimiliki oleh API sebelah
class bbmModel(str, Enum):
    Pertamax_Turbo = "Pertamax Turbo"
    Pertamax = "Pertamax"
    Pertalite = "Pertalite"

#menambah motor baru ke dalam database
@app_motor.post("/motor")
def insert_motor(new_motor: Motor, current_user:User = Depends(get_current_user)):
    #cek apakah motor sudah ada dalam database atau belum

    jumlah = dbmotor.count_documents({"Tipe_Motor": new_motor.Tipe_Motor})
    if (jumlah != 0):
        return{'message': 'motor sudah ada di dalam database. silakan masukkan tipe motor lain'}

    motor = {'Tipe_Motor': '', 'Harga': ''}
    motor['Tipe_Motor'] = new_motor.Tipe_Motor
    motor['Harga'] = new_motor.Harga


    insert = dbmotor.insert_one(motor)

    return {"motor": "insert success"}

#menghapus motor dari database berdasarkan tipe motor
@app_motor.delete("/motor/delete/{jenis_motor}")
def delete_motor(jenis_motor: str, current_user:User = Depends(get_current_user)):
    # cek ada atau tidak jenis_motor yang dimaksud
    jumlah = dbmotor.count_documents({"Tipe_Motor": jenis_motor})
    if (jumlah == 0):
        return{'message': 'Tipe motor yang Anda masukkan salah. Silakan masukkan tipe motor yang benar'}

    delete = dbmotor.delete_one({"Tipe_Motor": jenis_motor})
    return {"motor": "delete success"}

#mengubah harga motor berdasarkan tipe motor
@app_motor.put("/motor/update/{jenis_motor}")
def update_harga_motor(jenis_motor: str, harga_baru: int, current_user:User = Depends(get_current_user)):
    # cek ada atau tidak jenis_motor yang dimaksud
    jumlah = dbmotor.count_documents({"Tipe_Motor": jenis_motor})
    if (jumlah == 0):
        return{'message': 'Tipe motor yang Anda masukkan salah. Silakan masukkan tipe motor yang benar'}
    
    indicator = {"Tipe_Motor": jenis_motor }
    newvalues = { "$set": { "Harga": harga_baru } }

    dbmotor.update_one(indicator, newvalues)
    return({"motor": "update success"})

#melihat harga dari suatu motor (tidak perlu login alias fitur gratisan)
@app_motor.get("/motor/{jenis_motor}")
def cek_harga(jenis_motor: str):
    # cek ada atau tidak jenis_motor yang dimaksud
    jumlah = dbmotor.count_documents({"Tipe_Motor": jenis_motor})
    if (jumlah == 0):
        return{'message': 'Tipe motor yang Anda masukkan salah. Silakan masukkan tipe motor yang benar'}
    
    motor = dbmotor.find_one({"Tipe_Motor": jenis_motor})

    harga_motor = motor['Harga']
    return harga_motor

#melakukan penghitungan cicilan berdasarkan tipe motor
@app_motor.get("/motor/cicilan/{jenis_motor}")
def hitung_cicilan(jenis_motor: str, bunga: float, tenor: Tenor, down_payment: int, current_user:User = Depends(get_current_user)):
    # cek ada atau tidak jenis_motor yang dimaksud
    jumlah = dbmotor.count_documents({"Tipe_Motor": jenis_motor})
    if (jumlah == 0):
        return{'message': 'Tipe motor yang Anda masukkan salah. Silakan masukkan tipe motor yang benar'}
    
    if tenor is Tenor.dua_belas_bulan:
        tenor = 12
    elif tenor is Tenor.delapan_belas_bulan:
        tenor = 18
    elif tenor is Tenor.dua_puluh_empat:
        tenor = 24
    elif tenor is Tenor.tiga_puluh:
        tenor = 30       

    cicilan = {'cicilan': ''}
    motor = dbmotor.find_one({"Tipe_Motor": jenis_motor})

    harga_motor = motor['Harga']
    hutang = harga_motor - down_payment
    cicilan['cicilan'] = ((hutang * bunga * tenor) + hutang) / tenor #rumus menghitung cicilan per bulan
    return cicilan

#melakukan penghitungan cicilan beserta rekomendasinya
@app_motor.get("/motor/cicilan/rekomendasi/{jenis_motor}")
def hitung_rekomendasi(jenis_motor: str, bunga: float, tenor: Tenor, down_payment: int, budget_per_bulan: int, current_user:User = Depends(get_current_user)):
    # cek ada atau tidak jenis_motor yang dimaksud
    jumlah = dbmotor.count_documents({"Tipe_Motor": jenis_motor})
    if (jumlah == 0):
        return{'message': 'Tipe motor yang Anda masukkan salah. Silakan masukkan tipe motor yang benar'}

    if tenor is Tenor.dua_belas_bulan:
        tenor = 12
    elif tenor is Tenor.delapan_belas_bulan:
        tenor = 18
    elif tenor is Tenor.dua_puluh_empat:
        tenor = 24
    elif tenor is Tenor.tiga_puluh:
        tenor = 30     

    cicilan = {'cicilan': ''}
    motor = {'Tipe_Motor': '', 'Harga': ''}
    motor = dbmotor.find_one({"Tipe_Motor": jenis_motor})

    harga_motor = motor['Harga']
    hutang = harga_motor - down_payment
    cicilan['cicilan'] = ((hutang * bunga * tenor) + hutang) / tenor

    kemampuan = {'kemampuan': ''}
    kemampuan['kemampuan'] = budget_per_bulan - 1000000

    batas_rekomendasi = {'batas_rekomendasi': ''}
    batas_rekomendasi['batas_rekomendasi'] = ((kemampuan['kemampuan']*tenor)/(bunga*tenor+1)) + down_payment - 1000000 #menghitung harga asli motor sesuai kemampuan (budget-1jt) setelah bunga. diakhir dikurang 500ribu lagi untuk menutupi pembulatan
    batas_rekomendasi_bulat = batas_rekomendasi['batas_rekomendasi']//1

    batas_bawah = {'batas_bawah': ''}
    batas_bawah['batas_bawah'] = batas_rekomendasi['batas_rekomendasi']-10000000 #diambil hingga kurang dari 10 juta dari harga yang direkomendasikan

    #mencari nama motor yang sesuai dengan budget
    list_motor =[]
    for x in dbmotor.find({"$and":[{"Harga": {"$lt": batas_rekomendasi['batas_rekomendasi']}}, {"Harga": {"$gt": batas_bawah['batas_bawah']}}]}):
        list_motor.append(x['Tipe_Motor'])

    list_motor_random = []

    #randomize ambil 5 nama motor rekomendasi sesuai budget
    if(len(list_motor)>5):
        for i in range (5):
            loop = True
            while loop==True:
                ketemu = False
                bil = random()
                indeks = bil * len(list_motor) // 1
                indeks = int(indeks)
                nama_motor = list_motor[indeks]
                for j in range (len(list_motor_random)):
                    if nama_motor == list_motor_random[j]:
                        ketemu = True
                if ketemu==False:
                    loop = False   
                    list_motor_random.append(nama_motor)

    #randomize ambil 5 nama motor rekomendasi sesuai budget. kalau tidak sampai 5 yaudah output semua
    rekomendasi_motor = []
    if (len(list_motor)>5):
        for x in range (5):
            rekomendasi_motor.append(list_motor_random[x])
    else:
        for x in range (len(list_motor)):
            rekomendasi_motor.append(list_motor[x])        

    #output
    if (cicilan['cicilan'] <= kemampuan['kemampuan'] and len(list_motor)>0): #spare 1 juta untuk biaya bensin dan kebutuhan motor lainnya
        return{"cicilan sebesar": cicilan['cicilan'], "message": "Anda mampu untuk membeli motor tersebut", "rekomendasi motor sesuai budget": rekomendasi_motor}

    elif (cicilan['cicilan'] > kemampuan['kemampuan'] and cicilan['cicilan'] < budget_per_bulan and len(list_motor)>0):
         return{"cicilan sebesar": cicilan['cicilan'], "message": "Anda mampu untuk membeli motor, tapi sangat mepet dengan budget. Pertimbangkan untuk membeli motor lain yang lebih murah untuk mengantisipasi adanya biaya diluar dugaan", "rekomendasi motor sesuai budget": rekomendasi_motor}

    elif (cicilan['cicilan'] > kemampuan['kemampuan'] and len(list_motor)==0):
        return{"cicilan sebesar": cicilan['cicilan'], "message": "Budget Anda belum cukup untuk membeli motor. Harus lebih semangat untuk mencari uang"}

    else:
        return{"cicilan sebesar": cicilan['cicilan'], "message": "Anda tidak mampu untuk membeli motor tersebut", "rekomendasi cicilan per bulan": kemampuan['kemampuan'] ,"rekomendasi harga motor": batas_rekomendasi_bulat, "rekomendasi motor sesuai budget": rekomendasi_motor}    

#menghitung prediksi total pengeluaran berdasarkan cicilan per bulan dan biaya bensin (gabungan API dengan partner)
@app_motor.get("/motor/cicilan/gabungan/{jenis_motor}")
def hitung_total (jenis_motor: str, jangkauan_km_perhari: float, lokasi: str, jenis_bbm: bbmModel, bunga: float, tenor: Tenor, down_payment: int, current_user:User = Depends(get_current_user)): #fungsi dari API partner
    bensin = get_bensin(jenis_motor, jangkauan_km_perhari, lokasi, jenis_bbm)
    harga_bensin = bensin['harga']
    cicilan = hitung_cicilan(jenis_motor, bunga, tenor, down_payment)
    harga_cicilan = cicilan['cicilan']

    total = harga_bensin + harga_cicilan

    return total

#menghitung prediksi total pengeluaran berdasarkan cicilan per bulan dan biaya bensin beserta rekomendasinya (gabungan API dengan partner)
@app_motor.get("/motor/cicilan/gabungan/rekomendasi/{jenis_motor}")
def hitung_total_beserta_rekomendasi (jenis_motor: str, jangkauan_km_perhari: float, lokasi: str, jenis_bbm: bbmModel, bunga: float, tenor: Tenor, down_payment: int, budget_per_bulan: int, current_user:User = Depends(get_current_user)): 
    total = hitung_total(jenis_motor, jangkauan_km_perhari, lokasi, jenis_bbm, bunga, tenor, down_payment) #fungsi dari API partner
    total = total // 1 #supaya angkanya bulat

    if tenor is Tenor.dua_belas_bulan:
        tenor = 12
    elif tenor is Tenor.delapan_belas_bulan:
        tenor = 18
    elif tenor is Tenor.dua_puluh_empat:
        tenor = 24
    elif tenor is Tenor.tiga_puluh:
        tenor = 30

    kemampuan = {'kemampuan': ''}
    kemampuan['kemampuan'] = budget_per_bulan - 1000000
    kemampuan['kemampuan'] = kemampuan['kemampuan']//1 #supaya bulat

    batas_rekomendasi = {'batas_rekomendasi': ''}
    batas_rekomendasi['batas_rekomendasi'] = ((kemampuan['kemampuan']*tenor)/(bunga*tenor+1)) + down_payment - 1000000 #menghitung harga asli motor sesuai kemampuan (budget-1jt) setelah bunga. diakhir dikurang 500ribu lagi untuk menutupi pembulatan
    batas_rekomendasi_bulat = batas_rekomendasi['batas_rekomendasi']//1

    batas_bawah = {'batas_bawah': ''}
    batas_bawah['batas_bawah'] = batas_rekomendasi['batas_rekomendasi']-10000000 #diambil hingga kurang dari 10 juta dari harga yang direkomendasikan

    #mencari nama motor yang sesuai dengan budget
    list_motor =[]
    for x in dbmotor.find({"$and":[{"Harga": {"$lt": batas_rekomendasi['batas_rekomendasi']}}, {"Harga": {"$gt": batas_bawah['batas_bawah']}}]}):
        list_motor.append(x['Tipe_Motor'])

    list_motor_random = []

    #randomize ambil 5 nama motor rekomendasi sesuai budget
    if(len(list_motor)>5):
        for i in range (5):
            loop = True
            while loop==True:
                ketemu = False
                bil = random()
                indeks = bil * len(list_motor) // 1
                indeks = int(indeks)
                nama_motor = list_motor[indeks]
                for j in range (len(list_motor_random)):
                    if nama_motor == list_motor_random[j]:
                        ketemu = True
                if ketemu==False:
                    loop = False   
                    list_motor_random.append(nama_motor)

    #memasukkan nama motor ke dalam list rekomendasi_motor
    rekomendasi_motor = []
    if (len(list_motor)>5):
        for x in range (5):
            rekomendasi_motor.append(list_motor_random[x])
    else:
        for x in range (len(list_motor)):
            rekomendasi_motor.append(list_motor[x])        


    #output
    if (total <= kemampuan['kemampuan'] and len(list_motor)>0): #spare 1 juta untuk biaya bensin dan kebutuhan motor lainnya
        return{"jumlah prediksi pengeluaran sebesar": total, "message": "Anda mampu untuk membeli motor tersebut", "rekomendasi motor sesuai budget": rekomendasi_motor}

    elif (total > kemampuan['kemampuan'] and total < budget_per_bulan and len(list_motor)>0):
         return{"jumlah prediksi pengeluaran sebesar": total, "message": "Anda mampu untuk membeli motor, tapi sangat mepet dengan budget. Pertimbangkan untuk membeli motor lain yang lebih murah untuk mengantisipasi adanya biaya diluar dugaan", "rekomendasi motor sesuai budget": rekomendasi_motor}

    elif (total > kemampuan['kemampuan'] and len(list_motor)==0):
        return{"jumlah prediksi pengeluaran sebesar": total, "message": "Budget Anda belum cukup untuk membeli motor. Harus lebih semangat untuk mencari uang"}

    else:
        return{"jumlah prediksi pengeluaran sebesar": total, "message": "Anda tidak mampu untuk membeli motor tersebut", "rekomendasi cicilan per bulan": kemampuan['kemampuan'] ,"rekomendasi harga motor": batas_rekomendasi_bulat, "rekomendasi motor sesuai budget": rekomendasi_motor}