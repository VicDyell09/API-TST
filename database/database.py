from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:admin@clustertst.siflrzd.mongodb.net/?retryWrites=true&w=majority")
db1 = client.Motor
db2 = client.User
dbmotor = db1["HargaMotor"]
dbuser = db2["DaftarUser"]