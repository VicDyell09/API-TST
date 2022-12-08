from fastapi import HTTPException, Depends, status, APIRouter
from authentication.hashing import Hash
from authentication.jwttoken import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from models.modeluser import User
from database.database import dbuser

app_user = APIRouter()

#menambah user baru ke dalam database (register)
@app_user.post('/register')
def create_user(request:User):
	hashed_pass = Hash.bcrypt(request.password)
	user_object = dict(request)
	user_object["password"] = hashed_pass
	user_id = dbuser.insert_one(user_object)
	return {"User":"created"}

#melakukan login untuk API lain dan akan mengeluarkan token access untuk menyambungkan API nya
@app_user.post('/login')
def login(request:OAuth2PasswordRequestForm = Depends()):
	user = dbuser.find_one({"username":request.username})
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'No user found with this {request.username} username')
	if not Hash.verify(user["password"],request.password):
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Wrong Username or password')
	access_token = create_access_token(data={"sub": user["username"] })
	return {"access_token": access_token, "token_type": "bearer"}